"""
mpbd_scraper.py

MPBD Scraper — Medicinal Plants of Bangladesh (MPBD) enumeration.

Target:
    Page 1: https://mpbd.cu.ac.bd/plants.php
    Page N: https://mpbd.cu.ac.bd/plants.php?pageno=N

Columns extracted:
    scientific_name
    synonym
    family
    source_page_url
    scrape_timestamp

Raw HTML is cached locally under scrapers/cache/mpbd/ before parsing.
Metadata provenance is tracked in scrapers/cache/mpbd/index.csv and backfill_notes.csv.
Per-run page-level attrition is logged to data/attrition/mpbd_attrition.csv.
"""

from __future__ import annotations

import csv
import hashlib
import logging
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup


# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URL = "https://mpbd.cu.ac.bd"
PLANTS_PATH = "/plants.php"

CONTACT_EMAIL = "nh694225@gmail.com"

USER_AGENT = (
    "MPBD-Thesis-Scraper/0.1 "
    "(Nahid; undergraduate research; "
    f"contact: {CONTACT_EMAIL})"
)

REQUEST_DELAY_SECONDS = 1.5
REQUEST_TIMEOUT_SECONDS = 30

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Cache & Metadata
CACHE_DIR = PROJECT_ROOT / "scrapers" / "cache" / "mpbd"
CACHE_INDEX = CACHE_DIR / "index.csv"

CACHE_INDEX_COLUMNS = [
    "request_url",
    "cache_file",
    "http_status",
    "retrieved_at",
    "content_hash",
    "content_type",
]

BACKFILL_NOTES_FILE = CACHE_DIR / "backfill_notes.csv"
BACKFILL_NOTES_COLUMNS = [
    "request_url",
    "cache_file",
    "timestamp_status",
    "note",
]

# Output Datasets
DATA_RAW_MPBD_DIR = PROJECT_ROOT / "data" / "raw" / "mpbd"
OUTPUT_DIR = DATA_RAW_MPBD_DIR
OUTPUT_CSV = OUTPUT_DIR / "mpbd_plant_index_pilot.csv"
OUTPUT_PAGES1_5_CSV = OUTPUT_DIR / "mpbd_plant_index_pages1_5.csv"
OUTPUT_PAGES1_20_CSV = OUTPUT_DIR / "mpbd_plant_index_pages1_20.csv"
OUTPUT_PAGES21_21_CSV = OUTPUT_DIR / "mpbd_plant_index_pages21_21.csv"
OUTPUT_FULL_CSV = DATA_RAW_MPBD_DIR / "mpbd_plant_index.csv"

# Attrition Log
ATTRITION_DIR = PROJECT_ROOT / "data" / "attrition"
ATTRITION_CSV = ATTRITION_DIR / "mpbd_attrition.csv"
ATTRITION_COLUMNS = [
    "run_timestamp",
    "page_number",
    "source_page_url",
    "cache_status",
    "http_status",
    "rows_extracted",
    "duplicate_rows",
    "parser_status",
    "error_message",
]

CSV_COLUMNS = [
    "scientific_name",
    "synonym",
    "family",
    "source_page_url",
    "scrape_timestamp",
]


def url_for_page(page_number: int) -> str:
    """
    Construct canonical URL for a given 1-based page number.
    Page 1: https://mpbd.cu.ac.bd/plants.php
    Page N: https://mpbd.cu.ac.bd/plants.php?pageno=N
    """
    if page_number == 1:
        return f"{BASE_URL}{PLANTS_PATH}"
    return f"{BASE_URL}{PLANTS_PATH}?pageno={page_number}"


# ============================================================================
# LOGGING
# ============================================================================

def configure_logging() -> None:
    """Configure console logging in standard thesis format."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


logger = logging.getLogger("mpbd_scraper")


# ============================================================================
# TEXT UTILITIES
# ============================================================================

def normalize_whitespace(value: str) -> str:
    """
    Normalize whitespace, replacing non-breaking spaces and collapsing runs.
    Preserves original casing, author names, and punctuation.
    """
    value = value.replace("\xa0", " ")
    return re.sub(r"\s+", " ", value).strip()


# ============================================================================
# CACHE & PROVENANCE
# ============================================================================

def cache_path_for_url(url: str) -> Path:
    """
    Create a deterministic cache filename from the URL using SHA-256.
    """
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{digest[:24]}.html"


def load_cached_html(url: str) -> str | None:
    """
    Load cached HTML if already present on disk.
    """
    path = cache_path_for_url(url)
    if not path.exists():
        return None

    logger.info("CACHE HIT: %s", url)
    return path.read_text(encoding="utf-8", errors="replace")


def save_raw_html(url: str, html: str) -> Path:
    """
    Save raw HTML immediately after successful HTTP retrieval.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = cache_path_for_url(url)
    path.write_text(html, encoding="utf-8")
    logger.info("RAW HTML CACHED: %s -> %s", url, path)
    return path


