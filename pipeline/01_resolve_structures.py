#!/usr/bin/env python3
"""
Stage 7A - Pipeline Step 1: Resolve Chemical Structures from PubChem PUG-REST (Production)

Reads:
  - data/raw/mpbd/mpbd_plant_index.csv (Frozen master; verified against manifest)
  - data/raw/bmppd/bmppd_compounds_raw.csv (Consolidated plant-compound pairs)

Produces:
  - data/processed/compounds/compound_structures_resolved.csv
  - data/processed/compounds/name_multiple_matches_review.csv
  - data/attrition/compound_resolution_attrition.csv
  - data/cache/pubchem/ (Raw JSON responses for CIDs and names)
  - data/quality/compound_resolution.log
  - data/quality/stage7a_resolution_report.md

Rules & Safeguards:
  - Verifies SHA-256 of master MPBD index at start and end.
  - Encoding-loss check: If compound_name_original contains literal '?', U+FFFD, or mojibake,
    it is classified as 'skipped_encoding_loss' and NOT queried against PubChem.
  - Non-specific filter: Identifies and skips mixtures/extracts (essential oil, extract, unknown, etc.).
  - Conservative name cleaning: only whitespace trimming and unicode quote normalization.
  - NEVER strips or alters stereo/locant prefixes (e.g. (+)-, (-)-, alpha-, beta-).
  - Strict match policy: Exactly 1 CID -> exact_match; >1 CIDs -> multiple_matches (needs_review);
    0 CIDs -> no_match (404); Transient network errors -> fetch_error (retried up to 3 passes).
  - Evaluates candidate InChIKey connectivity layer (first 14 chars) for all multiple-match items.
  - Analyzes structural categories for all no_match items.
  - Caches all raw API responses to disk so reruns make 0 network calls.
  - Rate limits requests (<= 4 req/sec) with exponential backoff on HTTP 429/503.
"""

import argparse
from collections import Counter, deque
import csv
import datetime
import hashlib
import json
import logging
import os
from pathlib import Path
import random
import re
import sys
import time
import urllib.parse
from typing import Dict, List, Optional, Set, Tuple

import requests

# ---------------------------------------------------------------------------
# Constants & Configuration
# ---------------------------------------------------------------------------
USER_AGENT = "bmppd-thesis/1.0 (academic research; contact: thesis-pipeline@local)"
PUG_REST_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
REQUEST_DELAY_SEC = 0.25  # Polite delay between network requests (<= 4 req/s)
MAX_RETRIES = 4
BATCH_CID_SIZE = 100
MAX_ERROR_RATE_WINDOW = 200
MAX_ERROR_RATE_THRESHOLD = 0.05  # 5%

NON_SPECIFIC_PATTERNS = [
    r'^(?:essential\s+)?oil(?:s)?$',
    r'.*\bessential\s+oil(?:s)?\b.*',
    r'.*\bextract(?:s)?\b.*',
    r'.*\bunknown\b.*',
    r'.*\bunidentified\b.*',
    r'.*\bfatty\s+acid(?:s)?\b.*',
    r'.*\bfraction(?:s)?\b.*',
    r'.*\bcrude\b.*',
    r'^(?:total\s+)?(?:alkaloids|flavonoids|saponins|tannins|phenolics|terpenoids|glycosides)$',
    r'^(?:resin|gum|wax)$',
    r'.*\boleoresin\b.*',
]
COMPILED_NON_SPECIFIC = [re.compile(p, re.IGNORECASE) for p in NON_SPECIFIC_PATTERNS]


