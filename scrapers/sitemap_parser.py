"""
sitemap_parser.py

Stage 1 pilot utility for BMPPD.

Responsibilities:
1. Discover sitemap URL from robots.txt.
2. Fall back to common sitemap locations if the declared sitemap fails.
3. Parse both <urlset> and <sitemapindex>.
4. Recursively collect page URLs.
5. Filter URLs that look like plant/compound detail pages.
6. Cache successfully fetched resources locally.

Usage from project root:

    python scrapers/sitemap_parser.py

Or import functions from bmppd_scraper.py.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from xml.etree import ElementTree as ET

import requests


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = "https://bmppd.org"

CONTACT_EMAIL = "nh694225@gmail.com"

USER_AGENT = (
    "BMPPD-Thesis-Scraper/0.1 "
    "(Nahid; undergraduate research; "
    f"contact: {CONTACT_EMAIL})"
)

DEFAULT_CACHE_DIR = (
    Path(__file__).resolve().parent.parent / "scrapers" / "cache"
)

REQUEST_DELAY_SECONDS = 1.5
REQUEST_TIMEOUT_SECONDS = 30

# Common sitemap locations.
SITEMAP_CANDIDATES = [
    "/sitemap.xml",
    "/sitemap_index.xml",
    "/sitemap-index.xml",
    "/sitemapindex.xml",
]


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logger = logging.getLogger("bmppd_sitemap")


def configure_logging() -> None:
    """Configure simple console logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

def cache_filename(url: str, suffix: str) -> str:
    """
    Create a deterministic cache filename from a URL.

    Example:
        https://bmppd.org/sitemap.xml
        -> abc123... .xml
    """
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return f"{digest[:24]}{suffix}"


def get_cache_path(
    url: str,
    cache_dir: Path,
    suffix: str,
) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / cache_filename(url, suffix)


def load_cached_text(
    url: str,
    cache_dir: Path,
    suffix: str,
) -> str | None:
    """Return cached text if it exists."""
    path = get_cache_path(url, cache_dir, suffix)

    if not path.exists():
        return None

    logger.info("CACHE HIT: %s", url)
    return path.read_text(encoding="utf-8", errors="replace")


def save_cached_text(
    url: str,
    text: str,
    cache_dir: Path,
    suffix: str,
) -> Path:
    """Save text to deterministic cache path."""
    path = get_cache_path(url, cache_dir, suffix)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

    logger.info("CACHED: %s -> %s", url, path)
    return path


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

_last_request_time = 0.0


def polite_sleep() -> None:
    """
    Ensure at least REQUEST_DELAY_SECONDS between network requests.
    """
    global _last_request_time

    elapsed = time.monotonic() - _last_request_time

    if elapsed < REQUEST_DELAY_SECONDS:
        time.sleep(REQUEST_DELAY_SECONDS - elapsed)