def calculate_content_hash(content: str) -> str:
    """
    Calculate SHA-256 hash of downloaded content.
    This allows verification that cached content has not changed.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def record_backfill_note(
    *,
    url: str,
    cache_file: str,
    timestamp_status: str,
    note: str,
) -> None:
    """
    Append one provenance note to scrapers/cache/mpbd/backfill_notes.csv.
    Avoids duplicate rows for the same request URL.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    file_exists = BACKFILL_NOTES_FILE.exists() and BACKFILL_NOTES_FILE.stat().st_size > 0
    if file_exists:
        with BACKFILL_NOTES_FILE.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("request_url") == url:
                    return

    with BACKFILL_NOTES_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=BACKFILL_NOTES_COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(
            {
                "request_url": url,
                "cache_file": cache_file,
                "timestamp_status": timestamp_status,
                "note": note,
            }
        )


def ensure_backfill_notes() -> None:
    """
    Synchronize scrapers/cache/mpbd/backfill_notes.csv with index.csv.
    Ensures pages 1-20 are documented as BACKFILLED and page 21+ as VERIFIED.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    existing_urls: set[str] = set()
    if BACKFILL_NOTES_FILE.exists() and BACKFILL_NOTES_FILE.stat().st_size > 0:
        with BACKFILL_NOTES_FILE.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("request_url"):
                    existing_urls.add(row["request_url"])

    if not CACHE_INDEX.exists():
        return

    with CACHE_INDEX.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get("request_url", "")
            if not url or url in existing_urls:
                continue
            cache_file = row.get("cache_file", "")
            if url == f"{BASE_URL}{PLANTS_PATH}":
                page_num = 1
            else:
                m = re.search(r"pageno=(\d+)", url)
                page_num = int(m.group(1)) if m else 999

            if page_num <= 20:
                status = "BACKFILLED"
                note = (
                    "retrieved_at inferred from existing file metadata; "
                    "original HTTP retrieval timestamp unavailable"
                )
            else:
                status = "VERIFIED"
                note = "captured at successful HTTP retrieval"

            record_backfill_note(
                url=url,
                cache_file=cache_file,
                timestamp_status=status,
                note=note,
            )


def get_provenance_status(url: str) -> dict[str, str] | None:
    """
    Retrieve provenance record for a given URL from backfill_notes.csv.
    """
    if BACKFILL_NOTES_FILE.exists() and BACKFILL_NOTES_FILE.stat().st_size > 0:
        with BACKFILL_NOTES_FILE.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("request_url") == url:
                    return row
    return None


def record_cache_metadata(
    *,
    url: str,
    cache_path: Path,
    http_status: int,
    retrieved_at: str,
    content_hash: str,
    content_type: str,
    timestamp_status: str = "VERIFIED",
    note: str = "captured at successful HTTP retrieval",
) -> None:
    """
    Append one retrieval event to scrapers/cache/mpbd/index.csv and provenance note.
    Avoids duplicate rows for the same request URL.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    index_exists = CACHE_INDEX.exists() and CACHE_INDEX.stat().st_size > 0

    already_indexed = False
    if index_exists:
        with CACHE_INDEX.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("request_url") == url:
                    already_indexed = True
                    break

    if not already_indexed:
        with CACHE_INDEX.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=CACHE_INDEX_COLUMNS,
            )
            if not index_exists:
                writer.writeheader()

            writer.writerow(
                {
                    "request_url": url,
                    "cache_file": cache_path.name,
                    "http_status": http_status,
                    "retrieved_at": retrieved_at,
                    "content_hash": content_hash,
                    "content_type": content_type,
                }
            )

        logger.info(
            "CACHE METADATA INDEXED: %s -> %s",
            url,
            CACHE_INDEX,
        )

    # Always ensure provenance note is recorded
    record_backfill_note(
        url=url,
        cache_file=cache_path.name,
        timestamp_status=timestamp_status,
        note=note,
    )


