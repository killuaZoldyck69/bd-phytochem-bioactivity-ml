"""
bmppd_bulk_scraper.py

Stage 6 -- Bulk BMPPD phytochemical scraper.

Reads the deterministic query mapping from data/processed/mpbd/mpbd_bmppd_query_map.csv,
joins with the frozen MPBD plant index on plant_index, and dispatches BMPPD searches
using bmpdd_query_name while preserving the original frozen MPBD scientific name as
source_query.

Usage (from project root):

    python scrapers\\bmppd_bulk_scraper.py --plants 1-5
    python scrapers\\bmppd_bulk_scraper.py --plants 1-20
    python scrapers\\bmppd_bulk_scraper.py --full
    python scrapers\\bmppd_bulk_scraper.py --cache-only
    python scrapers\\bmppd_bulk_scraper.py --retry-failed

    Flags may be combined, e.g.:
        python scrapers\\bmppd_bulk_scraper.py --plants 1-5 --cache-only

IMPORTANT:
    - Do NOT run --full until staged batches (1-5, 1-20) have been
      reviewed and approved.
    - data/raw/mpbd/mpbd_plant_index.csv is FROZEN and must never be
      modified. It is only ever opened in read mode ("r").
    - This script must never make network requests unless explicitly
      invoked with a run mode that permits live fetching.

Architecture:
    - Pure parsing functions (find_result_tables, parse_result_table,
      identify_quality_flags, build_search_url, etc.) are imported from
      bmppd_scraper.py.
    - All cache/HTTP/robots functions are re-implemented here to use
      scrapers/cache/bmppd/ rather than the pilot's scrapers/cache/.
    - Provenance (plant_index, source_query, bmpdd_query_name, source_page_url,
      scrape_timestamp) is added in this module, not inside the imported parsers.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# sys.path guard -- MUST come before any project-local imports.
#
# Ensures `from bmppd_scraper import ...` resolves correctly when this
# script is invoked as:
#
#     python scrapers/bmppd_bulk_scraper.py ...
#
# from the project root, where Python does NOT automatically add the
# scrapers/ directory to sys.path.
# ---------------------------------------------------------------------------

import sys
from pathlib import Path

_SCRAPERS_DIR = Path(__file__).resolve().parent
if str(_SCRAPERS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRAPERS_DIR))

# ---------------------------------------------------------------------------
# Standard library
# ---------------------------------------------------------------------------

import csv
import hashlib
import logging
import time
from datetime import datetime, timezone
from typing import Any
from urllib.robotparser import RobotFileParser

# ---------------------------------------------------------------------------
# Third-party
# ---------------------------------------------------------------------------

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Import pure parsing functions from the BMPPD pilot scraper.
#
# These functions are pure (no side effects, no dependency on the pilot's
# CACHE_DIR) and are safe to import and call from this module.
#
# NOT imported: fetch_search_page, cache_path_for_url, load_cached_html,
# save_raw_html, record_cache_metadata, get_robot_parser -- those use the
# pilot's CACHE_DIR (scrapers/cache/) and are re-implemented here to use
# scrapers/cache/bmppd/.
# ---------------------------------------------------------------------------

from bmppd_scraper import (  # noqa: E402
    normalize_whitespace,  # noqa: F401 (used internally by imported parsers)
    normalize_header,      # noqa: F401
    identify_field,        # noqa: F401
    extract_cid,           # noqa: F401
    identify_quality_flags,  # noqa: F401
    extract_reference,     # noqa: F401
    find_result_tables,
    parse_result_table,
    build_search_url,
    USER_AGENT,
    REQUEST_DELAY_SECONDS,
    REQUEST_TIMEOUT_SECONDS,
    BASE_URL,
)


# ===========================================================================
# CONFIGURATION
# ===========================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# -- Frozen MPBD inventory (READ-ONLY) ---------------------------------------
#
# Never open this file with mode "w", "a", or "r+".
# The SHA-256 lock in mpbd_normalizer.py catches accidental overwrites,
# but this scraper must enforce read-only access independently.

MPBD_CSV = PROJECT_ROOT / "data" / "raw" / "mpbd" / "mpbd_plant_index.csv"

# -- Deterministic Query Map -------------------------------------------------
QUERY_MAP_CSV = PROJECT_ROOT / "data" / "processed" / "mpbd" / "mpbd_bmppd_query_map.csv"

# -- Bulk BMPPD cache --------------------------------------------------------
#
# Intentionally separate from the pilot's cache at scrapers/cache/.
# Mixing the two would corrupt the pilot's index.csv metadata.

BMPPD_CACHE_DIR = PROJECT_ROOT / "scrapers" / "cache" / "bmppd"
BMPPD_CACHE_INDEX = BMPPD_CACHE_DIR / "index.csv"

CACHE_INDEX_COLUMNS: list[str] = [
    "request_url",
    "cache_file",
    "http_status",
    "retrieved_at",
    "content_hash",
    "content_type",
]

# -- Output files ------------------------------------------------------------

DATA_RAW_BMPPD = PROJECT_ROOT / "data" / "raw" / "bmppd"
OUTPUT_CSV = DATA_RAW_BMPPD / "bmppd_compounds_raw.csv"
FAILED_PLANTS_CSV = DATA_RAW_BMPPD / "bmppd_failed_plants.csv"

DATA_ATTRITION = PROJECT_ROOT / "data" / "attrition"
ATTRITION_CSV = DATA_ATTRITION / "bmppd_attrition.csv"

DATA_QUALITY = PROJECT_ROOT / "data" / "quality"
SUMMARY_MD = DATA_QUALITY / "bmppd_scrape_summary.md"

# -- Column definitions ------------------------------------------------------

OUTPUT_COLUMNS: list[str] = [
    "plant_index",       # 1-based index from MPBD master inventory
    "source_query",      # raw frozen MPBD scientific_name
    "bmpdd_query_name",  # resolved query name dispatched to BMPPD
    "plant_name",        # as returned by BMPPD
    "common_name",       # as returned by BMPPD
    "compound_name",     # phytochemical name
    "pubchem_cid",       # PubChem CID string; empty string if missing
    "reference_link",    # absolute BMPPD reference URL
    "source_page_url",   # BMPPD search URL that produced this row
    "quality_flags",     # semicolon-joined QC flag strings
    "scrape_timestamp",  # ISO-8601 UTC -- original page retrieval time
]

ATTRITION_COLUMNS: list[str] = [
    "run_timestamp",
    "plant_index",
    "source_query",
    "bmpdd_query_name",
    "query_url",
    "cache_status",       # HIT | MISS | FETCH_FAILED
    "http_status",
    "rows_before_dedup",
    "rows_extracted",
    "rows_with_cid",
    "rows_missing_cid",
    "parser_status",      # PASS | ZERO_RESULTS | FETCH_FAILED | PARSE_FAILED
    "error_message",
]

FAILED_PLANTS_COLUMNS: list[str] = [
    "plant_index",
    "source_query",
    "bmpdd_query_name",
    "query_url",
    "failure_type",            # FETCH_FAILED | PARSE_FAILED
    "error_message",
    "last_attempt_timestamp",
]


# ===========================================================================
# LOGGING
# ===========================================================================

def configure_logging() -> None:
    """Configure structured logging to stdout."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