# ---------------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------------
def setup_logging(log_file: Path) -> logging.Logger:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("01_resolve_structures")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh_fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    fh.setFormatter(fh_fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch_fmt = logging.Formatter("[%(levelname)s] %(message)s")
    ch.setFormatter(ch_fmt)
    logger.addHandler(ch)

    return logger


# ---------------------------------------------------------------------------
# Master Dataset Integrity Check
# ---------------------------------------------------------------------------
def verify_master_manifest(logger: logging.Logger) -> str:
    manifest_path = Path("data/raw/mpbd/mpbd_dataset_manifest.json")
    master_path = Path("data/raw/mpbd/mpbd_plant_index.csv")

    if not manifest_path.exists():
        logger.error(f"Manifest missing: {manifest_path}")
        raise FileNotFoundError(f"Manifest missing: {manifest_path}")
    if not master_path.exists():
        logger.error(f"Master index missing: {master_path}")
        raise FileNotFoundError(f"Master index missing: {master_path}")

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    expected_sha256 = manifest["final_sha256"]

    h = hashlib.sha256()
    with open(master_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    actual_sha256 = h.hexdigest().upper()

    if actual_sha256 != expected_sha256.upper():
        logger.critical(
            f"MASTER MPBD SHA-256 MISMATCH! Expected {expected_sha256}, got {actual_sha256}"
        )
        raise ValueError(f"Master dataset integrity compromised: {actual_sha256}")

    logger.info(f"Master MPBD hash verified: {actual_sha256}")
    return actual_sha256


# ---------------------------------------------------------------------------
# Name Cleaning, Encoding-Loss & Non-Specific Detection
# ---------------------------------------------------------------------------
def check_encoding_loss(raw_name: str) -> bool:
    """
    Checks if raw name contains upstream corrupted characters:
    literal '?', U+FFFD, or mojibake sequences.
    """
    if not raw_name:
        return False
    if "?" in raw_name:
        return True
    if "\ufffd" in raw_name:
        return True
    if "\u00ef\u00bf\u00bd" in raw_name:
        return True
    return False


def clean_compound_name(name: str) -> str:
    """
    Conservative name cleaning:
    - Normalizes unicode spaces, curly quotes, backticks
    - Collapses repeated spaces
    - Leaves stereochemistry, locants, prefixes, and punctuation intact
    """
    if not name:
        return ""
    cleaned = name.replace("\u00a0", " ").replace("\u2018", "'").replace("\u2019", "'")
    cleaned = cleaned.replace("\u201c", '"').replace("\u201d", '"')
    cleaned = cleaned.replace("`", "'").replace("´", "'")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def is_non_specific(cleaned_name: str) -> Tuple[bool, Optional[str]]:
    """Checks if a compound name is a non-specific mixture or general term."""
    for regex in COMPILED_NON_SPECIFIC:
        if regex.search(cleaned_name):
            return True, regex.pattern
    return False, None


# ---------------------------------------------------------------------------
# PubChem PUG-REST Client with Disk Caching
# ---------------------------------------------------------------------------
class PubChemResolver:
    def __init__(self, cache_dir: Path, logger: logging.Logger):
        self.cache_dir = cache_dir
        self.cache_names_dir = cache_dir / "names"
        self.cache_cids_dir = cache_dir / "cids"
        self.cache_names_dir.mkdir(parents=True, exist_ok=True)
        self.cache_cids_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logger
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

        self.network_calls_count = 0
        self.cache_hits_count = 0

    def _get_with_retry(self, url: str) -> Tuple[Optional[requests.Response], Optional[str]]:
        """
        Executes request with exponential backoff on 429/503/timeout.
        Returns (response, error_str).
        """
        delay = REQUEST_DELAY_SEC
        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            time.sleep(REQUEST_DELAY_SEC)
            try:
                self.network_calls_count += 1
                resp = self.session.get(url, timeout=20)
                if resp.status_code in (429, 503):
                    wait = delay * (2 ** (attempt - 1))
                    self.logger.warning(
                        f"HTTP {resp.status_code} on {url}. Retrying in {wait:.1f}s (attempt {attempt}/{MAX_RETRIES})..."
                    )
                    time.sleep(wait)
                    continue
                return resp, None
            except (requests.RequestException, TimeoutError) as e:
                last_error = str(e)
                wait = delay * (2 ** (attempt - 1))
                self.logger.warning(
                    f"Request error ({e}) on {url}. Retrying in {wait:.1f}s (attempt {attempt}/{MAX_RETRIES})..."
                )
                time.sleep(wait)

        return None, last_error

    def query_name_cids(self, cleaned_name: str) -> Tuple[str, List[str], bool]:
        """
        Queries PubChem for CIDs matching a name.
        Returns: (match_type, candidate_cids_list, is_transient_error)
        match_type: 'exact_match', 'multiple_matches', 'no_match', 'fetch_error'
        """
        name_key = cleaned_name.lower().encode("utf-8")
        h = hashlib.sha256(name_key).hexdigest()[:24]
        cache_file = self.cache_names_dir / f"name_{h}.json"

        if cache_file.exists():
            self.cache_hits_count += 1
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            cids = [str(c) for c in data.get("cids", [])]
            status = data.get("status", 200)
            if status == 404 or len(cids) == 0:
                return "no_match", [], False
            elif len(cids) == 1:
                return "exact_match", cids, False
            else:
                return "multiple_matches", cids, False

        encoded_name = urllib.parse.quote(cleaned_name)
        url = f"{PUG_REST_BASE}/compound/name/{encoded_name}/cids/JSON"

        resp, err = self._get_with_retry(url)

        if resp is None:
            # Network failure after retries
            return "fetch_error", [], True

        if resp.status_code == 200:
            try:
                result_json = resp.json()
                raw_cids = result_json.get("IdentifierList", {}).get("CID", [])
                cids = [str(c) for c in raw_cids]
            except Exception as e:
                self.logger.error(f"Error parsing JSON from {url}: {e}")
                return "fetch_error", [], True

            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump({"name": cleaned_name, "status": 200, "cids": cids}, f)

            if len(cids) == 0:
                return "no_match", [], False
            elif len(cids) == 1:
                return "exact_match", cids, False
            else:
                return "multiple_matches", cids, False

        elif resp.status_code == 404:
            # Legitimate 404 from PubChem
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump({"name": cleaned_name, "status": 404, "cids": []}, f)
            return "no_match", [], False

        else:
            # Transient or server error (e.g. 500, 502, 504) -> Do NOT cache as no_match!
            self.logger.warning(f"HTTP {resp.status_code} for name '{cleaned_name}' - marked for retry")
            return "fetch_error", [], True

    def fetch_cid_properties_batch(self, cids: List[str]) -> Dict[str, Dict[str, str]]:
        """
        Fetches compound properties for a list of CIDs using disk cache and batch queries.
        Includes Title for name-verification.
        Returns a dictionary mapping cid -> property_dict.
        """
        results: Dict[str, Dict[str, str]] = {}
        missing_cids: List[str] = []

        # Check individual caches first
        for cid in cids:
            cache_file = self.cache_cids_dir / f"cid_{cid}.json"
            if cache_file.exists():
                with open(cache_file, "r", encoding="utf-8") as f:
                    prop_data = json.load(f)
                if "pubchem_title" in prop_data and "isomeric_smiles" in prop_data:
                    self.cache_hits_count += 1
                    results[cid] = prop_data
                    continue
            missing_cids.append(cid)

        if not missing_cids:
            return results

        # Query missing CIDs in batches of up to BATCH_CID_SIZE
        prop_fields = "CanonicalSMILES,IsomericSMILES,InChI,InChIKey,MolecularFormula,MolecularWeight,Title"
        for i in range(0, len(missing_cids), BATCH_CID_SIZE):
            chunk = missing_cids[i : i + BATCH_CID_SIZE]
            chunk_str = ",".join(chunk)
            url = f"{PUG_REST_BASE}/compound/cid/{chunk_str}/property/{prop_fields}/JSON"

            resp, err = self._get_with_retry(url)
            if resp is not None and resp.status_code == 200:
                try:
                    data = resp.json()
                    props_list = data.get("PropertyTable", {}).get("Properties", [])
                    for prop in props_list:
                        prop_cid = str(prop.get("CID"))
                        clean_props = {
                            "canonical_smiles": prop.get("ConnectivitySMILES")
                            or prop.get("CanonicalSMILES")
                            or prop.get("SMILES", ""),
                            "isomeric_smiles": prop.get("SMILES")
                            or prop.get("IsomericSMILES", ""),
                            "inchi": prop.get("InChI", ""),
                            "inchikey": prop.get("InChIKey", ""),
                            "molecular_formula": prop.get("MolecularFormula", ""),
                            "molecular_weight": str(prop.get("MolecularWeight", "")),
                            "pubchem_title": prop.get("Title", ""),
                        }
                        results[prop_cid] = clean_props

                        # Cache individually
                        cid_cache_file = self.cache_cids_dir / f"cid_{prop_cid}.json"
                        with open(cid_cache_file, "w", encoding="utf-8") as f:
                            json.dump(clean_props, f)

                except Exception as e:
                    self.logger.error(f"Error parsing batch properties response: {e}")
            else:
                self.logger.error(f"Batch properties query failed for chunk {chunk[:3]}...")

        # Fill any CIDs that were not returned by PubChem
        for cid in missing_cids:
            if cid not in results:
                empty_props = {
                    "canonical_smiles": "",
                    "isomeric_smiles": "",
                    "inchi": "",
                    "inchikey": "",
                    "molecular_formula": "",
                    "molecular_weight": "",
                    "pubchem_title": "",
                }
                results[cid] = empty_props
                cid_cache_file = self.cache_cids_dir / f"cid_{cid}.json"
                with open(cid_cache_file, "w", encoding="utf-8") as f:
                    json.dump(empty_props, f)

        return results


# ---------------------------------------------------------------------------
# Main Orchestration
# ---------------------------------------------------------------------------
def run_resolution(
    limit: Optional[int] = None,
    sample: Optional[int] = None,
    seed: int = 42,
    output_dir: Optional[Path] = None,
):
    log_file = Path("data/quality/compound_resolution.log")
    logger = setup_logging(log_file)
    logger.info("=" * 70)
    logger.info("STAGE 7A: PubChem Chemical Structure Resolution")
    logger.info(f"Execution Timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}")
    logger.info(f"Parameters: sample={sample}, seed={seed}, limit={limit}, output_dir={output_dir}")
    logger.info("=" * 70)

    start_time = time.time()

    # 1. Master dataset integrity check at start
    start_hash = verify_master_manifest(logger)

    # 2. Paths & output directories
    raw_compounds_file = Path("data/raw/bmppd/bmppd_compounds_raw.csv")

    if output_dir is not None:
        out_dir = Path(output_dir)
    elif sample is not None or limit is not None:
        out_dir = Path("data/processed/compounds/sample")
    else:
        out_dir = Path("data/processed/compounds")

    attrition_dir = Path("data/attrition")
    cache_dir = Path("data/cache/pubchem")
    quality_dir = Path("data/quality")

    out_dir.mkdir(parents=True, exist_ok=True)
    attrition_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)
    quality_dir.mkdir(parents=True, exist_ok=True)

    out_resolved_csv = out_dir / "compound_structures_resolved.csv"
    out_multiple_review_csv = out_dir / "name_multiple_matches_review.csv"
    out_attrition_csv = attrition_dir / "compound_resolution_attrition.csv"
    out_report_md = quality_dir / "stage7a_resolution_report.md"

    # 3. Read all input rows
    with open(raw_compounds_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)

    total_input_rows = len(all_rows)
    logger.info(f"Loaded {total_input_rows} rows from {raw_compounds_file}")

    # Build global distinct entity pools
    all_unique_cids = sorted(list(set(
        r["pubchem_cid"].strip() for r in all_rows if r["pubchem_cid"].strip().isdigit()
    )))
    all_unique_names = sorted(list(set(
        clean_compound_name(r["compound_name"].strip())
        for r in all_rows
        if not r["pubchem_cid"].strip().isdigit()
    )))

    total_unique_entities = len(all_unique_cids) + len(all_unique_names)
    logger.info(
        f"Global Unique Query Entities: {len(all_unique_cids)} CIDs + {len(all_unique_names)} names-without-CID = {total_unique_entities} total"
    )

    resolver = PubChemResolver(cache_dir, logger)

    # Handle sampling or row limitation
    if sample is not None:
        logger.info(f"Drawing proportional random sample of {sample} unique entities with seed={seed}...")
        rng = random.Random(seed)

        prop_cid = len(all_unique_cids) / total_unique_entities
        sample_cid_count = round(sample * prop_cid)
        sample_name_count = sample - sample_cid_count

        logger.info(
            f"Proportional Split Target: {sample_cid_count} CIDs ({sample_cid_count/sample*100:.1f}%) and {sample_name_count} names ({sample_name_count/sample*100:.1f}%)"
        )

        sampled_cids_set = set(rng.sample(all_unique_cids, sample_cid_count))
        sampled_names_set = set(rng.sample(all_unique_names, sample_name_count))

        rows = [
            r for r in all_rows
            if (r["pubchem_cid"].strip().isdigit() and r["pubchem_cid"].strip() in sampled_cids_set)
            or (not r["pubchem_cid"].strip().isdigit() and clean_compound_name(r["compound_name"].strip()) in sampled_names_set)
        ]
        direct_cids = sampled_cids_set
        names_to_resolve = {}
        for r in rows:
            if not r["pubchem_cid"].strip().isdigit():
                c_clean = clean_compound_name(r["compound_name"].strip())
                if c_clean in sampled_names_set and c_clean not in names_to_resolve:
                    names_to_resolve[c_clean] = r["compound_name"].strip()

    elif limit is not None and limit < total_input_rows:
        cid_rows = [r for r in all_rows if r["pubchem_cid"].strip().isdigit()]
        no_cid_rows = [r for r in all_rows if not r["pubchem_cid"].strip().isdigit()]
        half = limit // 2
        rows = cid_rows[:half] + no_cid_rows[: (limit - half)]
        direct_cids = set(r["pubchem_cid"].strip() for r in rows if r["pubchem_cid"].strip().isdigit())
        names_to_resolve = {}
        for r in rows:
            if not r["pubchem_cid"].strip().isdigit():
                c_clean = clean_compound_name(r["compound_name"].strip())
                if c_clean not in names_to_resolve:
                    names_to_resolve[c_clean] = r["compound_name"].strip()

    else:
        rows = all_rows
        direct_cids = set(all_unique_cids)
        names_to_resolve = {}
        for r in rows:
            if not r["pubchem_cid"].strip().isdigit():
                c_clean = clean_compound_name(r["compound_name"].strip())
                if c_clean not in names_to_resolve:
                    names_to_resolve[c_clean] = r["compound_name"].strip()

    logger.info(
        f"Active Workload: {len(direct_cids)} direct CIDs, {len(names_to_resolve)} distinct names without CID"
    )

    # 4. Process unique names with Encoding-Loss check, Non-Specific check, and Rolling Error Window
    name_resolution_results: Dict[str, Tuple[str, List[str], Optional[str]]] = {}
    multiple_matches_records = []
    skipped_nonspecific_records = []
    skipped_encoding_records = []
    fetch_error_names: Set[str] = set()
    exact_match_cids: Set[str] = set()

    total_names_count = len(names_to_resolve)
    recent_errors = deque(maxlen=MAX_ERROR_RATE_WINDOW)
    names_start_time = time.time()

    logger.info(f"Starting name-resolution phase for {total_names_count} unique names...")

    # Pass 1: Primary Query Pass
    processed_count = 0
    for cleaned_name, original_name in names_to_resolve.items():
        processed_count += 1

        # Check 1: Encoding Loss (Runs FIRST)
        if check_encoding_loss(original_name):
            logger.info(f"Skipped encoding loss: '{original_name}' (contains corrupted characters)")
            name_resolution_results[cleaned_name] = ("skipped_encoding_loss", [], None)
            skipped_encoding_records.append((original_name, cleaned_name))
            recent_errors.append(False)
            continue

        # Check 2: Non-Specific Filter (Runs SECOND)
        is_nonspec, pattern = is_non_specific(cleaned_name)
        if is_nonspec:
            logger.info(f"Skipped non-specific: '{original_name}' (matched pattern: {pattern})")
            name_resolution_results[cleaned_name] = ("skipped_nonspecific", [], None)
            skipped_nonspecific_records.append((original_name, cleaned_name, pattern))
            recent_errors.append(False)
            continue

        # Query PubChem PUG-REST
        match_type, cids, is_transient_error = resolver.query_name_cids(cleaned_name)
        recent_errors.append(is_transient_error)

        # Check rolling error rate
        if len(recent_errors) >= 50:
            err_rate = sum(recent_errors) / len(recent_errors)
            if err_rate > MAX_ERROR_RATE_THRESHOLD:
                logger.warning(
                    f"High error rate detected ({err_rate*100:.1f}% in last {len(recent_errors)} queries). Pausing for 10s backoff..."
                )
                time.sleep(10.0)

        if is_transient_error:
            fetch_error_names.add(cleaned_name)
            name_resolution_results[cleaned_name] = ("fetch_error", [], None)
        elif match_type == "exact_match":
            resolved_cid = cids[0]
            name_resolution_results[cleaned_name] = ("exact_match", cids, resolved_cid)
            exact_match_cids.add(resolved_cid)
        elif match_type == "multiple_matches":
            name_resolution_results[cleaned_name] = ("multiple_matches", cids, None)
            multiple_matches_records.append(
                {
                    "compound_name_original": original_name,
                    "compound_name_query": cleaned_name,
                    "candidate_cids": "|".join(cids),
                    "candidate_count": len(cids),
                }
            )
        else:
            name_resolution_results[cleaned_name] = ("no_match", [], None)

        # Progress reporting every 250 names
        if processed_count % 250 == 0 or processed_count == total_names_count:
            elapsed_p = time.time() - names_start_time
            rate = processed_count / max(1.0, elapsed_p)
            remaining = (total_names_count - processed_count) / max(0.01, rate)
            logger.info(
                f"Progress: {processed_count}/{total_names_count} names ({processed_count/total_names_count*100:.1f}%) | "
                f"Elapsed: {elapsed_p:.1f}s | Rate: {rate:.2f} names/s | ETA: {remaining/60:.1f}m | "
                f"Exact: {len(exact_match_cids)} | Mult: {len(multiple_matches_records)} | Err: {len(fetch_error_names)}"
            )

    # Pass 2 & 3: Retry transient fetch errors up to 3 passes
    retry_pass = 0
    while fetch_error_names and retry_pass < 3:
        retry_pass += 1
        wait_retry = 3.0 * retry_pass
        logger.info(
            f"Retry Pass {retry_pass}: Retrying {len(fetch_error_names)} transient fetch errors after {wait_retry:.1f}s sleep..."
        )
        time.sleep(wait_retry)

        still_failing = set()
        for cleaned_name in list(fetch_error_names):
            orig_name = names_to_resolve[cleaned_name]
            match_type, cids, is_transient_error = resolver.query_name_cids(cleaned_name)
            if is_transient_error:
                still_failing.add(cleaned_name)
            else:
                if match_type == "exact_match":
                    resolved_cid = cids[0]
                    name_resolution_results[cleaned_name] = ("exact_match", cids, resolved_cid)
                    exact_match_cids.add(resolved_cid)
                elif match_type == "multiple_matches":
                    name_resolution_results[cleaned_name] = ("multiple_matches", cids, None)
                    multiple_matches_records.append(
                        {
                            "compound_name_original": orig_name,
                            "compound_name_query": cleaned_name,
                            "candidate_cids": "|".join(cids),
                            "candidate_count": len(cids),
                        }
                    )
                else:
                    name_resolution_results[cleaned_name] = ("no_match", [], None)

        fetch_error_names = still_failing
        logger.info(f"Retry Pass {retry_pass} complete. Remaining failures: {len(fetch_error_names)}")

    # 5. Fetch chemical properties for ALL needed CIDs (direct CIDs + exact_match CIDs)
    all_needed_cids = list(direct_cids.union(exact_match_cids))
    logger.info(f"Fetching chemical properties for {len(all_needed_cids)} total distinct CIDs...")
    cid_properties_map = resolver.fetch_cid_properties_batch(all_needed_cids)

    # Also fetch properties for candidate CIDs of multiple-match items to analyze connectivity layers
    all_multiple_candidate_cids: Set[str] = set()
    for mr in multiple_matches_records:
        for cid_str in mr["candidate_cids"].split("|"):
            if cid_str.strip().isdigit():
                all_multiple_candidate_cids.add(cid_str.strip())

    if all_multiple_candidate_cids:
        logger.info(f"Fetching properties for {len(all_multiple_candidate_cids)} candidate CIDs of multiple-match records...")
        cand_props_map = resolver.fetch_cid_properties_batch(list(all_multiple_candidate_cids))
    else:
        cand_props_map = {}

    # Evaluate connectivity layer homogeneity for multiple-match items
    multiple_matches_same_connectivity_count = 0
    for mr in multiple_matches_records:
        cand_cids = mr["candidate_cids"].split("|")
        conn_layers = set()
        for cid_str in cand_cids:
            p = cand_props_map.get(cid_str, {})
            ikey = p.get("inchikey", "")
            if ikey and len(ikey) >= 14:
                conn_layers.add(ikey[:14])
        if len(conn_layers) == 1:
            multiple_matches_same_connectivity_count += 1

    # 6. Map results back to every row
    resolved_rows = []
    match_counts = {
        "CID-based": 0,
        "exact_match": 0,
        "multiple_matches": 0,
        "no_match": 0,
        "skipped_nonspecific": 0,
        "skipped_encoding_loss": 0,
        "fetch_error": 0,
    }

    timestamp_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Track distinct structures & plant distribution
    distinct_inchikeys: Set[str] = set()
    distinct_connectivity_layers: Set[str] = set()
    plants_per_inchikey: Dict[str, Set[str]] = {}

    for r in rows:
        plant_idx = r["plant_index"]
        src_query = r["source_query"]
        bmpdd_query = r["bmpdd_query_name"]
        orig_name = r["compound_name"].strip()
        query_name = clean_compound_name(orig_name)
        orig_cid = r["pubchem_cid"].strip()
        src_url = r["source_page_url"]

        if orig_cid.isdigit():
            match_type = "CID-based"
            res_method = "direct_pubchem_cid"
            pubchem_query = orig_cid
            res_cid = orig_cid
            candidate_cids_str = orig_cid
            match_counts["CID-based"] += 1
        else:
            m_type, cand_cids, res_cid = name_resolution_results[query_name]
            match_type = m_type
            res_method = f"name_lookup_{m_type}"
            pubchem_query = query_name
            candidate_cids_str = "|".join(cand_cids) if cand_cids else ""
            match_counts[m_type] += 1

        props = cid_properties_map.get(res_cid, {}) if res_cid else {}
        ikey = props.get("inchikey", "")

        if ikey:
            distinct_inchikeys.add(ikey)
            if len(ikey) >= 14:
                distinct_connectivity_layers.add(ikey[:14])
            if ikey not in plants_per_inchikey:
                plants_per_inchikey[ikey] = set()
            plants_per_inchikey[ikey].add(plant_idx)

        resolved_rows.append(
            {
                "plant_index": plant_idx,
                "source_query": src_query,
                "bmpdd_query_name": bmpdd_query,
                "compound_name_original": orig_name,
                "compound_name_query": query_name,
                "pubchem_query": pubchem_query,
                "pubchem_cid_original": orig_cid,
                "resolved_cid": res_cid or "",
                "pubchem_title": props.get("pubchem_title", ""),
                "match_type": match_type,
                "resolution_method": res_method,
                "candidate_cids": candidate_cids_str,
                "isomeric_smiles": props.get("isomeric_smiles", ""),
                "canonical_smiles": props.get("canonical_smiles", ""),
                "inchi": props.get("inchi", ""),
                "inchikey": ikey,
                "molecular_formula": props.get("molecular_formula", ""),
                "molecular_weight": props.get("molecular_weight", ""),
                "source_page_url": src_url,
                "resolved_timestamp": timestamp_iso,
            }
        )

    # Plant counts per distinct InChIKey
    single_plant_compounds = sum(1 for pset in plants_per_inchikey.values() if len(pset) == 1)
    multi_plant_compounds = sum(1 for pset in plants_per_inchikey.values() if len(pset) >= 2)

    # 7. Write resolved dataset
    fieldnames = [
        "plant_index",
        "source_query",
        "bmpdd_query_name",
        "compound_name_original",
        "compound_name_query",
        "pubchem_query",
        "pubchem_cid_original",
        "resolved_cid",
        "pubchem_title",
        "match_type",
        "resolution_method",
        "candidate_cids",
        "isomeric_smiles",
        "canonical_smiles",
        "inchi",
        "inchikey",
        "molecular_formula",
        "molecular_weight",
        "source_page_url",
        "resolved_timestamp",
    ]

    with open(out_resolved_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resolved_rows)

    logger.info(f"Wrote {len(resolved_rows)} resolved rows to {out_resolved_csv}")

    # 8. Write multiple matches review file
    with open(out_multiple_review_csv, "w", newline="", encoding="utf-8") as f:
        review_fields = [
            "compound_name_original",
            "compound_name_query",
            "candidate_cids",
            "candidate_count",
        ]
        writer = csv.DictWriter(f, fieldnames=review_fields)
        writer.writeheader()
        writer.writerows(multiple_matches_records)

    logger.info(
        f"Wrote {len(multiple_matches_records)} multiple-match review records to {out_multiple_review_csv}"
    )

    # 9. Categorize no_match items
    no_match_unique_names = [
        names_to_resolve[k]
        for k, v in name_resolution_results.items()
        if v[0] == "no_match"
    ]

    no_match_breakdown = {
        "parenthetical_synonym": 0,
        "cas_inverted": 0,
        "stereo_descriptor": 0,
        "class_or_plural": 0,
        "other": 0,
    }

    for nm in no_match_unique_names:
        if bool(re.match(r'^\([^\)]+\)-', nm)):
            no_match_breakdown["stereo_descriptor"] += 1
        elif ", " in nm:
            no_match_breakdown["cas_inverted"] += 1
        elif bool(re.search(r'\([A-Za-z0-9\s\-]{2,}\)|\[.+\]', nm)):
            no_match_breakdown["parenthetical_synonym"] += 1
        elif nm.lower().endswith(('s', 'es')) or any(w in nm.lower() for w in ['derivatives', 'fraction', 'extract', 'glycosides', 'alkaloids', 'phenols', 'flavonoids', 'tannins', 'saponins']):
            no_match_breakdown["class_or_plural"] += 1
        else:
            no_match_breakdown["other"] += 1

    # 10. Write attrition metrics
    attrition_records = [
        {
            "step": "1_input_rows",
            "description": "Total input plant-compound pairs evaluated",
            "row_count": len(rows),
            "notes": f"Sample: {sample}, Seed: {seed}, Limit: {limit}",
        },
        {
            "step": "2_cid_based_input",
            "description": "Rows with valid numeric PubChem CID",
            "row_count": match_counts["CID-based"],
            "notes": "Direct CID property lookup",
        },
        {
            "step": "3_name_based_exact",
            "description": "Name lookup returning exactly 1 CID",
            "row_count": match_counts["exact_match"],
            "notes": "Single exact match auto-accepted",
        },
        {
            "step": "4_name_based_multiple",
            "description": "Name lookup returning >1 CIDs",
            "row_count": match_counts["multiple_matches"],
            "notes": "Logged for manual review, not auto-guessed",
        },
        {
            "step": "5_name_based_no_match",
            "description": "Name lookup returning 0 CIDs (404)",
            "row_count": match_counts["no_match"],
            "notes": "PubChem has no record for this name",
        },
        {
            "step": "6_skipped_nonspecific",
            "description": "Non-specific mixture or extract terms skipped",
            "row_count": match_counts["skipped_nonspecific"],
            "notes": "Skipped without API call",
        },
        {
            "step": "7_skipped_encoding_loss",
            "description": "Corrupted upstream character terms skipped",
            "row_count": match_counts["skipped_encoding_loss"],
            "notes": "Skipped without API call",
        },
        {
            "step": "8_fetch_error",
            "description": "Transient network errors after retries",
            "row_count": match_counts["fetch_error"],
            "notes": "Should be 0 after retry passes",
        },
        {
            "step": "9_structures_resolved",
            "description": "Rows successfully assigned a structure",
            "row_count": match_counts["CID-based"] + match_counts["exact_match"],
            "notes": "Valid SMILES and InChIKey populated",
        },
    ]

    with open(out_attrition_csv, "w", newline="", encoding="utf-8") as f:
        attr_fields = ["step", "description", "row_count", "notes"]
        writer = csv.DictWriter(f, fieldnames=attr_fields)
        writer.writeheader()
        writer.writerows(attrition_records)

    logger.info(f"Wrote resolution attrition summary to {out_attrition_csv}")

    # 11. Final integrity check
    end_hash = verify_master_manifest(logger)
    assert start_hash == end_hash, "Master dataset hash changed during execution!"

    elapsed = time.time() - start_time

    # Calculate unique entity breakdown
    unique_counts = {
        "CID-based": len(direct_cids),
        "exact_match": len([k for k, v in name_resolution_results.items() if v[0] == "exact_match"]),
        "multiple_matches": len([k for k, v in name_resolution_results.items() if v[0] == "multiple_matches"]),
        "no_match": len([k for k, v in name_resolution_results.items() if v[0] == "no_match"]),
        "skipped_nonspecific": len([k for k, v in name_resolution_results.items() if v[0] == "skipped_nonspecific"]),
        "skipped_encoding_loss": len([k for k, v in name_resolution_results.items() if v[0] == "skipped_encoding_loss"]),
        "fetch_error": len([k for k, v in name_resolution_results.items() if v[0] == "fetch_error"]),
    }
    total_unique_workload = len(direct_cids) + len(names_to_resolve)

    logger.info("=" * 70)
    logger.info("STAGE 7A EXECUTION SUMMARY:")
    logger.info(f"  Total Rows Evaluated:       {len(rows)}")
    logger.info(f"  CID-based (Direct):         {match_counts['CID-based']}")
    logger.info(f"  Exact Match (Name):         {match_counts['exact_match']}")
    logger.info(f"  Multiple Matches (Review):  {match_counts['multiple_matches']}")
    logger.info(f"  No Match (404):             {match_counts['no_match']}")
    logger.info(f"  Skipped Non-Specific:       {match_counts['skipped_nonspecific']}")
    logger.info(f"  Skipped Encoding Loss:      {match_counts['skipped_encoding_loss']}")
    logger.info(f"  Fetch Errors Remaining:     {match_counts['fetch_error']}")
    logger.info(
        f"  Total Rows Resolved:        {match_counts['CID-based'] + match_counts['exact_match']} ({ (match_counts['CID-based'] + match_counts['exact_match'])/max(1, len(rows))*100:.1f}%)"
    )
    logger.info(f"  Distinct InChIKeys:         {len(distinct_inchikeys)}")
    logger.info(f"  Distinct Connectivity:      {len(distinct_connectivity_layers)}")
    logger.info(f"  Single Plant Compounds:     {single_plant_compounds}")
    logger.info(f"  Multi Plant Compounds:      {multi_plant_compounds}")
    logger.info(f"  Network Calls Made:         {resolver.network_calls_count}")
    logger.info(f"  Cache Hits:                 {resolver.cache_hits_count}")
    logger.info(f"  Total Runtime:              {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
    logger.info("=" * 70)

    # 12. Write comprehensive markdown report
    resolved_rows_count = match_counts["CID-based"] + match_counts["exact_match"]
    resolved_rows_pct = resolved_rows_count / max(1, len(rows)) * 100.0
    resolved_entities_count = unique_counts["CID-based"] + unique_counts["exact_match"]
    resolved_entities_pct = resolved_entities_count / max(1, total_unique_workload) * 100.0

    report_md_content = f"""# Stage 7A: Chemical Structure Resolution Report

**Execution Timestamp**: {timestamp_iso}  
**Master MPBD SHA-256 (Start & End)**: `{end_hash}` (Integrity Verified)  
**Total Runtime**: {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)  
**Network Calls Made**: {resolver.network_calls_count}  
**Cache Hits**: {resolver.cache_hits_count}  

---

## 1. Unique Entities Processed

| Match Classification | Unique Count | % of Workload | Definition / Description |
| :--- | :---: | :---: | :--- |
| **`CID-based`** (Direct) | **{unique_counts['CID-based']:,}** | {unique_counts['CID-based']/total_unique_workload*100:.2f}% | Directly resolved via numeric PubChem CID in BMPPD |
| **`exact_match`** (Name) | **{unique_counts['exact_match']:,}** | {unique_counts['exact_match']/total_unique_workload*100:.2f}% | Name-based lookup returning exactly 1 CID |
| **`multiple_matches`** | **{unique_counts['multiple_matches']:,}** | {unique_counts['multiple_matches']/total_unique_workload*100:.2f}% | Name-based lookup returning >1 CIDs (logged for review) |
| **`no_match`** | **{unique_counts['no_match']:,}** | {unique_counts['no_match']/total_unique_workload*100:.2f}% | PubChem returned 404 (no compound found for string) |
| **`skipped_nonspecific`** | **{unique_counts['skipped_nonspecific']:,}** | {unique_counts['skipped_nonspecific']/total_unique_workload*100:.2f}% | Mixture/extract terms skipped without API call |
| **`skipped_encoding_loss`**| **{unique_counts['skipped_encoding_loss']:,}** | {unique_counts['skipped_encoding_loss']/total_unique_workload*100:.2f}% | Corrupted characters ('?', '\\ufffd') skipped without API call |
| **`fetch_error`** | **{unique_counts['fetch_error']:,}** | {unique_counts['fetch_error']/total_unique_workload*100:.2f}% | Transient network errors remaining after 3 retry passes |
| **Total Workload Entities** | **{total_unique_workload:,}** | **100.00%** | |
| **Total Resolved Entities** | **{resolved_entities_count:,}** | **{resolved_entities_pct:.2f}%** | Structure resolved (`CID-based` + `exact_match`) |

---

## 2. Row-Level Dataset Coverage

- **Total Plant–Compound Rows**: **{len(rows):,}**
- **Rows Successfully Resolved**: **{resolved_rows_count:,}** (**{resolved_rows_pct:.2f}%**)
- **Rows Missing Structure**: **{len(rows) - resolved_rows_count:,}** (**{100.0 - resolved_rows_pct:.2f}%**)

---

## 3. Non-Specific Skipped Names (`skipped_nonspecific`)

Total Count: **{len(skipped_nonspecific_records)}**

| # | Compound Name (Original) | Cleaned Query | Triggering Regex Pattern | Single Compound Assessment |
| :-: | :--- | :--- | :--- | :--- |
"""
    if skipped_nonspecific_records:
        for idx, (orig, clean, pat) in enumerate(skipped_nonspecific_records, 1):
            is_single = "POTENTIAL SINGLE COMPOUND (REVIEW)" if "fatty acid" in orig.lower() else "True mixture / extract"
            report_md_content += f"| {idx} | `{orig}` | `{clean}` | `{pat}` | {is_single} |\n"
    else:
        report_md_content += "| — | None skipped in this run | — | — | — |\n"

    report_md_content += f"""
---

## 4. Encoding-Loss Skipped Names (`skipped_encoding_loss`)

Total Count: **{len(skipped_encoding_records)}**

| # | Compound Name (Original) | Cleaned Query | Notes |
| :-: | :--- | :--- | :--- |
"""
    if skipped_encoding_records:
        for idx, (orig, clean) in enumerate(skipped_encoding_records, 1):
            report_md_content += f"| {idx} | `{orig}` | `{clean}` | Contains destroyed character (`?` or replacement) |\n"
    else:
        report_md_content += "| — | None in this run | — | — |\n"

    report_md_content += f"""
---

## 5. Multiple-Matches Analysis (`multiple_matches`)

- **Total Multiple-Match Names**: **{len(multiple_matches_records):,}**
- **Names where ALL candidates share the SAME 14-char InChIKey connectivity layer**: **{multiple_matches_same_connectivity_count:,}** ({multiple_matches_same_connectivity_count/max(1, len(multiple_matches_records))*100:.1f}%)
- **Interpretation**: {multiple_matches_same_connectivity_count} of the {len(multiple_matches_records)} multiple-match names represent stereoisomers or salt variants of the exact same 2D molecular graph.

---

## 6. No-Match Structural Breakdown (`no_match`)

Total Unresolved Names: **{len(no_match_unique_names):,}**

| Category Pattern | Count | % of No-Match | Example Pattern |
| :--- | :---: | :---: | :--- |
| **Parenthetical or bracketed synonym** | **{no_match_breakdown['parenthetical_synonym']:,}** | {no_match_breakdown['parenthetical_synonym']/max(1, len(no_match_unique_names))*100:.1f}% | `Compound Name (Synonym)` or `Name[Synonym]` |
| **CAS-style inverted name** | **{no_match_breakdown['cas_inverted']:,}** | {no_match_breakdown['cas_inverted']/max(1, len(no_match_unique_names))*100:.1f}% | `Silane, cyclohexyl dimethoxy methyl` |
| **Parenthesized stereo descriptor prefix** | **{no_match_breakdown['stereo_descriptor']:,}** | {no_match_breakdown['stereo_descriptor']/max(1, len(no_match_unique_names))*100:.1f}% | `(1R,2S)-...` or `(+)-...` |
| **Class or plural names** | **{no_match_breakdown['class_or_plural']:,}** | {no_match_breakdown['class_or_plural']/max(1, len(no_match_unique_names))*100:.1f}% | `Flavonones`, `...derivatives` |
| **Other / Misspelling / Obscure** | **{no_match_breakdown['other']:,}** | {no_match_breakdown['other']/max(1, len(no_match_unique_names))*100:.1f}% | `Andrachcine` (misspelling), obscure metabolites |

---

## 7. Distinct Resolved Structures & Plant Co-Occurrence

- **Distinct Standard InChIKeys**: **{len(distinct_inchikeys):,}**
- **Distinct Flat Connectivity Layers (First 14 chars)**: **{len(distinct_connectivity_layers):,}**
- **Compounds found in ONLY 1 plant**: **{single_plant_compounds:,}** ({single_plant_compounds/max(1, len(distinct_inchikeys))*100:.1f}%)
- **Compounds found in 2 OR MORE plants**: **{multi_plant_compounds:,}** ({multi_plant_compounds/max(1, len(distinct_inchikeys))*100:.1f}%)

---

## 8. Provenance & Artifact Checklist

- Resolved dataset: [`data/processed/compounds/compound_structures_resolved.csv`](file:///f:/bmppd-thesis/data/processed/compounds/compound_structures_resolved.csv)
- Multiple-match review table: [`data/processed/compounds/name_multiple_matches_review.csv`](file:///f:/bmppd-thesis/data/processed/compounds/name_multiple_matches_review.csv)
- Attrition ledger: [`data/attrition/compound_resolution_attrition.csv`](file:///f:/bmppd-thesis/data/attrition/compound_resolution_attrition.csv)
- Execution log: [`data/quality/compound_resolution.log`](file:///f:/bmppd-thesis/data/quality/compound_resolution.log)
"""

    with open(out_report_md, "w", encoding="utf-8") as f:
        f.write(report_md_content)

    logger.info(f"Wrote comprehensive resolution report to {out_report_md}")

    return match_counts, unique_counts, elapsed


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Stage 7A Step 1: Resolve Chemical Structures from PubChem PUG-REST (Production)"
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        help="Proportional random sample of unique entities (CIDs + names-without-CID)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible sampling (default: 42)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of rows for testing",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Custom output directory (default: data/processed/compounds)",
    )
    args = parser.parse_args()

    run_resolution(
        limit=args.limit,
        sample=args.sample,
        seed=args.seed,
        output_dir=Path(args.output_dir) if args.output_dir else None,
    )