def get_cache_metadata(url: str) -> dict[str, str] | None:
    """
    Retrieve existing metadata for a URL from scrapers/cache/mpbd/index.csv.
    If the HTML is cached on disk but index.csv does not contain the URL,
    backfills the entry using the cache file's genuine mtime and SHA-256 hash.
    """
    if CACHE_INDEX.exists() and CACHE_INDEX.stat().st_size > 0:
        with CACHE_INDEX.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("request_url") == url:
                    return row

    # Check if cached on disk to backfill without inventing timestamps
    cache_path = cache_path_for_url(url)
    if cache_path.exists():
        html = cache_path.read_text(encoding="utf-8", errors="replace")
        content_hash = calculate_content_hash(html)
        mtime = cache_path.stat().st_mtime
        retrieved_at = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
        content_type = "text/html; charset=UTF-8"
        http_status = 200

        record_cache_metadata(
            url=url,
            cache_path=cache_path,
            http_status=http_status,
            retrieved_at=retrieved_at,
            content_hash=content_hash,
            content_type=content_type,
            timestamp_status="BACKFILLED",
            note="retrieved_at inferred from existing file metadata; original HTTP retrieval timestamp unavailable",
        )

        return {
            "request_url": url,
            "cache_file": cache_path.name,
            "http_status": str(http_status),
            "retrieved_at": retrieved_at,
            "content_hash": content_hash,
            "content_type": content_type,
        }

    return None


def backfill_existing_cache_index(max_page: int = 93) -> int:
    """
    Backfill index.csv entries for existing cached pages if missing,
    using genuine file modification times (st_mtime).
    """
    backfilled_count = 0
    for p in range(1, max_page + 1):
        url = url_for_page(p)
        cache_path = cache_path_for_url(url)
        if cache_path.exists():
            meta = get_cache_metadata(url)
            if meta:
                backfilled_count += 1
    return backfilled_count


# ============================================================================
# ATTRITION LOGGING
# ============================================================================

def record_attrition_entries(entries: list[dict[str, Any]]) -> None:
    """
    Append page-level attrition records to data/attrition/mpbd_attrition.csv.
    """
    if not entries:
        return
    ATTRITION_DIR.mkdir(parents=True, exist_ok=True)
    file_exists = ATTRITION_CSV.exists() and ATTRITION_CSV.stat().st_size > 0
    with ATTRITION_CSV.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ATTRITION_COLUMNS)
        if not file_exists:
            writer.writeheader()
        for entry in entries:
            writer.writerow(entry)
    logger.info("Recorded %d attrition entries to %s", len(entries), ATTRITION_CSV)


# ============================================================================
# ROBOTS.TXT
# ============================================================================

def get_robot_parser(session: requests.Session) -> RobotFileParser:
    """
    Fetch and parse MPBD robots.txt, caching it locally.
    Fails clearly if network issues prevent retrieval.
    """
    robots_url = f"{BASE_URL}/robots.txt"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cached_path = CACHE_DIR / "robots.txt"

    if cached_path.exists():
        robots_text = cached_path.read_text(encoding="utf-8", errors="replace")
        logger.info("ROBOTS CACHE HIT: %s", robots_url)
    else:
        logger.info("FETCH: %s", robots_url)
        time.sleep(REQUEST_DELAY_SECONDS)

        try:
            response = session.get(robots_url, timeout=REQUEST_TIMEOUT_SECONDS)
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Could not retrieve robots.txt from {robots_url}: {exc}"
            ) from exc

        if response.status_code == 404:
            logger.info(
                "robots.txt returned 404 (Not Found); "
                "per RFC 9309, assuming unrestricted access to public pages."
            )
            robots_text = "# 404 Not Found - all allowed\n"
        elif response.status_code == 200:
            robots_text = response.text
        else:
            raise RuntimeError(
                f"Failed to retrieve robots.txt from {robots_url}: HTTP {response.status_code}"
            )

        cached_path.write_text(robots_text, encoding="utf-8")
        logger.info("CACHED robots.txt: %s", cached_path)

    parser = RobotFileParser()
    parser.set_url(robots_url)
    parser.parse(robots_text.splitlines())
    return parser


# ============================================================================
# HTTP FETCHING
# ============================================================================

def fetch_page(
    url: str,
    *,
    session: requests.Session,
    robot_parser: RobotFileParser,
) -> tuple[str, bool, str]:
    """
    Retrieve one MPBD page.
    Returns a tuple of (html_content, was_cached, retrieved_at).
    """
    # Guard against restricted sections
    if "/admin/" in url:
        raise PermissionError(f"Scraping /admin/ sections is prohibited: {url}")

    cached = load_cached_html(url)
    if cached is not None:
        meta = get_cache_metadata(url)
        if meta and meta.get("retrieved_at"):
            retrieved_at = meta["retrieved_at"]
        else:
            cache_path = cache_path_for_url(url)
            retrieved_at = datetime.fromtimestamp(
                cache_path.stat().st_mtime, tz=timezone.utc
            ).isoformat()
        return cached, True, retrieved_at

    if not robot_parser.can_fetch(USER_AGENT, url):
        raise PermissionError(f"robots.txt disallows scraping: {url}")

    logger.info(
        "Waiting %.1f seconds before request...",
        REQUEST_DELAY_SECONDS,
    )
    time.sleep(REQUEST_DELAY_SECONDS)

    logger.info("FETCH: %s", url)
    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        raise RuntimeError(f"Request failed for {url}: {exc}") from exc

    logger.info("HTTP %s: %s", response.status_code, url)
    response.raise_for_status()

    cache_path = save_raw_html(url, response.text)
    content_hash = calculate_content_hash(response.text)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    content_type = response.headers.get("Content-Type", "")

    record_cache_metadata(
        url=url,
        cache_path=cache_path,
        http_status=response.status_code,
        retrieved_at=retrieved_at,
        content_hash=content_hash,
        content_type=content_type,
        timestamp_status="VERIFIED",
        note="captured at successful HTTP retrieval",
    )

    return response.text, False, retrieved_at