def fetch_text(
    url: str,
    *,
    session: requests.Session,
    cache_dir: Path,
    suffix: str,
    allow_cache: bool = True,
) -> tuple[str | None, int | None]:
    """
    Fetch a text resource with local caching.

    Returns:
        (text, HTTP status)
    """
    if allow_cache:
        cached = load_cached_text(
            url,
            cache_dir,
            suffix,
        )

        if cached is not None:
            return cached, 200

    polite_sleep()

    logger.info("FETCH: %s", url)

    try:
        response = session.get(
            url,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

        global _last_request_time
        _last_request_time = time.monotonic()

    except requests.RequestException as exc:
        logger.error("REQUEST FAILED: %s | %s", url, exc)
        return None, None

    logger.info(
        "HTTP %s: %s",
        response.status_code,
        url,
    )

    # Cache successful responses only.
    # We don't cache 404/500 responses because a future run should be
    # able to retry those resources.
    if response.ok:
        save_cached_text(
            url,
            response.text,
            cache_dir,
            suffix,
        )

    return response.text if response.ok else None, response.status_code


# ---------------------------------------------------------------------------
# robots.txt
# ---------------------------------------------------------------------------

def fetch_robots(
    base_url: str,
    *,
    session: requests.Session,
    cache_dir: Path,
) -> str | None:
    """Download robots.txt with caching."""

    robots_url = f"{base_url.rstrip('/')}/robots.txt"

    return fetch_text(
        robots_url,
        session=session,
        cache_dir=cache_dir,
        suffix=".txt",
    )[0]


def build_robot_parser(
    base_url: str,
    robots_text: str,
) -> RobotFileParser:
    """
    Build urllib's RobotFileParser from already-downloaded text.

    This avoids making an extra HTTP request.
    """
    robots_url = f"{base_url.rstrip('/')}/robots.txt"

    parser = RobotFileParser()
    parser.set_url(robots_url)
    parser.parse(robots_text.splitlines())

    return parser


# ---------------------------------------------------------------------------
# Sitemap discovery
# ---------------------------------------------------------------------------

def extract_sitemap_directives(
    robots_text: str,
) -> list[str]:
    """
    Extract Sitemap: directives from robots.txt.
    """
    sitemap_urls: list[str] = []

    for line in robots_text.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.lower().startswith("sitemap:"):
            value = line.split(":", 1)[1].strip()

            if value:
                sitemap_urls.append(value)

    return sitemap_urls


def discover_sitemaps(
    base_url: str,
    *,
    session: requests.Session,
    cache_dir: Path,
) -> tuple[list[str], RobotFileParser]:
    """
    Discover sitemap URLs.

    Priority:
        1. Sitemap directives in robots.txt
        2. Common sitemap locations on the base domain
    """

    robots_text = fetch_robots(
        base_url,
        session=session,
        cache_dir=cache_dir,
    )

    if robots_text is None:
        raise RuntimeError(
            f"Could not fetch robots.txt from {base_url}"
        )

    robot_parser = build_robot_parser(
        base_url,
        robots_text,
    )

    discovered: list[str] = []

    # First use the site's declared sitemap(s).
    for url in extract_sitemap_directives(robots_text):
        if url not in discovered:
            discovered.append(url)

    # Add fallback candidates.
    for path in SITEMAP_CANDIDATES:
        url = f"{base_url.rstrip('/')}{path}"

        if url not in discovered:
            discovered.append(url)

    logger.info(
        "Sitemap candidates discovered: %d",
        len(discovered),
    )

    return discovered, robot_parser


# ---------------------------------------------------------------------------
# XML helpers
# ---------------------------------------------------------------------------

def local_name(tag: str) -> str:
    """
    Convert namespaced XML tags into their local name.

    Example:
        {http://www.sitemaps.org/schemas/sitemap/0.9}urlset
        -> urlset
    """
    return tag.rsplit("}", 1)[-1]


def parse_sitemap_xml(xml_text: str) -> tuple[str, list[str]]:
    """
    Parse one sitemap.

    Returns:
        ("urlset", [page URLs])

    or:

        ("sitemapindex", [child sitemap URLs])
    """

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise ValueError(
            f"Invalid sitemap XML: {exc}"
        ) from exc

    root_type = local_name(root.tag)

    urls: list[str] = []

    for element in root.iter():
        tag = local_name(element.tag)

        if tag != "loc":
            continue

        if element.text:
            value = element.text.strip()

            if value:
                urls.append(value)

    if root_type not in {"urlset", "sitemapindex"}:
        raise ValueError(
            f"Unknown sitemap root element: {root_type}"
        )

    return root_type, urls


# ---------------------------------------------------------------------------
# Recursive sitemap collection
# ---------------------------------------------------------------------------

def collect_urls_from_sitemap(
    sitemap_url: str,
    *,
    session: requests.Session,
    cache_dir: Path,
    robot_parser: RobotFileParser,
    visited_sitemaps: set[str] | None = None,
) -> list[str]:
    """
    Recursively collect page URLs from a sitemap or sitemap index.
    """

    if visited_sitemaps is None:
        visited_sitemaps = set()

    if sitemap_url in visited_sitemaps:
        return []

    visited_sitemaps.add(sitemap_url)

    # Respect robots.txt before fetching the sitemap.
    if not robot_parser.can_fetch(
        USER_AGENT,
        sitemap_url,
    ):
        logger.warning(
            "ROBOTS BLOCKED SITEMAP: %s",
            sitemap_url,
        )
        return []

    xml_text, status = fetch_text(
        sitemap_url,
        session=session,
        cache_dir=cache_dir,
        suffix=".xml",
    )

    if xml_text is None:
        logger.warning(
            "Could not retrieve sitemap: %s | status=%s",
            sitemap_url,
            status,
        )
        return []

    try:
        sitemap_type, locs = parse_sitemap_xml(
            xml_text
        )
    except ValueError as exc:
        logger.error(
            "SITEMAP PARSE ERROR: %s | %s",
            sitemap_url,
            exc,
        )
        return []

    logger.info(
        "Parsed %s: type=%s entries=%d",
        sitemap_url,
        sitemap_type,
        len(locs),
    )

    # Flat sitemap.
    if sitemap_type == "urlset":
        return locs

    # Sitemap index.
    collected: list[str] = []

    for child_sitemap in locs:
        collected.extend(
            collect_urls_from_sitemap(
                child_sitemap,
                session=session,
                cache_dir=cache_dir,
                robot_parser=robot_parser,
                visited_sitemaps=visited_sitemaps,
            )
        )

    return collected


# ---------------------------------------------------------------------------
# URL filtering
# ---------------------------------------------------------------------------

EXCLUDED_PATH_PARTS = {
    "/admin/",
    "/login",
    "/register",
    "/search",
    "/about",
    "/contact",
    "/feedback",
    "/robots.txt",
    "/sitemap",
}

DETAIL_PATH_HINTS = {
    "plant",
    "plants",
    "phytochemical",
    "phytochemicals",
    "compound",
    "compounds",
    "species",
    "detail",
    "details",
}


def looks_like_detail_url(url: str) -> bool:
    """
    Heuristic filter for plant/compound detail URLs.

    This intentionally does NOT assume one exact BMPPD route.
    """

    parsed = urlparse(url)

    path = parsed.path.lower()

    # Only consider HTTP(S).
    if parsed.scheme not in {"http", "https"}:
        return False

    # Skip explicitly excluded routes.
    if any(
        excluded in path
        for excluded in EXCLUDED_PATH_PARTS
    ):
        return False

    # Check useful route hints.
    path_parts = {
        part
        for part in re.split(r"[/_-]+", path)
        if part
    }

    return bool(
        path_parts.intersection(DETAIL_PATH_HINTS)
    )


def filter_detail_urls(
    urls: Iterable[str],
) -> list[str]:
    """Return unique URLs that look like detail pages."""

    seen: set[str] = set()
    results: list[str] = []

    for url in urls:
        normalized = url.rstrip("/")

        if normalized in seen:
            continue

        seen.add(normalized)

        if looks_like_detail_url(normalized):
            results.append(normalized)

    return results


# ---------------------------------------------------------------------------
# Plant URL search
# ---------------------------------------------------------------------------

def find_plant_candidates(
    urls: Iterable[str],
    keyword: str,
) -> list[str]:
    """
    Find URLs whose path contains the supplied keyword.

    Examples:
        keyword="azadirachta"
        keyword="neem"
        keyword="azadirachta-indica"
    """

    keyword = keyword.strip().lower()

    if not keyword:
        return []

    normalized_keyword = re.sub(
        r"[^a-z0-9]+",
        "-",
        keyword,
    )

    results = []

    for url in urls:
        path = urlparse(url).path.lower()

        if (
            keyword in path
            or normalized_keyword in path
            or normalized_keyword.replace("-", "") in path.replace("-", "")
        ):
            results.append(url)

    return results


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

def main() -> None:
    configure_logging()

    cache_dir = DEFAULT_CACHE_DIR

    session = requests.Session()

    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,*/*;q=0.8"
            ),
        }
    )

    sitemap_candidates, robot_parser = discover_sitemaps(
        BASE_URL,
        session=session,
        cache_dir=cache_dir,
    )

    all_page_urls: list[str] = []

    for sitemap_url in sitemap_candidates:
        urls = collect_urls_from_sitemap(
            sitemap_url,
            session=session,
            cache_dir=cache_dir,
            robot_parser=robot_parser,
        )

        if urls:
            logger.info(
                "Working sitemap found: %s",
                sitemap_url,
            )

            all_page_urls.extend(urls)

            # For Stage 1, stop after the first working sitemap.
            break

    all_page_urls = sorted(set(all_page_urls))

    if not all_page_urls:
        logger.error(
            "No page URLs were collected."
        )
        return

    detail_urls = filter_detail_urls(
        all_page_urls
    )

    logger.info(
        "Total sitemap URLs: %d",
        len(all_page_urls),
    )

    print("\n--- ALL SITEMAP URLS ---")

    for index, url in enumerate(all_page_urls, start=1):
        print(f"[{index}] {url}")

    logger.info(
        "Potential plant/compound detail URLs: %d",
        len(detail_urls),
    )

    output_path = (
        Path(__file__).resolve().parent /
        "bmppd_detail_urls.txt"
    )

    output_path.write_text(
        "\n".join(detail_urls),
        encoding="utf-8",
    )

    logger.info(
        "Saved candidate URLs to: %s",
        output_path,
    )

    print("\n--- FILTERED DETAIL URLS ---")

    if detail_urls:
        for index, url in enumerate(detail_urls, start=1):
            print(f"[{index}] {url}")
    else:
        print("None")

    print("\n--- Summary ---")
    print(f"Total sitemap URLs:       {len(all_page_urls)}")
    print(f"Potential detail URLs:    {len(detail_urls)}")


if __name__ == "__main__":
    main()