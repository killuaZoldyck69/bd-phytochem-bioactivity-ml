"""
bmppd_scraper.py

BMPPD Stage 1 — single-query pilot scraper.

Current discovery:
BMPPD search requests are handled through:

    https://bmppd.org/bmppd_result/?q=<query>

Example:

    python scrapers/bmppd_scraper.py

This pilot searches for:

    Azadirachta indica

and extracts:

    plant_name
    common_name
    compound_name
    pubchem_cid
    reference_link
    source_page_url
    scrape_timestamp

The raw HTML response is cached locally before parsing.
"""

from __future__ import annotations

import csv
import hashlib
import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus, urljoin
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup


# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URL = "https://bmppd.org"

SEARCH_PATH = "/bmppd_result/"

# Replace this with your real research contact email.
CONTACT_EMAIL = "YOUR_EMAIL@example.com"

USER_AGENT = (
    "BMPPD-Thesis-Scraper/0.1 "
    "(Nahid; undergraduate research; "
    f"contact: {CONTACT_EMAIL})"
)

# Minimum delay between network requests.
REQUEST_DELAY_SECONDS = 1.5

REQUEST_TIMEOUT_SECONDS = 30

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CACHE_DIR = PROJECT_ROOT / "scrapers" / "cache"

CACHE_INDEX = CACHE_DIR / "index.csv"

CACHE_INDEX_COLUMNS = [
    "request_url",
    "cache_file",
    "http_status",
    "retrieved_at",
    "content_hash",
    "content_type",
]

OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "bmppd"

OUTPUT_CSV = OUTPUT_DIR / "bmppd_pilot.csv"


# ============================================================================
# LOGGING
# ============================================================================

def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


logger = logging.getLogger("bmppd_scraper")


# ============================================================================
# TEXT UTILITIES
# ============================================================================

def normalize_whitespace(value: str) -> str:
    """
    Normalize whitespace, including non-breaking spaces.
    """

    value = value.replace("\xa0", " ")

    return re.sub(
        r"\s+",
        " ",
        value,
    ).strip()


# ============================================================================
# CACHE
# ============================================================================

def cache_path_for_url(url: str) -> Path:
    """
    Create a deterministic cache filename from the URL.

    The same URL always maps to the same cached file.
    """

    digest = hashlib.sha256(
        url.encode("utf-8")
    ).hexdigest()

    return CACHE_DIR / f"{digest[:24]}.html"


def load_cached_html(url: str) -> str | None:
    """
    Load cached HTML if it already exists.
    """

    path = cache_path_for_url(url)

    if not path.exists():
        return None

    logger.info(
        "CACHE HIT: %s",
        url,
    )

    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def save_raw_html(
    url: str,
    html: str,
) -> Path:
    """
    Save raw HTML immediately after successful HTTP retrieval.
    """

    CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = cache_path_for_url(url)

    path.write_text(
        html,
        encoding="utf-8",
    )

    logger.info(
        "RAW HTML CACHED: %s -> %s",
        url,
        path,
    )

    return path

def calculate_content_hash(
    content: str,
) -> str:
    """
    Calculate SHA-256 hash of downloaded content.

    This allows us to verify that the cached content has not changed.
    """

    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


def record_cache_metadata(
    *,
    url: str,
    cache_path: Path,
    http_status: int,
    retrieved_at: str,
    content_hash: str,
    content_type: str,
) -> None:
    """
    Append one retrieval event to cache/index.csv.
    """

    CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    index_exists = CACHE_INDEX.exists() and CACHE_INDEX.stat().st_size > 0

    with CACHE_INDEX.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as file:

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

# ============================================================================
# ROBOTS.TXT
# ============================================================================