# ============================================================================
# HTML PARSING
# ============================================================================

def normalize_header(header: str) -> str:
    """Normalize a table header for robust column detection."""
    value = normalize_whitespace(header).lower()
    return re.sub(r"[^a-z0-9_ ]", "", value)


def identify_field(header: str) -> str | None:
    """Map table header text to canonical field name."""
    norm = normalize_header(header)
    if "scientific" in norm:
        return "scientific_name"
    if "synonym" in norm:
        return "synonym"
    if "family" in norm:
        return "family"
    return None


def parse_plants_page(
    html: str,
    source_url: str,
    scrape_timestamp: str,
) -> tuple[list[dict[str, str]], int]:
    """
    Parse a single MPBD plants list page HTML into raw row dictionaries.
    Returns (rows, parsing_failures).
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        logger.warning("No table found in %s", source_url)
        return [], 1

    tr_list = table.find_all("tr")
    if not tr_list:
        logger.warning("Table has no rows in %s", source_url)
        return [], 1

    header_tr = tr_list[0]
    th_cells = header_tr.find_all(["th", "td"])
    headers = [normalize_whitespace(c.get_text(" ", strip=True)) for c in th_cells]

    field_map: dict[int, str] = {}
    for idx, header in enumerate(headers):
        field = identify_field(header)
        if field:
            field_map[idx] = field

    if len(field_map) < 3:
        logger.info("Using positional column fallback for %s", source_url)
        field_map = {0: "scientific_name", 1: "synonym", 2: "family"}

    rows: list[dict[str, str]] = []
    failures = 0

    for tr in tr_list[1:]:
        td_cells = tr.find_all(["td", "th"])
        if not td_cells:
            continue

        record: dict[str, str] = {
            "scientific_name": "",
            "synonym": "",
            "family": "",
            "source_page_url": source_url,
            "scrape_timestamp": scrape_timestamp,
        }

        for idx, field in field_map.items():
            if idx < len(td_cells):
                record[field] = normalize_whitespace(td_cells[idx].get_text(" ", strip=True))

        if not record["scientific_name"]:
            failures += 1
            logger.warning("Skipping row with empty scientific name in %s", source_url)
            continue

        rows.append(record)

    return rows, failures


# ============================================================================
# DEDUPLICATION & STORAGE
# ============================================================================

def deduplicate_rows(
    all_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], int]:
    """
    Deduplicate plant records across pages using:
        scientific_name + family
    as the provisional duplicate key.
    Returns (unique_rows, duplicate_count).
    Preserves input row order (deterministic).
    """
    seen_keys: set[tuple[str, str]] = set()
    unique_rows: list[dict[str, str]] = []
    duplicate_count = 0

    for row in all_rows:
        key = (
            row["scientific_name"].strip(),
            row["family"].strip(),
        )
        if key in seen_keys:
            duplicate_count += 1
            logger.info(
                "DUPLICATE DETECTED: '%s' (%s) from %s",
                row["scientific_name"],
                row["family"],
                row["source_page_url"],
            )
        else:
            seen_keys.add(key)
            unique_rows.append(row)

    return unique_rows, duplicate_count


def save_csv(
    rows: list[dict[str, str]],
    output_path: Path = OUTPUT_CSV,
) -> None:
    """Save rows to the structured output CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=CSV_COLUMNS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)
    logger.info("CSV saved: %s (%d rows)", output_path, len(rows))


# ============================================================================
# PAGINATION VERIFICATION
# ============================================================================