logger = logging.getLogger("bmppd_bulk_scraper")


# ===========================================================================
# CACHE FUNCTIONS
#
# Re-implemented to target BMPPD_CACHE_DIR (scrapers/cache/bmppd/).
# Do NOT import or call the equivalent functions from bmppd_scraper.py.
# ===========================================================================

def cache_path_for_url(url: str) -> Path:
    """
    Map a URL to a deterministic cache filename via SHA-256.
    The same URL always produces the same Path object.
    """
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return BMPPD_CACHE_DIR / f"{digest[:24]}.html"


def load_cached_html(url: str) -> str | None:
    """
    Return cached HTML for a URL if it exists on disk, else None.
    Does not write anything; does not touch BMPPD_CACHE_INDEX.
    """
    path = cache_path_for_url(url)
    if not path.exists():
        return None
    logger.info("CACHE HIT: %s", url)
    return path.read_text(encoding="utf-8", errors="replace")


def save_raw_html(url: str, html: str) -> Path:
    """
    Persist raw HTML to disk immediately after a successful HTTP fetch.
    HTML is always cached before any parsing begins.
    """
    BMPPD_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = cache_path_for_url(url)
    path.write_text(html, encoding="utf-8")
    logger.info("RAW HTML CACHED: %s -> %s", url, path.name)
    return path


def _read_cache_entry(url: str) -> dict[str, str] | None:
    """
    Return the BMPPD_CACHE_INDEX row for a URL, or None if not present.
    Used internally by the duplicate-URL guard and the timestamp lookup.
    """
    if not BMPPD_CACHE_INDEX.exists() or BMPPD_CACHE_INDEX.stat().st_size == 0:
        return None
    with BMPPD_CACHE_INDEX.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("request_url") == url:
                return dict(row)
    return None