def get_robot_parser(
    session: requests.Session,
) -> RobotFileParser:
    """
    Fetch robots.txt and build a RobotFileParser from it.
    """

    robots_url = f"{BASE_URL}/robots.txt"

    cached_path = CACHE_DIR / "robots.txt"

    if cached_path.exists():
        robots_text = cached_path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        logger.info(
            "ROBOTS CACHE HIT: %s",
            robots_url,
        )

    else:
        logger.info(
            "FETCH: %s",
            robots_url,
        )

        time.sleep(
            REQUEST_DELAY_SECONDS
        )

        response = session.get(
            robots_url,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

        response.raise_for_status()

        CACHE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        robots_text = response.text

        cached_path.write_text(
            robots_text,
            encoding="utf-8",
        )

        logger.info(
            "CACHED robots.txt: %s",
            cached_path,
        )

    parser = RobotFileParser()

    parser.set_url(
        robots_url
    )

    parser.parse(
        robots_text.splitlines()
    )

    return parser


# ============================================================================
# URL CONSTRUCTION
# ============================================================================

def build_search_url(
    query: str,
) -> str:
    """
    Build the BMPPD search URL.

    Example:

        Azadirachta indica

    becomes:

        https://bmppd.org/bmppd_result/?q=Azadirachta+indica
    """

    return (
        f"{BASE_URL}"
        f"{SEARCH_PATH}"
        f"?q={quote_plus(query)}"
    )


# ============================================================================
# HTTP
# ============================================================================

def fetch_search_page(
    url: str,
    *,
    session: requests.Session,
    robot_parser: RobotFileParser,
) -> str:
    """
    Retrieve one BMPPD search page.

    Cached pages are never requested again.
    """

    cached = load_cached_html(url)

    if cached is not None:
        return cached

    # ------------------------------------------------------------
    # Respect robots.txt
    # ------------------------------------------------------------

    if not robot_parser.can_fetch(
        USER_AGENT,
        url,
    ):
        raise PermissionError(
            f"robots.txt disallows:\n{url}"
        )

    # ------------------------------------------------------------
    # Polite request delay
    # ------------------------------------------------------------

    logger.info(
        "Waiting %.1f seconds before request...",
        REQUEST_DELAY_SECONDS,
    )

    time.sleep(
        REQUEST_DELAY_SECONDS
    )

    logger.info(
        "FETCH: %s",
        url,
    )

    try:
        response = session.get(
            url,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

    except requests.RequestException as exc:
        raise RuntimeError(
            f"Request failed for {url}: {exc}"
        ) from exc

    logger.info(
        "HTTP %s: %s",
        response.status_code,
        url,
    )

    response.raise_for_status()

    # ------------------------------------------------------------
    # IMPORTANT:
    # Save raw HTML BEFORE parsing.
    # ------------------------------------------------------------

    cache_path = save_raw_html(
        url,
        response.text,
    )

    content_hash = calculate_content_hash(
        response.text
    )

    retrieved_at = datetime.now(
        timezone.utc
    ).isoformat()

    content_type = response.headers.get(
        "Content-Type",
        "",
    )

    record_cache_metadata(
        url=url,
        cache_path=cache_path,
        http_status=response.status_code,
        retrieved_at=retrieved_at,
        content_hash=content_hash,
        content_type=content_type,
    )

    return response.text


# ============================================================================
# FIELD IDENTIFICATION
# ============================================================================

def normalize_header(
    header: str,
) -> str:
    """
    Normalize a table header.
    """

    value = normalize_whitespace(
        header
    ).lower()

    value = value.replace(
        ":",
        "",
    )

    return value


def identify_field(
    header: str,
) -> str | None:
    """
    Map BMPPD table headers to our canonical field names.
    """

    value = normalize_header(
        header
    )

    # Plant
    if (
        value == "plant name"
        or value == "plant"
        or "plant name" in value
    ):
        return "plant_name"

    # Common name
    if (
        "common name" in value
        or value == "common"
    ):
        return "common_name"

    # Phytochemical
    if (
        "phytochemical" in value
        or "compound" in value
    ):
        return "compound_name"

    # PubChem
    if (
        value == "cid"
        or "pubchem" in value
    ):
        return "pubchem_cid"

    # Reference
    if (
        "reference" in value
        or "citation" in value
        or value == "source"
    ):
        return "reference_link"

    return None


# ============================================================================
# PUBCHEM CID
# ============================================================================

CID_PATTERN = re.compile(
    r"\bCID\s*:\s*(\d+)\b",
    flags=re.IGNORECASE,
)


def extract_cid(
    text: str,
) -> str:
    """
    Extract a numeric PubChem CID from text.

    Examples:

        CID: 12345
        CID: -       -> ""

    Missing CID is deliberately preserved as an empty string.
    """

    text = normalize_whitespace(
        text
    )

    match = CID_PATTERN.search(
        text
    )

    if match:
        return match.group(1)

    return ""

def identify_quality_flags(
    compound_name: str,
    pubchem_cid: str,
) -> list[str]:
    """
    Identify simple data-quality issues without altering source data.

    This function flags records for later review. It does not attempt
    to chemically correct names.
    """

    flags: list[str] = []

    # Missing PubChem CID.
    if not pubchem_cid:
        flags.append("missing_pubchem_cid")

    # Question marks often indicate uncertain/truncated source names.
    if "?" in compound_name:
        flags.append("uncertain_compound_name")

    # Very short names may deserve manual inspection.
    if len(compound_name.strip()) < 4:
        flags.append("very_short_compound_name")

    # Suspicious whitespace directly after a hyphen.
    if re.search(
        r"-\s+",
        compound_name,
    ):
        flags.append("possible_spacing_anomaly")

    return flags

# ============================================================================
# REFERENCE
# ============================================================================

def extract_reference(
    cell,
) -> str:
    """
    Extract and normalize the BMPPD reference URL.

    Relative BMPPD URLs such as:

        /reference/?ref=...

    are converted to absolute URLs:

        https://bmppd.org/reference/?ref=...

    The URL itself is not otherwise modified.
    """

    link = cell.find(
        "a",
        href=True,
    )

    if link:
        href = normalize_whitespace(
            link["href"]
        )

        if href:
            return urljoin(
                BASE_URL,
                href,
            )

    text = normalize_whitespace(
        cell.get_text(
            " ",
            strip=True,
        )
    )

    if text:
        if text.startswith("/") or text.startswith("http"):
            return urljoin(
                BASE_URL,
                text,
            )

        return text

    return ""


# ============================================================================
# TABLE PARSER
# ============================================================================

def find_result_tables(
    soup: BeautifulSoup,
):
    """
    Locate tables that appear to contain BMPPD search results.

    We don't assume an exact CSS class or HTML ID.
    Instead, we inspect their headers.
    """

    tables = soup.find_all(
        "table"
    )

    logger.info(
        "HTML tables found: %d",
        len(tables),
    )

    result_tables = []

    for index, table in enumerate(
        tables,
        start=1,
    ):

        # Prefer <th>.
        header_cells = table.find_all(
            "th"
        )

        # Fallback for tables that use <td> as headers.
        if not header_cells:
            first_row = table.find("tr")

            if first_row:
                header_cells = first_row.find_all(
                    ["td", "th"]
                )

        headers = [
            normalize_whitespace(
                cell.get_text(
                    " ",
                    strip=True,
                )
            )
            for cell in header_cells
        ]

        logger.info(
            "Table %d headers: %s",
            index,
            headers,
        )

        identified_fields = {
            identify_field(header)
            for header in headers
        }

        identified_fields.discard(None)

        if "compound_name" in identified_fields:
            result_tables.append(
                table
            )

    return result_tables


def parse_result_table(
    table,
) -> list[dict[str, str]]:
    """
    Parse one BMPPD result table.
    """

    header_cells = table.find_all(
        "th"
    )

    if not header_cells:
        first_row = table.find("tr")

        if not first_row:
            return []

        header_cells = first_row.find_all(
            ["td", "th"]
        )

    headers = [
        normalize_whitespace(
            cell.get_text(
                " ",
                strip=True,
            )
        )
        for cell in header_cells
    ]

    # Map column index -> canonical field.
    field_map: dict[int, str] = {}

    for index, header in enumerate(
        headers
    ):
        field = identify_field(
            header
        )

        if field:
            field_map[index] = field

    logger.info(
        "Detected field mapping: %s",
        field_map,
    )

    rows = []

    # All body rows.
    for tr in table.find_all("tr"):

        cells = tr.find_all(
            "td"
        )

        if not cells:
            continue

        record = {
            "plant_name": "",
            "common_name": "",
            "compound_name": "",
            "pubchem_cid": "",
            "reference_link": "",
        }

        for index, field in field_map.items():

            if index >= len(cells):
                continue

            cell = cells[index]

            text = normalize_whitespace(
                cell.get_text(
                    " ",
                    strip=True,
                )
            )

            if field == "pubchem_cid":

                record[field] = extract_cid(
                    text
                )

            elif field == "reference_link":

                record[field] = extract_reference(
                    cell
                )

            else:

                record[field] = text

        # Some BMPPD rows may contain CID text even if CID isn't
        # perfectly isolated into its expected column.
        if not record["pubchem_cid"]:

            entire_row_text = normalize_whitespace(
                tr.get_text(
                    " ",
                    strip=True,
                )
            )

            record["pubchem_cid"] = extract_cid(
                entire_row_text
            )

            record["quality_flags"] = identify_quality_flags(
            record["compound_name"],
            record["pubchem_cid"],
        )

        # Don't keep empty rows.
        if not record["compound_name"]:
            continue

        rows.append(
            record
        )

    return rows


# ============================================================================
# FULL PAGE PARSING
# ============================================================================

def parse_search_page(
    html: str,
    source_url: str,
) -> list[dict[str, str]]:
    """
    Parse the HTML result page.
    """

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    tables = find_result_tables(
        soup
    )

    if not tables:
        logger.warning(
            "No result table was detected."
        )

        return []

    all_rows = []

    for table in tables:

        rows = parse_result_table(
            table
        )

        all_rows.extend(
            rows
        )

    # ------------------------------------------------------------
    # Deduplicate
    # ------------------------------------------------------------

    unique_rows = []

    seen = set()

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    for row in all_rows:

        key = (
            row["plant_name"].lower(),
            row["compound_name"].lower(),
            row["pubchem_cid"],
            row["reference_link"],
        )

        if key in seen:
            continue

        seen.add(key)

        row["source_page_url"] = (
            source_url
        )

        row["scrape_timestamp"] = (
            timestamp
        )

        unique_rows.append(
            row
        )

    return unique_rows


# ============================================================================
# CSV
# ============================================================================

CSV_COLUMNS = [
    "plant_name",
    "common_name",
    "compound_name",
    "pubchem_cid",
    "reference_link",
    "source_page_url",
    "scrape_timestamp",
]

QC_COLUMNS = [
    "plant_name",
    "common_name",
    "compound_name",
    "pubchem_cid",
    "source_page_url",
    "quality_flags",
]


def save_csv(
    rows: list[dict[str, str]],
) -> None:

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=CSV_COLUMNS,
            extrasaction="ignore",
        )

        writer.writeheader()

        writer.writerows(
            rows
        )

    logger.info(
        "CSV saved: %s",
        OUTPUT_CSV,
    )

def save_qc_csv(
    rows: list[dict[str, str]],
) -> None:
    """
    Save only records requiring quality review.
    """

    qc_rows = []

    for row in rows:

        flags = row.get(
            "quality_flags",
            [],
        )

        if not flags:
            continue

        qc_rows.append(
            {
                "plant_name": row["plant_name"],
                "common_name": row["common_name"],
                "compound_name": row["compound_name"],
                "pubchem_cid": row["pubchem_cid"],
                "source_page_url": row["source_page_url"],
                "quality_flags": ";".join(flags),
            }
        )

    qc_path = (
        OUTPUT_DIR /
        "bmppd_pilot_qc.csv"
    )

    with qc_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=QC_COLUMNS,
        )

        writer.writeheader()
        writer.writerows(qc_rows)

    logger.info(
        "QC CSV saved: %s",
        qc_path,
    )