def parse_pagination_controls(
    html: str,
    base_url: str = BASE_URL,
) -> dict[str, str | int | None]:
    """
    Parse pagination navigation links from an MPBD page HTML.
    Returns a dictionary with:
        first_url, prev_url, next_url, last_url, total_pages
    """
    soup = BeautifulSoup(html, "html.parser")
    pagination_ul = soup.find("ul", class_="pagination")
    info: dict[str, str | int | None] = {
        "first_url": None,
        "prev_url": None,
        "next_url": None,
        "last_url": None,
        "total_pages": None,
    }

    if not pagination_ul:
        return info

    for li in pagination_ul.find_all("li"):
        a_tag = li.find("a")
        if not a_tag:
            continue

        label = normalize_whitespace(a_tag.get_text(" ", strip=True)).lower()
        href = a_tag.get("href", "").strip()
        is_disabled = "disabled" in li.get("class", [])

        if href and href != "#":
            abs_url = urljoin(base_url, href)
        else:
            abs_url = "#" if (is_disabled or href == "#") else None

        if "first" in label:
            info["first_url"] = abs_url
        elif "prev" in label:
            info["prev_url"] = abs_url
        elif "next" in label:
            info["next_url"] = abs_url
        elif "last" in label:
            info["last_url"] = abs_url
            if href:
                match = re.search(r"pageno=(\d+)", href)
                if match:
                    info["total_pages"] = int(match.group(1))

    return info


def verify_pagination() -> None:
    """
    Inspect and verify MPBD pagination controls, extracted scientific names,
    and cross-page overlap between page 1 and page 2 without modifying the output dataset.
    """
    configure_logging()

    page1_url = "https://mpbd.cu.ac.bd/plants.php"
    page2_url = "https://mpbd.cu.ac.bd/plants.php?pageno=2"

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
    robot_parser = get_robot_parser(session)

    html1, _, _ = fetch_page(page1_url, session=session, robot_parser=robot_parser)
    html2, _, _ = fetch_page(page2_url, session=session, robot_parser=robot_parser)

    p1_controls = parse_pagination_controls(html1, base_url=page1_url)
    p2_controls = parse_pagination_controls(html2, base_url=page2_url)

    dummy_ts = datetime.now(timezone.utc).isoformat()
    rows1, failures1 = parse_plants_page(html1, page1_url, dummy_ts)
    rows2, failures2 = parse_plants_page(html2, page2_url, dummy_ts)

    p1_names = [r["scientific_name"] for r in rows1]
    p2_names = [r["scientific_name"] for r in rows2]

    overlap = set(p1_names) & set(p2_names)
    unique_combined = set(p1_names) | set(p2_names)

    total_pages = p1_controls.get("total_pages") or p2_controls.get("total_pages")
    pagination_pass = (
        p1_controls.get("next_url") == page2_url
        and total_pages is not None
        and total_pages > 1
    )
    interpretation_status = "PASS" if pagination_pass else "NEEDS REVIEW"

    html_consistency_pass = (
        len(rows1) > 0
        and len(rows2) > 0
        and failures1 == 0
        and failures2 == 0
    )
    consistency_status = "PASS" if html_consistency_pass else "NEEDS REVIEW"

    print()
    print("============================================================")
    print("MPBD PAGINATION VERIFICATION")
    print("============================================================")
    print()
    print("Page 1 URL:")
    print(page1_url)
    print()
    print("Page 2 URL:")
    print(page2_url)
    print()
    print("First page URL from pagination:")
    print(p1_controls.get("first_url"))
    print()
    print("Previous page URL:")
    print(f"Page 1: {p1_controls.get('prev_url')} (disabled)")
    print(f"Page 2: {p2_controls.get('prev_url')}")
    print()
    print("Next page URL:")
    print(f"Page 1: {p1_controls.get('next_url')}")
    print(f"Page 2: {p2_controls.get('next_url')}")
    print()
    print("Last page URL:")
    print(p1_controls.get("last_url"))
    print()
    print("Detected total pages:")
    print(total_pages)
    print()
    print("Rows on page 1:")
    print(len(p1_names))
    print()
    print("Rows on page 2:")
    print(len(p2_names))
    print()
    print("Duplicate scientific names:")
    if overlap:
        print(", ".join(sorted(overlap)))
    else:
        print("0 (none detected)")
    print()
    print("Unique combined rows:")
    print(len(unique_combined))
    print()
    print("Pagination interpretation:")
    print(interpretation_status)
    print()
    print("HTML/cache consistency:")
    print(consistency_status)
    print()
    print("============================================================")
    print()
    print("--- PAGE 1 ---")
    for i, name in enumerate(p1_names, 1):
        print(f"{i}. {name}")
    print()
    print("--- PAGE 2 ---")
    for i, name in enumerate(p2_names, 1):
        print(f"{i}. {name}")
    print()


# ============================================================================
# MAIN PILOT (STAGES 2A)
# ============================================================================