def get_cached_retrieved_at(url: str) -> str:
    """
    Look up the original retrieved_at timestamp for a cached page.

    Reads from BMPPD_CACHE_INDEX (written during the live fetch).
    Falls back to the file's mtime for pages cached without an index entry.

    This ensures that scrape_timestamp in output rows reflects when the
    page was fetched from the network, not when it was parsed from disk.
    """
    entry = _read_cache_entry(url)
    if entry and entry.get("retrieved_at"):
        return entry["retrieved_at"]
    # Fallback: file modification time
    path = cache_path_for_url(url)
    if path.exists():
        return datetime.fromtimestamp(
            path.stat().st_mtime, tz=timezone.utc
        ).isoformat()
    return datetime.now(timezone.utc).isoformat()


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
    Append one retrieval event to scrapers/cache/bmppd/index.csv.

    Duplicate-URL guard: if the URL is already present in the index this
    call is a no-op.  Only live HTTP fetches should call this function;
    cache hits must never call it.
    """
    BMPPD_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Duplicate-URL guard -- prevents double-indexing on resumed runs.
    if _read_cache_entry(url) is not None:
        logger.debug("Cache index already has entry for %s -- skipping.", url)
        return

    index_exists = BMPPD_CACHE_INDEX.exists() and BMPPD_CACHE_INDEX.stat().st_size > 0

    with BMPPD_CACHE_INDEX.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CACHE_INDEX_COLUMNS)
        if not index_exists:
            writer.writeheader()
        writer.writerow({
            "request_url": url,
            "cache_file": cache_path.name,
            "http_status": http_status,
            "retrieved_at": retrieved_at,
            "content_hash": content_hash,
            "content_type": content_type,
        })

    logger.info("CACHE METADATA INDEXED: %s", url)


# ===========================================================================
# ROBOTS.TXT
#
# Re-implemented to cache the robots file in BMPPD_CACHE_DIR/robots.txt,
# keeping it separate from the pilot's cached copy.
# ===========================================================================

def get_robot_parser(session: requests.Session) -> RobotFileParser:
    """
    Fetch and parse BMPPD's robots.txt, caching it in BMPPD_CACHE_DIR.

    Makes at most one network request across all runs (on first use).
    Subsequent calls read the locally cached file.
    A 404 response is treated as no restrictions.
    """
    robots_url = f"{BASE_URL}/robots.txt"
    cached_path = BMPPD_CACHE_DIR / "robots.txt"

    BMPPD_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if cached_path.exists():
        robots_text = cached_path.read_text(encoding="utf-8", errors="replace")
        logger.info("ROBOTS CACHE HIT: %s", robots_url)
    else:
        logger.info("FETCH robots.txt: %s", robots_url)
        time.sleep(REQUEST_DELAY_SECONDS)

        try:
            response = session.get(robots_url, timeout=REQUEST_TIMEOUT_SECONDS)
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Could not retrieve robots.txt: {exc}"
            ) from exc

        if response.status_code == 404:
            robots_text = "# 404 -- no robots.txt; all paths assumed allowed\n"
            logger.info("robots.txt returned 404 -- treating all paths as allowed.")
        else:
            response.raise_for_status()
            robots_text = response.text

        cached_path.write_text(robots_text, encoding="utf-8")
        logger.info("CACHED robots.txt -> %s", cached_path)

    parser = RobotFileParser()
    parser.set_url(robots_url)
    parser.parse(robots_text.splitlines())
    return parser


# ===========================================================================
# HTTP FETCH
# ===========================================================================

def fetch_query_page(
    url: str,
    *,
    session: requests.Session,
    robot_parser: RobotFileParser,
) -> tuple[str, str, str, int | None]:
    """
    Fetch one BMPPD search result page.

    Returns:
        (html, cache_status, retrieved_at, http_status)
        cache_status : "HIT"  -- served from disk; no network call made
                       "MISS" -- live HTTP fetch; HTML now persisted to cache
        retrieved_at : ISO-8601 UTC string of original retrieval time
        http_status  : integer for live fetches; None for cache hits

    Raises:
        PermissionError      -- robots.txt disallows the URL
        requests.HTTPError   -- server responded with 4xx or 5xx
        RuntimeError         -- network-level error (timeout, DNS, etc.)

    Rate-limiting:
        time.sleep(REQUEST_DELAY_SECONDS) is called before every live
        network request. Cache hits do NOT incur any sleep.
    """
    # -- Cache hit ------------------------------------------------------------
    cached = load_cached_html(url)
    if cached is not None:
        retrieved_at = get_cached_retrieved_at(url)
        return cached, "HIT", retrieved_at, None

    # -- robots.txt compliance ------------------------------------------------
    if not robot_parser.can_fetch(USER_AGENT, url):
        raise PermissionError(f"robots.txt disallows access to: {url}")

    # -- Polite delay ---------------------------------------------------------
    logger.info(
        "Waiting %.1f seconds before network request...",
        REQUEST_DELAY_SECONDS,
    )
    time.sleep(REQUEST_DELAY_SECONDS)

    # -- Live fetch -----------------------------------------------------------
    logger.info("FETCH: %s", url)
    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        raise RuntimeError(f"Network error for {url}: {exc}") from exc

    logger.info("HTTP %s: %s", response.status_code, url)
    response.raise_for_status()  # raises requests.HTTPError for 4xx/5xx

    # -- Cache immediately (before any parsing) --------------------------------
    cache_path = save_raw_html(url, response.text)
    content_hash = hashlib.sha256(response.text.encode("utf-8")).hexdigest()
    retrieved_at = datetime.now(timezone.utc).isoformat()
    content_type = response.headers.get("Content-Type", "")

    record_cache_metadata(
        url=url,
        cache_path=cache_path,
        http_status=response.status_code,
        retrieved_at=retrieved_at,
        content_hash=content_hash,
        content_type=content_type,
    )

    return response.text, "MISS", retrieved_at, response.status_code


# ===========================================================================
# PARSING
# ===========================================================================

def parse_compound_rows(
    html: str,
    source_url: str,
    source_query: str,
    retrieved_at: str,
    plant_index: int | str | None = None,
    bmpdd_query_name: str | None = None,
) -> tuple[int, list[dict[str, str]]]:
    """
    Parse BMPPD HTML into compound rows for one plant query.

    Uses find_result_tables and parse_result_table imported from
    bmppd_scraper.py.  Does NOT call parse_search_page (which calls
    datetime.now() internally -- incorrect for cache hits).

    Provenance fields (plant_index, source_query, bmpdd_query_name,
    source_page_url, scrape_timestamp) are added here so that
    scrape_timestamp reflects the original retrieval time, not the
    current processing time.

    quality_flags is serialized from list[str] to a semicolon-joined
    string before being written to the output CSV.

    Returns:
        (rows_before_dedup, unique_rows)
        rows_before_dedup : raw row count before within-query dedup
        unique_rows       : deduplicated rows with full provenance
    """
    soup = BeautifulSoup(html, "html.parser")
    tables = find_result_tables(soup)

    if not tables:
        return 0, []

    # Collect raw rows from all result tables on this page.
    all_rows: list[dict[str, Any]] = []
    for table in tables:
        all_rows.extend(parse_result_table(table))

    rows_before_dedup = len(all_rows)

    # Within-query deduplication -- same key logic as
    # bmppd_scraper.parse_search_page.
    unique_rows: list[dict[str, str]] = []
    seen: set[tuple[str, ...]] = set()

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

        # Serialize quality_flags: parse_result_table returns list[str].
        flags = row.get("quality_flags", [])
        row["quality_flags"] = (
            ";".join(flags) if isinstance(flags, list) else str(flags)
        )

        # Provenance -- added here, not inside parse_result_table.
        row["plant_index"] = str(plant_index) if plant_index is not None else ""
        row["source_query"] = source_query
        row["bmpdd_query_name"] = bmpdd_query_name if bmpdd_query_name else source_query
        row["source_page_url"] = source_url
        row["scrape_timestamp"] = retrieved_at

        unique_rows.append(row)

    return rows_before_dedup, unique_rows


# ===========================================================================
# INPUT -- FROZEN PLANT INVENTORY & DETERMINISTIC QUERY MAP
# ===========================================================================

def load_plant_inventory() -> list[str]:
    """
    Load the scientific_name column from the frozen MPBD plant index.

    Opened strictly in read mode ("r").  Preserves the exact original
    capitalisation and spelling of every raw scientific_name -- no
    normalisation, lowercasing, or botanical correction is applied.

    Returns a list of 916 strings (one per MPBD record).
    """
    names: list[str] = []
    with MPBD_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            names.append(row["scientific_name"])
    logger.info(
        "Loaded %d plant names from frozen inventory: %s",
        len(names),
        MPBD_CSV,
    )
    return names


def load_query_map() -> dict[int, dict[str, str]]:
    """
    Load the deterministic query mapping from
    data/processed/mpbd/mpbd_bmppd_query_map.csv.

    Keyed by integer plant_index (1 to 916).
    """
    if not QUERY_MAP_CSV.exists():
        raise FileNotFoundError(
            f"Deterministic query map not found: {QUERY_MAP_CSV}"
        )
    mapping: dict[int, dict[str, str]] = {}
    with QUERY_MAP_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            idx = int(row["plant_index"])
            mapping[idx] = row
    logger.info(
        "Loaded %d query mappings from %s", len(mapping), QUERY_MAP_CSV
    )
    return mapping


def load_resolved_plant_inventory() -> list[dict[str, Any]]:
    """
    Load the frozen MPBD plant index and join with the deterministic query map
    using plant_index as the join key.

    Returns a list of 916 dicts:
        {
            "plant_index": int,
            "source_query": str,       # raw frozen MPBD scientific name
            "bmpdd_query_name": str,   # deterministic resolved query name
            "query_status": str,       # READY | MANUAL_REVIEW
        }
    """
    raw_names = load_plant_inventory()
    query_map = load_query_map()

    joined: list[dict[str, Any]] = []
    for i, raw_name in enumerate(raw_names, start=1):
        q_entry = query_map.get(i)
        if not q_entry:
            raise KeyError(f"Missing query map entry for plant_index={i}")

        map_raw_name = q_entry.get("raw_mpbd_name", "")
        if map_raw_name != raw_name:
            raise ValueError(
                f"Mismatch at plant_index={i}: MPBD has '{raw_name}' but "
                f"query map has '{map_raw_name}'"
            )

        bmpdd_query = q_entry.get("bmpdd_query_name", "").strip()
        if not bmpdd_query:
            raise ValueError(f"Empty bmpdd_query_name at plant_index={i}")

        joined.append({
            "plant_index": i,
            "source_query": raw_name,
            "bmpdd_query_name": bmpdd_query,
            "query_status": q_entry.get("query_status", "READY"),
        })

    logger.info(
        "Successfully joined %d plants on plant_index with deterministic query map.",
        len(joined),
    )
    return joined


# ===========================================================================
# OUTPUT -- COMPOUND CSV
# ===========================================================================

def load_completed_plants() -> tuple[set[int], set[str]]:
    """
    Return sets of (completed_plant_indices, completed_source_queries) from OUTPUT_CSV.

    Used for resume protection: any plant already recorded in OUTPUT_CSV
    is silently skipped.
    """
    indices: set[int] = set()
    queries: set[str] = set()
    if not OUTPUT_CSV.exists() or OUTPUT_CSV.stat().st_size == 0:
        return indices, queries
    with OUTPUT_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            idx_str = row.get("plant_index", "").strip()
            if idx_str.isdigit():
                indices.add(int(idx_str))
            sq = row.get("source_query", "").strip()
            if sq:
                queries.add(sq)
    logger.info(
        "Resume: %d plant_index values (%d distinct queries) already in %s",
        len(indices),
        len(queries),
        OUTPUT_CSV,
    )
    return indices, queries


def load_completed_queries() -> set[str]:
    """Return set of source_query strings already recorded in OUTPUT_CSV."""
    _, queries = load_completed_plants()
    return queries


def append_compound_rows(rows: list[dict[str, Any]]) -> None:
    """
    Append compound rows to the consolidated output CSV.
    Creates the file and writes the header on the first call.
    """
    if not rows:
        return
    DATA_RAW_BMPPD.mkdir(parents=True, exist_ok=True)
    file_exists = OUTPUT_CSV.exists() and OUTPUT_CSV.stat().st_size > 0
    with OUTPUT_CSV.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=OUTPUT_COLUMNS,
            extrasaction="ignore",
        )
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


# ===========================================================================
# OUTPUT -- ATTRITION LOG
# ===========================================================================

def append_attrition_records(records: list[dict[str, Any]]) -> None:
    """
    Append per-plant attrition records to ATTRITION_CSV.

    Records are accumulated in memory during a run and flushed once at
    the end to avoid excessive file open/close operations.
    """
    if not records:
        return
    DATA_ATTRITION.mkdir(parents=True, exist_ok=True)
    file_exists = ATTRITION_CSV.exists() and ATTRITION_CSV.stat().st_size > 0
    if file_exists:
        # Check if existing header needs migration to include bmpdd_query_name
        with ATTRITION_CSV.open("r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, [])
        if header != ATTRITION_COLUMNS:
            with ATTRITION_CSV.open("r", newline="", encoding="utf-8") as f:
                dict_reader = csv.DictReader(f)
                old_records = list(dict_reader)
            for r in old_records:
                if "bmpdd_query_name" not in r:
                    r["bmpdd_query_name"] = r.get("source_query", "")
            with ATTRITION_CSV.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f, fieldnames=ATTRITION_COLUMNS, extrasaction="ignore"
                )
                writer.writeheader()
                writer.writerows(old_records)

    file_exists = ATTRITION_CSV.exists() and ATTRITION_CSV.stat().st_size > 0
    with ATTRITION_CSV.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=ATTRITION_COLUMNS, extrasaction="ignore"
        )
        if not file_exists:
            writer.writeheader()
        for rec in records:
            writer.writerow(rec)
    logger.info(
        "Attrition: %d records written to %s", len(records), ATTRITION_CSV
    )


# ===========================================================================
# OUTPUT -- FAILED PLANTS
# ===========================================================================

def load_failed_plants() -> list[dict[str, str]]:
    """Return all records from bmppd_failed_plants.csv, or [] if absent."""
    if not FAILED_PLANTS_CSV.exists() or FAILED_PLANTS_CSV.stat().st_size == 0:
        return []
    with FAILED_PLANTS_CSV.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_failed_plants(records: list[dict[str, Any]]) -> None:
    """
    Overwrite bmppd_failed_plants.csv with the supplied records.

    Called at the end of EVERY run (normal and retry) to reflect the
    CURRENT failure state, not a historical accumulation.  Plants that
    succeeded this run are removed; newly failed plants are added.
    """
    DATA_RAW_BMPPD.mkdir(parents=True, exist_ok=True)
    with FAILED_PLANTS_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FAILED_PLANTS_COLUMNS)
        writer.writeheader()
        if records:
            writer.writerows(records)
    logger.info(
        "Failed-plants file updated: %d remaining failures -> %s",
        len(records),
        FAILED_PLANTS_CSV,
    )


# ===========================================================================
# SUMMARY REPORT
# ===========================================================================

def write_summary(
    run_timestamp: str,
    mode: str,
    plant_range: str,
    stats: dict[str, int],
) -> None:
    """Write the post-run markdown summary to data/quality/bmppd_scrape_summary.md."""
    DATA_QUALITY.mkdir(parents=True, exist_ok=True)

    total_rows = stats.get("total_rows", 0)
    rows_missing = stats.get("rows_missing_cid", 0)
    pct_missing = (rows_missing / total_rows * 100) if total_rows > 0 else 0.0

    lines: list[str] = [
        "# BMPPD Stage 6 -- Bulk Scrape Summary",
        "",
        f"**Stage**: 6 -- Bulk BMPPD Phytochemical Scraping  ",
        f"**Run Mode**: `{mode}`  ",
        f"**Plant Range**: `{plant_range}`  ",
        f"**Run Timestamp**: `{run_timestamp}`  ",
        f"**Report Generated**: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "---",
        "",
        "## Run Statistics",
        "",
        "| Metric | Value |",
        "| :--- | :--- |",
        f"| **Plants attempted** | {stats.get('plants_attempted', 0)} |",
        f"| **Successful queries (>=1 result)** | {stats.get('plants_successful', 0)} |",
        f"| **Zero-result queries** | {stats.get('plants_zero_results', 0)} |",
        f"| **Fetch failures** | {stats.get('plants_fetch_failed', 0)} |",
        f"| **Parse failures** | {stats.get('plants_parse_failed', 0)} |",
        f"| **Total compound rows extracted** | {total_rows} |",
        f"| **Rows with valid PubChem CID** | {stats.get('rows_with_cid', 0)} |",
        f"| **Rows missing CID** | {rows_missing} ({pct_missing:.2f}%) |",
        f"| **Cache hits** | {stats.get('cache_hits', 0)} |",
        f"| **Live web fetches** | {stats.get('web_fetches', 0)} |",
        "",
        "---",
        "",
        "## Output Files",
        "",
        "- `data/raw/bmppd/bmppd_compounds_raw.csv` -- consolidated compound rows",
        "- `data/attrition/bmppd_attrition.csv` -- per-plant audit log",
        "- `data/raw/bmppd/bmppd_failed_plants.csv` -- plants that errored",
        "- `scrapers/cache/bmppd/` -- cached HTML responses + index.csv",
    ]

    with SUMMARY_MD.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    logger.info("Summary report written: %s", SUMMARY_MD)


def print_console_summary(
    stats: dict[str, int],
    mode: str,
    plant_range: str,
) -> None:
    """Print the run summary table to stdout."""
    total_rows = stats.get("total_rows", 0)
    rows_missing = stats.get("rows_missing_cid", 0)
    pct_missing = (rows_missing / total_rows * 100) if total_rows > 0 else 0.0

    print()
    print("=" * 64)
    print("BMPPD STAGE 6 -- RUN SUMMARY")
    print("=" * 64)
    print(f"Mode                       : {mode}")
    print(f"Plant range                : {plant_range}")
    print(f"Plants attempted           : {stats.get('plants_attempted', 0)}")
    print(f"Successful queries         : {stats.get('plants_successful', 0)}")
    print(f"Zero-result queries        : {stats.get('plants_zero_results', 0)}")
    print(f"Fetch failures             : {stats.get('plants_fetch_failed', 0)}")
    print(f"Parse failures             : {stats.get('plants_parse_failed', 0)}")
    print(f"Total compound rows        : {total_rows}")
    print(f"Rows with valid CID        : {stats.get('rows_with_cid', 0)}")
    print(f"Rows missing CID           : {rows_missing} ({pct_missing:.2f}%)")
    print(f"Cache hits                 : {stats.get('cache_hits', 0)}")
    print(f"Live web fetches           : {stats.get('web_fetches', 0)}")
    print("=" * 64)


# ===========================================================================
# CACHE-ONLY DRY RUN
# ===========================================================================

def run_cache_only(
    indexed_plants: list[dict[str, Any]],
    plant_range: str,
) -> None:
    """
    Inspect cache state without making any network requests.

    Reports which plants are already cached (fast resume or
    --cache-only parsing) and which would require a live fetch.
    Never calls time.sleep(); never opens a socket.
    """
    cached_list: list[dict[str, Any]] = []
    not_cached_list: list[dict[str, Any]] = []

    for plant in indexed_plants:
        url = build_search_url(plant["bmpdd_query_name"])
        if cache_path_for_url(url).exists():
            cached_list.append(plant)
        else:
            not_cached_list.append(plant)

    print()
    print("=" * 64)
    print("BMPPD STAGE 6 -- CACHE-ONLY DRY RUN")
    print("=" * 64)
    print(f"Plant range          : {plant_range}")
    print(f"Plants in scope      : {len(indexed_plants)}")
    print(f"Already cached       : {len(cached_list)}")
    print(f"Not yet cached       : {len(not_cached_list)}")
    print(f"Network requests     : 0")
    print("=" * 64)

    if not_cached_list:
        show = min(len(not_cached_list), 20)
        print(f"\nPlants NOT yet cached (first {show} of {len(not_cached_list)}):")
        for p in not_cached_list[:show]:
            print(f"  [{p['plant_index']:>4}] {p['source_query']} -> {p['bmpdd_query_name']}")
        if len(not_cached_list) > show:
            print(f"  ... and {len(not_cached_list) - show} more")

    if cached_list:
        show = min(len(cached_list), 5)
        print(f"\nPlants already cached ({len(cached_list)} total):")
        for p in cached_list[:show]:
            print(f"  [{p['plant_index']:>4}] {p['source_query']} -> {p['bmpdd_query_name']}")
        if len(cached_list) > show:
            print(f"  ... and {len(cached_list) - show} more")


# ===========================================================================
# RECORD BUILDERS
# ===========================================================================

def _make_attrition_record(
    run_timestamp: str,
    plant_index: int,
    source_query: str,
    bmpdd_query_name: str,
    query_url: str,
    cache_status: str,
    http_status: Any,
    rows_before_dedup: int,
    rows_extracted: int,
    rows_with_cid: int,
    rows_missing_cid: int,
    parser_status: str,
    error_message: str,
) -> dict[str, Any]:
    """Construct a single attrition log record dict."""
    return {
        "run_timestamp": run_timestamp,
        "plant_index": plant_index,
        "source_query": source_query,
        "bmpdd_query_name": bmpdd_query_name,
        "query_url": query_url,
        "cache_status": cache_status,
        "http_status": http_status if http_status is not None else "",
        "rows_before_dedup": rows_before_dedup,
        "rows_extracted": rows_extracted,
        "rows_with_cid": rows_with_cid,
        "rows_missing_cid": rows_missing_cid,
        "parser_status": parser_status,
        "error_message": error_message,
    }


def _make_failed_plant_record(
    plant_index: int,
    source_query: str,
    bmpdd_query_name: str,
    query_url: str,
    failure_type: str,
    error_message: str,
    last_attempt_timestamp: str,
) -> dict[str, str]:
    """Construct a failed-plant record dict."""
    return {
        "plant_index": str(plant_index),
        "source_query": source_query,
        "bmpdd_query_name": bmpdd_query_name,
        "query_url": query_url,
        "failure_type": failure_type,
        "error_message": error_message,
        "last_attempt_timestamp": last_attempt_timestamp,
    }


# ===========================================================================
# MAIN SCRAPE ENGINE
# ===========================================================================

def run_scrape(
    all_plants: list[dict[str, Any]] | list[str] | None = None,
    start_idx: int = 0,
    end_idx: int = -1,
    *,
    cache_only: bool = False,
    retry_failed: bool = False,
    all_plant_names: list[str] | None = None,
) -> None:
    """
    Execute Stage 6 for a contiguous slice of the plant inventory.

    Args:
        all_plants      : list of resolved plant dicts, or legacy list of names.
        start_idx       : 0-based inclusive start of the target slice.
        end_idx         : 0-based exclusive end of the target slice.
        cache_only      : inspect cache state only; zero network requests.
        retry_failed    : process only plants in bmppd_failed_plants.csv.
        all_plant_names : legacy alias for all_plants.

    Resume behaviour:
        load_completed_plants() reads OUTPUT_CSV at startup. Any plant
        whose plant_index or source_query already appears there is silently
        skipped. completed_indices and completed_queries are updated in
        memory as each plant succeeds.

    Failure-state management (end of run):
        merged = existing_failures
        merged.update(new_failures)     -- update with latest timestamps
        merged.discard(newly_succeeded) -- remove plants that worked
        save_failed_plants(merged)      -- overwrite the file
    """
    if all_plants is None:
        if all_plant_names is not None:
            all_plants = all_plant_names
        else:
            all_plants = load_resolved_plant_inventory()

    if all_plants and isinstance(all_plants[0], str):
        # Legacy invocation where only strings were passed: join with query map
        raw_names: list[str] = all_plants  # type: ignore
        query_map = load_query_map()
        resolved_plants: list[dict[str, Any]] = []
        for i, name in enumerate(raw_names, start=1):
            q_entry = query_map.get(i, {})
            resolved_plants.append({
                "plant_index": i,
                "source_query": name,
                "bmpdd_query_name": q_entry.get("bmpdd_query_name", name),
                "query_status": q_entry.get("query_status", "READY"),
            })
        indexed_plants_all = resolved_plants
    else:
        indexed_plants_all = all_plants  # type: ignore

    total_inventory = len(indexed_plants_all)
    if end_idx == -1 or end_idx > total_inventory:
        end_idx = total_inventory

    plant_range = f"{start_idx + 1}-{end_idx}"
    indexed_plants: list[dict[str, Any]] = indexed_plants_all[start_idx:end_idx]

    # -- Retry-failed filter --------------------------------------------------
    if retry_failed:
        failed_records = load_failed_plants()
        failed_indices = {
            int(r["plant_index"])
            for r in failed_records
            if r.get("plant_index", "").isdigit()
        }
        failed_queries = {
            r["source_query"].strip()
            for r in failed_records
            if r.get("source_query")
        }
        if not failed_indices and not failed_queries:
            logger.info(
                "--retry-failed: bmppd_failed_plants.csv is empty or absent. "
                "Nothing to retry."
            )
            return
        indexed_plants = [
            p for p in indexed_plants
            if p["plant_index"] in failed_indices or p["source_query"] in failed_queries
        ]
        logger.info("--retry-failed: %d plants in scope.", len(indexed_plants))

    # -- Cache-only dry run ---------------------------------------------------
    if cache_only:
        run_cache_only(indexed_plants, plant_range)
        return

    # -- Run mode label -------------------------------------------------------
    if retry_failed:
        mode = "retry-failed"
    elif start_idx == 0 and end_idx == total_inventory:
        mode = "full"
    else:
        mode = f"plants {start_idx + 1}-{end_idx}"

    run_timestamp = datetime.now(timezone.utc).isoformat()
    logger.info(
        "Stage 6 starting -- mode=%s  range=%s  timestamp=%s",
        mode, plant_range, run_timestamp,
    )

    # -- Resume protection ----------------------------------------------------
    completed_indices, completed_queries = load_completed_plants()

    # -- Failure-state management ---------------------------------------------
    existing_failures: dict[str, dict[str, str]] = {
        r.get("plant_index", r.get("source_query", "")): r
        for r in load_failed_plants()
        if r.get("plant_index") or r.get("source_query")
    }
    newly_succeeded: set[str] = set()
    new_failures: dict[str, dict[str, str]] = {}

    # -- HTTP session ---------------------------------------------------------
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    })

    robot_parser = get_robot_parser(session)

    # -- Statistics -----------------------------------------------------------
    stats: dict[str, int] = {
        "plants_attempted": 0,
        "plants_successful": 0,
        "plants_zero_results": 0,
        "plants_fetch_failed": 0,
        "plants_parse_failed": 0,
        "total_rows": 0,
        "rows_with_cid": 0,
        "rows_missing_cid": 0,
        "cache_hits": 0,
        "web_fetches": 0,
    }

    # Attrition records are collected in memory and flushed once at the end.
    attrition_records: list[dict[str, Any]] = []

    total_in_scope = len(indexed_plants)

    # =========================================================================
    # MAIN LOOP
    # =========================================================================

    for loop_pos, plant in enumerate(indexed_plants, start=1):
        plant_index = plant["plant_index"]
        source_query = plant["source_query"]
        bmpdd_query_name = plant["bmpdd_query_name"]

        # -- Resume skip -------------------------------------------------------
        if (plant_index in completed_indices or source_query in completed_queries) and not retry_failed:
            logger.info(
                "[%d/%d] SKIP (already completed): [%d] %s -> %s",
                loop_pos, total_in_scope, plant_index, source_query, bmpdd_query_name,
            )
            continue

        stats["plants_attempted"] += 1
        url = build_search_url(bmpdd_query_name)

        logger.info(
            "[%d/%d] plant_index=%d | source_query='%s' -> bmpdd_query_name='%s'",
            loop_pos, total_in_scope, plant_index, source_query, bmpdd_query_name,
        )
        logger.info("  url: %s", url)

        # =====================================================================
        # STEP 1 -- FETCH
        # =====================================================================

        html: str | None = None
        cache_status = "FETCH_FAILED"
        retrieved_at = run_timestamp
        http_status_val: Any = ""

        try:
            html, cache_status, retrieved_at, http_status_raw = fetch_query_page(
                url,
                session=session,
                robot_parser=robot_parser,
            )
            # At this point cache_status is "HIT" or "MISS".
            http_status_val = http_status_raw if http_status_raw is not None else 200

            if cache_status == "HIT":
                stats["cache_hits"] += 1
                logger.info(
                    "  cache_status=HIT  retrieved_at=%s", retrieved_at
                )
            else:
                stats["web_fetches"] += 1
                logger.info(
                    "  cache_status=MISS  http_status=%s", http_status_val
                )

        except requests.HTTPError as exc:
            # Server responded but with 4xx/5xx.
            http_status_val = (
                exc.response.status_code
                if exc.response is not None
                else ""
            )
            error_msg = str(exc)
            logger.error(
                "  FETCH_FAILED (HTTP %s): %s", http_status_val, error_msg
            )
            attrition_records.append(_make_attrition_record(
                run_timestamp, plant_index, source_query, bmpdd_query_name, url,
                "FETCH_FAILED", http_status_val,
                0, 0, 0, 0, "FETCH_FAILED", error_msg,
            ))
            new_failures[str(plant_index)] = _make_failed_plant_record(
                plant_index, source_query, bmpdd_query_name, url,
                "FETCH_FAILED", error_msg, run_timestamp,
            )
            stats["plants_fetch_failed"] += 1
            continue

        except (RuntimeError, PermissionError) as exc:
            # Network error or robots.txt block -- no HTTP response.
            error_msg = str(exc)
            logger.error("  FETCH_FAILED: %s", error_msg)
            attrition_records.append(_make_attrition_record(
                run_timestamp, plant_index, source_query, bmpdd_query_name, url,
                "FETCH_FAILED", "",
                0, 0, 0, 0, "FETCH_FAILED", error_msg,
            ))
            new_failures[str(plant_index)] = _make_failed_plant_record(
                plant_index, source_query, bmpdd_query_name, url,
                "FETCH_FAILED", error_msg, run_timestamp,
            )
            stats["plants_fetch_failed"] += 1
            continue

        # =====================================================================
        # STEP 2 -- PARSE
        # =====================================================================

        rows_before_dedup = 0
        unique_rows: list[dict[str, str]] = []

        try:
            rows_before_dedup, unique_rows = parse_compound_rows(
                html,
                url,
                source_query,
                retrieved_at,
                plant_index=plant_index,
                bmpdd_query_name=bmpdd_query_name,
            )
        except Exception as exc:
            error_msg = str(exc)
            logger.error("  PARSE_FAILED: %s", error_msg)
            attrition_records.append(_make_attrition_record(
                run_timestamp, plant_index, source_query, bmpdd_query_name, url,
                cache_status, http_status_val,
                0, 0, 0, 0, "PARSE_FAILED", error_msg,
            ))
            new_failures[str(plant_index)] = _make_failed_plant_record(
                plant_index, source_query, bmpdd_query_name, url,
                "PARSE_FAILED", error_msg, run_timestamp,
            )
            stats["plants_parse_failed"] += 1
            continue

        # =====================================================================
        # STEP 3 -- CLASSIFY AND RECORD
        # =====================================================================

        n_with_cid = sum(1 for r in unique_rows if r.get("pubchem_cid"))
        n_missing_cid = len(unique_rows) - n_with_cid
        parser_status = "PASS" if unique_rows else "ZERO_RESULTS"

        attrition_records.append(_make_attrition_record(
            run_timestamp, plant_index, source_query, bmpdd_query_name, url,
            cache_status, http_status_val,
            rows_before_dedup, len(unique_rows),
            n_with_cid, n_missing_cid,
            parser_status, "",
        ))

        if unique_rows:
            # Write compound rows; update in-memory resume set immediately.
            append_compound_rows(unique_rows)
            completed_indices.add(plant_index)
            completed_queries.add(source_query)
            newly_succeeded.add(str(plant_index))
            stats["plants_successful"] += 1
            stats["total_rows"] += len(unique_rows)
            stats["rows_with_cid"] += n_with_cid
            stats["rows_missing_cid"] += n_missing_cid
        else:
            # ZERO_RESULTS is a valid outcome.
            # Do NOT add to failed_plants or retry queue.
            stats["plants_zero_results"] += 1
            newly_succeeded.add(str(plant_index))
            logger.info("  ZERO_RESULTS -- BMPPD has no entries for this plant.")

        logger.info(
            "  parser_status=%s  rows=%d  with_cid=%d  "
            "missing_cid=%d  rows_before_dedup=%d",
            parser_status, len(unique_rows), n_with_cid,
            n_missing_cid, rows_before_dedup,
        )

    # =========================================================================
    # POST-LOOP -- FLUSH OUTPUTS
    # =========================================================================

    # -- Flush attrition log --------------------------------------------------
    if attrition_records:
        append_attrition_records(attrition_records)

    # -- Update failed-plants file --------------------------------------------
    #
    # Merge strategy (same for normal runs and --retry-failed):
    #   1. Start from existing failures
    #   2. Overwrite/add entries from this run's new_failures
    #      (updates last_attempt_timestamp for still-failing plants)
    #   3. Remove plants that succeeded in this run
    #
    merged_failures = dict(existing_failures)
    merged_failures.update(new_failures)
    for p_idx in newly_succeeded:
        merged_failures.pop(p_idx, None)

    save_failed_plants(list(merged_failures.values()))

    # -- Summary --------------------------------------------------------------
    write_summary(run_timestamp, mode, plant_range, stats)
    print_console_summary(stats, mode, plant_range)


# ===========================================================================
# CLI ARGUMENT PARSING
# ===========================================================================

def _parse_cli() -> tuple[int, int, bool, bool, bool]:
    """
    Parse sys.argv and return execution parameters.

    Returns:
        (start_1, end_1, is_full, is_cache_only, is_retry)
        start_1 : 1-based inclusive start plant number
        end_1   : 1-based inclusive end plant number (-1 = sentinel for all)
        is_full : True if --full is present
        is_cache_only : True if --cache-only is present
        is_retry : True if --retry-failed is present
    """
    argv = sys.argv[1:]

    is_full = "--full" in argv
    is_cache_only = "--cache-only" in argv
    is_retry = "--retry-failed" in argv

    # Extract --plants argument (supports --plants 1-5 and --plants=1-5).
    plants_arg: str | None = None
    for i, arg in enumerate(argv):
        if arg.startswith("--plants="):
            plants_arg = arg.split("=", 1)[1]
            break
        if arg == "--plants" and i + 1 < len(argv):
            plants_arg = argv[i + 1]
            break

    # Require at least one primary mode flag.
    mode_flags = int(is_full) + int(is_cache_only) + int(plants_arg is not None)
    if mode_flags == 0 and not is_retry:
        print(
            "\nUsage:\n"
            "  python scrapers\\bmppd_bulk_scraper.py --plants 1-5\n"
            "  python scrapers\\bmppd_bulk_scraper.py --plants 1-20\n"
            "  python scrapers\\bmppd_bulk_scraper.py --full\n"
            "  python scrapers\\bmppd_bulk_scraper.py --cache-only\n"
            "  python scrapers\\bmppd_bulk_scraper.py --retry-failed\n"
            "\nModifiers (may be combined with any of the above):\n"
            "  --cache-only   inspect cache only; no network requests\n"
        )
        sys.exit(1)

    # Parse the --plants range into 1-based inclusive bounds.
    start_1: int = 1
    end_1: int = -1  # sentinel: resolved in main() from inventory size

    if plants_arg is not None:
        parts = plants_arg.split("-", 1)
        try:
            start_1 = int(parts[0].strip())
            end_1 = int(parts[1].strip()) if len(parts) > 1 else start_1
        except (ValueError, IndexError):
            print(f"Error: invalid --plants argument: {plants_arg!r}")
            sys.exit(1)

    return start_1, end_1, is_full, is_cache_only, is_retry


# ===========================================================================
# ENTRY POINT
# ===========================================================================

def main() -> None:
    configure_logging()

    start_1, end_1, is_full, is_cache_only, is_retry = _parse_cli()

    # Load the frozen plant inventory joined with the deterministic query map
    all_plants = load_resolved_plant_inventory()
    n = len(all_plants)

    # Resolve the 0-based slice indices.
    if is_full or is_retry:
        start_idx = 0
        end_idx = n
    elif end_1 == -1:
        start_idx = 0
        end_idx = n
    else:
        start_idx = max(0, start_1 - 1)
        end_idx = min(n, end_1)
        if start_idx >= end_idx:
            print(
                f"Error: --plants {start_1}-{end_1} resolves to an empty range "
                f"(inventory has {n} records, valid range 1-{n})."
            )
            sys.exit(1)

    run_scrape(
        all_plants=all_plants,
        start_idx=start_idx,
        end_idx=end_idx,
        cache_only=is_cache_only,
        retry_failed=is_retry,
    )


if __name__ == "__main__":
    main()