# ============================================================================
# STATISTICS
# ============================================================================

def print_statistics(
    rows: list[dict[str, str]],
) -> None:

    total_rows = len(rows)

    valid_cid_rows = sum(
        1
        for row in rows
        if row["pubchem_cid"]
    )

    missing_cid_rows = (
        total_rows - valid_cid_rows
    )

    print()
    print("=" * 60)
    print("BMPPD STAGE 1 PILOT RESULTS")
    print("=" * 60)
    print(
        f"Rows extracted       : {total_rows}"
    )
    print(
        f"Rows with valid CID  : {valid_cid_rows}"
    )
    print(
        f"Rows missing CID     : {missing_cid_rows}"
    )

    if total_rows:
        percentage = (
            missing_cid_rows
            / total_rows
            * 100
        )

        print(
            f"Missing CID rate     : "
            f"{percentage:.2f}%"
        )

    print("=" * 60)


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:

    configure_logging()

    # ------------------------------------------------------------
    # Session
    # ------------------------------------------------------------

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

    # ------------------------------------------------------------
    # Pilot query
    # ------------------------------------------------------------

    query = "Azadirachta indica"

    url = build_search_url(
        query
    )

    logger.info(
        "Pilot query: %s",
        query,
    )

    logger.info(
        "Search URL: %s",
        url,
    )

    # ------------------------------------------------------------
    # robots.txt
    # ------------------------------------------------------------

    robot_parser = get_robot_parser(
        session
    )

    # ------------------------------------------------------------
    # Fetch
    # ------------------------------------------------------------

    html = fetch_search_page(
        url,
        session=session,
        robot_parser=robot_parser,
    )

    # ------------------------------------------------------------
    # Parse
    # ------------------------------------------------------------

    rows = parse_search_page(
        html,
        url,
    )

    # ------------------------------------------------------------
    # Save
    # ------------------------------------------------------------

    save_csv(
        rows
    )

    save_qc_csv(
    rows
)

    # ------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------

    print_statistics(
        rows
    )

    # ------------------------------------------------------------
    # Display first few rows for inspection
    # ------------------------------------------------------------

    print("\nFirst 5 extracted rows:")

    for row in rows[:5]:

        print()
        print(
            f"Plant      : {row['plant_name']}"
        )

        print(
            f"Common     : {row['common_name']}"
        )

        print(
            f"Compound   : {row['compound_name']}"
        )

        print(
            f"CID        : "
            f"{row['pubchem_cid'] or 'MISSING'}"
        )

        print(
            f"Reference  : {row['reference_link']}"
        )

    print()
    print(
        f"CSV: {OUTPUT_CSV}"
    )

    print(
        f"Cache: {cache_path_for_url(url)}"
    )


if __name__ == "__main__":
    main()