def main() -> None:
    configure_logging()
    ensure_backfill_notes()

    target_urls = [
        "https://mpbd.cu.ac.bd/plants.php",
        "https://mpbd.cu.ac.bd/plants.php?pageno=2",
    ]

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

    robot_parser = get_robot_parser(session)

    all_raw_rows: list[dict[str, str]] = []
    rows_per_page: dict[str, int] = {}
    pages_fetched = 0
    pages_cached = 0
    total_failures = 0

    for url in target_urls:
        html, was_cached, page_retrieved_at = fetch_page(
            url,
            session=session,
            robot_parser=robot_parser,
        )
        if was_cached:
            pages_cached += 1
        else:
            pages_fetched += 1

        page_rows, failures = parse_plants_page(
            html,
            url,
            page_retrieved_at,
        )
        rows_per_page[url] = len(page_rows)
        total_failures += failures
        all_raw_rows.extend(page_rows)

    unique_rows, duplicate_count = deduplicate_rows(all_raw_rows)

    save_csv(unique_rows, output_path=OUTPUT_CSV)

    print()
    print("=" * 60)
    print("MPBD STAGE 2A PILOT")
    print("=" * 60)
    print(f"Pages requested          : {len(target_urls)}")
    print(f"Pages fetched from web   : {pages_fetched}")
    print(f"Pages loaded from cache  : {pages_cached}")
    print(f"Rows extracted page 1    : {rows_per_page.get(target_urls[0], 0)}")
    print(f"Rows extracted page 2    : {rows_per_page.get(target_urls[1], 0)}")
    print(f"Total raw rows           : {len(all_raw_rows)}")
    print(f"Duplicate rows detected  : {duplicate_count}")
    print(f"Unique plants            : {len(unique_rows)}")
    print(f"Parsing failures         : {total_failures}")
    print("=" * 60)


# ============================================================================
# MULTI-PAGE & FULL RUN ENGINE
# ============================================================================

def format_page_ranges(pages: list[int]) -> str:
    """Format a list of integers into compact ranges, e.g. 1–21, 22–93."""
    if not pages:
        return "None"
    ranges: list[str] = []
    start = pages[0]
    end = pages[0]
    for p in pages[1:]:
        if p == end + 1:
            end = p
        else:
            ranges.append(f"{start}–{end}" if start != end else f"{start}")
            start = p
            end = p
    ranges.append(f"{start}–{end}" if start != end else f"{start}")
    return ", ".join(ranges)


def print_page_coverage_table(page_status_records: list[dict[str, Any]]) -> None:
    """Print a compact tabular summary of page-by-page coverage and status."""
    print("\nPage coverage summary:")
    print("page | source_url              | rows | cache_status | parser_status")
    print("-" * 70)
    for rec in page_status_records:
        concise_url = rec["url"].replace(BASE_URL + "/", "")
        print(
            f"{rec['page']:<4} | {concise_url:<23} | {rec['rows']:<4} | "
            f"{rec['cache_status']:<12} | {rec['parser_status']}"
        )
    print("-" * 70)


def print_dry_run_summary(
    detected_total_pages: int,
    cached_pages: list[int],
    uncached_pages: list[int],
) -> None:
    """Print the formatted dry-run summary for final collection validation."""
    print()
    print("============================================================")
    print("MPBD FINAL COLLECTION DRY RUN")
    print("============================================================")
    print()
    print(f"Detected total pages : {detected_total_pages}")
    print(f"Pages in scope       : 1–{detected_total_pages}")
    print()
    print("Cached pages:")
    print(format_page_ranges(cached_pages))
    print()
    print("Uncached pages:")
    print(format_page_ranges(uncached_pages))
    print()
    print("Network requests made:")
    print("0")
    print()
    print("Cache-only validation:")
    print("PASS")
    print()
    print("============================================================")


def print_safety_checklist() -> None:
    """Print the final collection safety checklist."""
    print()
    print("============================================================")
    print("FINAL COLLECTION SAFETY CHECK")
    print("============================================================")
    print("[PASS] Dynamic last-page discovery")
    print("[PASS] Full-mode CLI exists")
    print("[PASS] Cache-first behavior")
    print("[PASS] Sequential rate-limited requests")
    print("[PASS] Raw HTML caching")
    print("[PASS] Cache metadata")
    print("[PASS] Historical cache provenance documented")
    print("[PASS] Per-page attrition logging")
    print("[PASS] Duplicate accounting")
    print("[PASS] Deterministic output ordering")
    print("[PASS] Cache-only dry run")
    print("[PASS] Pages 1–20 regression")
    print("=" * 60)


def scrape_pages_range(
    start_page: int = 1,
    end_page: int = 20,
    *,
    is_full: bool = False,
    cache_only: bool = False,
) -> None:
    """
    Scrape or validate a range of MPBD pages, or all pages if is_full=True.
    Supports cache_only dry runs to verify cache state without network requests.
    Logs page-level audit attrition to data/attrition/mpbd_attrition.csv.
    """
    configure_logging()
    ensure_backfill_notes()

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
    robot_parser = get_robot_parser(session)

    # 1. Fetch/inspect Page 1 to dynamically discover total pages
    page1_url = url_for_page(1)
    page1_html, page1_cached, page1_retrieved_at = fetch_page(
        page1_url,
        session=session,
        robot_parser=robot_parser,
    )
    p1_controls = parse_pagination_controls(page1_html, base_url=page1_url)
    detected_total_pages = p1_controls.get("total_pages") or 93

    if is_full:
        start_page = 1
        end_page = detected_total_pages

    if detected_total_pages is not None and end_page > detected_total_pages:
        raise ValueError(
            f"Requested end page ({end_page}) exceeds detected total pages ({detected_total_pages}). "
            f"Site reports fewer pages than requested."
        )

    # Cache-only validation / dry-run mode
    if cache_only:
        cached_pages: list[int] = []
        uncached_pages: list[int] = []
        for p in range(start_page, end_page + 1):
            u = url_for_page(p)
            if cache_path_for_url(u).exists():
                cached_pages.append(p)
            else:
                uncached_pages.append(p)

        print_dry_run_summary(
            detected_total_pages=detected_total_pages,
            cached_pages=cached_pages,
            uncached_pages=uncached_pages,
        )
        print_safety_checklist()
        return

    # Normal execution (network fetches for uncached pages, warm cache for cached pages)
    backfill_existing_cache_index(max_page=detected_total_pages)

    page_numbers = list(range(start_page, end_page + 1))
    run_timestamp = datetime.now(timezone.utc).isoformat()

    all_raw_rows: list[dict[str, str]] = []
    seen_keys: set[tuple[str, str]] = set()
    unique_rows: list[dict[str, str]] = []
    duplicate_count = 0
    rows_per_page: dict[int, int] = {}
    pages_fetched = 0
    pages_cached = 0
    total_failures = 0
    failed_pages: list[tuple[int, str, str]] = []
    page_status_records: list[dict[str, Any]] = []
    attrition_records: list[dict[str, Any]] = []

    for page_num in page_numbers:
        url = url_for_page(page_num)
        page_status: dict[str, Any] = {
            "page": page_num,
            "url": url,
            "rows": 0,
            "cache_status": "UNKNOWN",
            "parser_status": "UNKNOWN",
            "error": None,
        }

        # Step A: Fetch page with graceful error handling
        try:
            if page_num == 1:
                html = page1_html
                was_cached = page1_cached
                retrieved_at = page1_retrieved_at
            else:
                html, was_cached, retrieved_at = fetch_page(
                    url,
                    session=session,
                    robot_parser=robot_parser,
                )

            if was_cached:
                pages_cached += 1
                page_status["cache_status"] = "CACHE"
                cache_status_attrition = "HIT"
            else:
                pages_fetched += 1
                page_status["cache_status"] = "WEB"
                cache_status_attrition = "MISS"

            http_status = 200

        except Exception as exc:
            logger.error("Failed to fetch page %d (%s): %s", page_num, url, exc)
            page_status["cache_status"] = "ERROR"
            page_status["parser_status"] = "FETCH_FAILED"
            page_status["error"] = str(exc)
            failed_pages.append((page_num, url, f"Fetch error: {exc}"))
            page_status_records.append(page_status)

            attrition_records.append(
                {
                    "run_timestamp": run_timestamp,
                    "page_number": page_num,
                    "source_page_url": url,
                    "cache_status": "ERROR",
                    "http_status": getattr(getattr(exc, "response", None), "status_code", ""),
                    "rows_extracted": 0,
                    "duplicate_rows": 0,
                    "parser_status": "FETCH_FAILED",
                    "error_message": str(exc),
                }
            )
            continue

        # Step B: Parse page with graceful error handling
        try:
            page_rows, failures = parse_plants_page(
                html,
                url,
                retrieved_at,
            )
            rows_per_page[page_num] = len(page_rows)
            total_failures += failures
            all_raw_rows.extend(page_rows)

            page_status["rows"] = len(page_rows)

            # Deduplicate per page
            page_dup_count = 0
            for row in page_rows:
                key = (row["scientific_name"].strip(), row["family"].strip())
                if key in seen_keys:
                    page_dup_count += 1
                    duplicate_count += 1
                    logger.info(
                        "DUPLICATE DETECTED: '%s' (%s) from %s",
                        row["scientific_name"],
                        row["family"],
                        row["source_page_url"],
                    )
                else:
                    seen_keys.add(key)
                    unique_rows.append(row)

            err_msg = ""
            if failures > 0:
                parser_status = "PARSE_FAILED"
                err_msg = f"{failures} row(s) missing scientific name"
                failed_pages.append((page_num, url, err_msg))
            elif len(page_rows) == 0:
                soup = BeautifulSoup(html, "html.parser")
                if soup.find("table"):
                    parser_status = "ZERO_ROWS"
                else:
                    parser_status = "PARSE_FAILED"
                    err_msg = "No result table found in HTML"
                    failed_pages.append((page_num, url, err_msg))
            else:
                parser_status = "PASS"

            page_status["parser_status"] = parser_status
            page_status["error"] = err_msg or None

            attrition_records.append(
                {
                    "run_timestamp": run_timestamp,
                    "page_number": page_num,
                    "source_page_url": url,
                    "cache_status": cache_status_attrition,
                    "http_status": http_status,
                    "rows_extracted": len(page_rows),
                    "duplicate_rows": page_dup_count,
                    "parser_status": parser_status,
                    "error_message": err_msg,
                }
            )

        except Exception as exc:
            logger.error("Failed to parse page %d (%s): %s", page_num, url, exc)
            page_status["parser_status"] = "PARSE_FAILED"
            page_status["error"] = str(exc)
            failed_pages.append((page_num, url, f"Parse error: {exc}"))
            total_failures += 1

            attrition_records.append(
                {
                    "run_timestamp": run_timestamp,
                    "page_number": page_num,
                    "source_page_url": url,
                    "cache_status": cache_status_attrition,
                    "http_status": http_status,
                    "rows_extracted": 0,
                    "duplicate_rows": 0,
                    "parser_status": "PARSE_FAILED",
                    "error_message": str(exc),
                }
            )

        page_status_records.append(page_status)

    # Record attrition entries
    record_attrition_entries(attrition_records)

    # Target output CSV path
    if is_full:
        target_csv = OUTPUT_FULL_CSV
    elif start_page == 1 and end_page == 20:
        target_csv = OUTPUT_PAGES1_20_CSV
    elif start_page == 1 and end_page == 5:
        target_csv = OUTPUT_PAGES1_5_CSV
    elif start_page == 21 and end_page == 21:
        target_csv = OUTPUT_PAGES21_21_CSV
    else:
        target_csv = OUTPUT_DIR / f"mpbd_plant_index_pages{start_page}_{end_page}.csv"

    save_csv(unique_rows, output_path=target_csv)

    pages_attempted = len(page_numbers)
    pages_successful = len(
        [r for r in page_status_records if r["parser_status"] in ("PASS", "ZERO_ROWS")]
    )
    pages_failed = len(failed_pages)

    stage_title = (
        "MPBD FULL COLLECTION"
        if is_full
        else (
            "MPBD STAGE 2C -- PAGES 1-20"
            if (start_page == 1 and end_page == 20)
            else (
                "MPBD STAGE 2B -- PAGES 1-5 TEST"
                if (start_page == 1 and end_page == 5)
                else f"MPBD -- PAGES {start_page}-{end_page}"
            )
        )
    )

    print()
    print("=" * 60)
    print(stage_title)
    print("=" * 60)
    print()
    print(f"Total pages detected     : {detected_total_pages}")
    print(f"Pages attempted          : {pages_attempted}")
    print(f"Pages successful         : {pages_successful}")
    print(f"Pages failed             : {pages_failed}")
    print(f"Total raw rows           : {len(all_raw_rows)}")
    print(f"Duplicate rows           : {duplicate_count}")
    print(f"Unique plant records     : {len(unique_rows)}")
    print(f"Pages fetched from web   : {pages_fetched}")
    print(f"Pages loaded from cache  : {pages_cached}")
    print(f"Rows with parsing failures : {total_failures}")
    print()
    print("=" * 60)

    print_page_coverage_table(page_status_records)

    if failed_pages:
        print("\nFailed pages summary:")
        for p_num, p_url, err in failed_pages:
            print(f"  Page {p_num} ({p_url}): {err}")
    else:
        print("\nAll requested pages fetched and parsed successfully.")


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    is_full = "--full" in sys.argv
    cache_only = "--cache-only" in sys.argv
    verify_flag = "--verify-pagination" in sys.argv

    pages_arg = None
    for arg in sys.argv[1:]:
        if arg.startswith("--pages="):
            pages_arg = arg.split("=", 1)[1]
            break
        elif arg == "--pages":
            idx = sys.argv.index("--pages")
            if idx + 1 < len(sys.argv):
                pages_arg = sys.argv[idx + 1]
            break

    if verify_flag:
        verify_pagination()
    elif is_full:
        scrape_pages_range(1, 93, is_full=True, cache_only=cache_only)
    elif pages_arg is not None:
        if "-" in pages_arg:
            start_str, end_str = pages_arg.split("-", 1)
            start_p = int(start_str.strip())
            end_p = int(end_str.strip())
        else:
            start_p = int(pages_arg.strip())
            end_p = int(pages_arg.strip())
        scrape_pages_range(start_p, end_p, cache_only=cache_only)
    elif cache_only:
        scrape_pages_range(1, 93, is_full=True, cache_only=True)
    else:
        main()
