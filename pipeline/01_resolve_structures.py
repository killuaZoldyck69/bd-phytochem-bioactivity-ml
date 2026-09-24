#!/usr/bin/env python3
"""
Stage 7A - Pipeline Step 1: Resolve Chemical Structures from PubChem PUG-REST

Reads:
  - data/raw/mpbd/mpbd_plant_index.csv (Frozen master; verified against manifest)
  - data/raw/bmppd/bmppd_compounds_raw.csv (Consolidated plant-compound pairs)

Produces:
  - data/processed/compounds/compound_structures_resolved.csv
  - data/processed/compounds/name_multiple_matches_review.csv
  - data/attrition/compound_resolution_attrition.csv
  - data/cache/pubchem/ (Raw JSON responses for CIDs and names)
  - data/quality/compound_resolution.log

Rules & Safeguards:
  - Verifies SHA-256 of master MPBD index at start and end.
  - Caches all raw API responses to disk so reruns make 0 network calls.
  - Conservative name cleaning: only whitespace trimming and unicode normalization.
  - Does NOT strip or alter stereo/locant prefixes (e.g. (+)-, (-)-, alpha-, beta-).
  - Skips non-specific names (essential oil, extract, unknown, fatty acids, etc.).
  - Flags multiple matches as needs_review without auto-guessing; writes candidate CIDs to review table.
  - Rate limits requests (<= 4 req/sec) with exponential backoff on HTTP 429/503.
"""

import argparse
import csv
import datetime
import hashlib
import json
import logging
import os
from pathlib import Path
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
# Name Cleaning & Non-Specific Detection
# ---------------------------------------------------------------------------
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

    def _get_with_retry(self, url: str) -> requests.Response:
        delay = REQUEST_DELAY_SEC
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
                return resp
            except (requests.RequestException, TimeoutError) as e:
                wait = delay * (2 ** (attempt - 1))
                self.logger.warning(
                    f"Request failed ({e}) on {url}. Retrying in {wait:.1f}s (attempt {attempt}/{MAX_RETRIES})..."
                )
                time.sleep(wait)

        # Final attempt
        self.network_calls_count += 1
        return self.session.get(url, timeout=25)

    def query_name_cids(self, cleaned_name: str) -> Tuple[str, List[str]]:
        """
        Queries PubChem for CIDs matching a name.
        Returns: (match_type, candidate_cids_list)
        match_type: 'exact_match', 'multiple_matches', 'no_match'
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
                return "no_match", []
            elif len(cids) == 1:
                return "exact_match", cids
            else:
                return "multiple_matches", cids

        encoded_name = urllib.parse.quote(cleaned_name)
        url = f"{PUG_REST_BASE}/compound/name/{encoded_name}/cids/JSON"

        resp = self._get_with_retry(url)

        if resp.status_code == 200:
            try:
                result_json = resp.json()
                raw_cids = result_json.get("IdentifierList", {}).get("CID", [])
                cids = [str(c) for c in raw_cids]
            except Exception as e:
                self.logger.error(f"Error parsing JSON from {url}: {e}")
                cids = []

            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump({"name": cleaned_name, "status": 200, "cids": cids}, f)

            if len(cids) == 0:
                return "no_match", []
            elif len(cids) == 1:
                return "exact_match", cids
            else:
                return "multiple_matches", cids

        elif resp.status_code == 404:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump({"name": cleaned_name, "status": 404, "cids": []}, f)
            return "no_match", []

        else:
            self.logger.error(f"Unexpected status {resp.status_code} for name '{cleaned_name}'")
            return "no_match", []

    def fetch_cid_properties_batch(self, cids: List[str]) -> Dict[str, Dict[str, str]]:
        """
        Fetches compound properties for a list of CIDs using disk cache and batch queries.
        Returns a dictionary mapping cid -> property_dict.
        """
        results: Dict[str, Dict[str, str]] = {}
        missing_cids: List[str] = []

        # Check individual caches first
        for cid in cids:
            cache_file = self.cache_cids_dir / f"cid_{cid}.json"
            if cache_file.exists():
                self.cache_hits_count += 1
                with open(cache_file, "r", encoding="utf-8") as f:
                    prop_data = json.load(f)
                results[cid] = prop_data
            else:
                missing_cids.append(cid)

        if not missing_cids:
            return results

        # Query missing CIDs in batches of up to BATCH_CID_SIZE
        prop_fields = "CanonicalSMILES,IsomericSMILES,InChI,InChIKey,MolecularFormula,MolecularWeight"
        for i in range(0, len(missing_cids), BATCH_CID_SIZE):
            chunk = missing_cids[i : i + BATCH_CID_SIZE]
            chunk_str = ",".join(chunk)
            url = f"{PUG_REST_BASE}/compound/cid/{chunk_str}/property/{prop_fields}/JSON"

            resp = self._get_with_retry(url)
            if resp.status_code == 200:
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
                        }
                        results[prop_cid] = clean_props

                        # Cache individually
                        cid_cache_file = self.cache_cids_dir / f"cid_{prop_cid}.json"
                        with open(cid_cache_file, "w", encoding="utf-8") as f:
                            json.dump(clean_props, f)

                except Exception as e:
                    self.logger.error(f"Error parsing batch properties response: {e}")
            else:
                self.logger.error(
                    f"Batch properties query failed with status {resp.status_code}: {resp.text[:150]}"
                )

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
                }
                results[cid] = empty_props
                cid_cache_file = self.cache_cids_dir / f"cid_{cid}.json"
                with open(cid_cache_file, "w", encoding="utf-8") as f:
                    json.dump(empty_props, f)

        return results


# ---------------------------------------------------------------------------
# Main Orchestration
# ---------------------------------------------------------------------------
def run_resolution(limit: Optional[int] = None, stratified: bool = True):
    log_file = Path("data/quality/compound_resolution.log")
    logger = setup_logging(log_file)
    logger.info("=" * 70)
    logger.info("STAGE 7A: PubChem Chemical Structure Resolution")
    logger.info(f"Execution Timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}")
    logger.info(f"Parameters: limit={limit}, stratified={stratified}")
    logger.info("=" * 70)

    # 1. Master dataset integrity check at start
    start_hash = verify_master_manifest(logger)

    # 2. Paths & output directories
    raw_compounds_file = Path("data/raw/bmppd/bmppd_compounds_raw.csv")
    out_dir = Path("data/processed/compounds")
    attrition_dir = Path("data/attrition")
    cache_dir = Path("data/cache/pubchem")

    out_dir.mkdir(parents=True, exist_ok=True)
    attrition_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    out_resolved_csv = out_dir / "compound_structures_resolved.csv"
    out_multiple_review_csv = out_dir / "name_multiple_matches_review.csv"
    out_attrition_csv = attrition_dir / "compound_resolution_attrition.csv"

    # 3. Read input rows
    with open(raw_compounds_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)

    total_input_rows = len(all_rows)
    logger.info(f"Loaded {total_input_rows} rows from {raw_compounds_file}")

    # Handle limit / sample subset
    if limit is not None and limit < total_input_rows:
        if stratified:
            cid_rows = [r for r in all_rows if r["pubchem_cid"].strip().isdigit()]
            no_cid_rows = [r for r in all_rows if not r["pubchem_cid"].strip().isdigit()]
            half = limit // 2
            selected_rows = cid_rows[:half] + no_cid_rows[: (limit - half)]
            logger.info(
                f"Stratified sample of {limit} rows: {len(cid_rows[:half])} CID-based + {len(no_cid_rows[:limit-half])} name-based"
            )
            rows = selected_rows
        else:
            rows = all_rows[:limit]
            logger.info(f"Sequential head sample of {limit} rows")
    else:
        rows = all_rows

    resolver = PubChemResolver(cache_dir, logger)

    # 4. Extract unique entities to resolve
    # Unique direct CIDs
    direct_cids: Set[str] = set()
    # Unique compound names missing CID
    names_to_resolve: Dict[str, str] = {}  # cleaned_name -> original_name

    for r in rows:
        raw_cid = r["pubchem_cid"].strip()
        cname = r["compound_name"].strip()
        if raw_cid.isdigit():
            direct_cids.add(raw_cid)
        else:
            c_cleaned = clean_compound_name(cname)
            if c_cleaned not in names_to_resolve:
                names_to_resolve[c_cleaned] = cname

    logger.info(
        f"Unique entities in workload: {len(direct_cids)} direct CIDs, {len(names_to_resolve)} distinct names without CID"
    )

    # 5. Process unique names
    # Mapping: cleaned_name -> (match_type, candidate_cids, resolved_cid)
    name_resolution_results: Dict[str, Tuple[str, List[str], Optional[str]]] = {}
    multiple_matches_records = []

    exact_match_cids: Set[str] = set()

    for cleaned_name, original_name in names_to_resolve.items():
        is_nonspec, pattern = is_non_specific(cleaned_name)
        if is_nonspec:
            logger.info(f"Skipping non-specific name: '{original_name}' (matched pattern: {pattern})")
            name_resolution_results[cleaned_name] = ("skipped_nonspecific", [], None)
            continue

        match_type, cids = resolver.query_name_cids(cleaned_name)

        if match_type == "exact_match":
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

    # 6. Fetch chemical properties for ALL needed CIDs (direct CIDs + exact_match CIDs)
    all_needed_cids = list(direct_cids.union(exact_match_cids))
    logger.info(f"Fetching chemical properties for {len(all_needed_cids)} total distinct CIDs...")
    cid_properties_map = resolver.fetch_cid_properties_batch(all_needed_cids)

    # 7. Map results back to every row
    resolved_rows = []
    match_counts = {
        "CID-based": 0,
        "exact_match": 0,
        "multiple_matches": 0,
        "no_match": 0,
        "skipped_nonspecific": 0,
    }

    timestamp_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

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
            res_cid = orig_cid
            candidate_cids_str = orig_cid
            match_counts["CID-based"] += 1
        else:
            m_type, cand_cids, res_cid = name_resolution_results[query_name]
            match_type = m_type
            res_method = f"name_lookup_{m_type}"
            candidate_cids_str = "|".join(cand_cids) if cand_cids else ""
            match_counts[m_type] += 1

        props = cid_properties_map.get(res_cid, {}) if res_cid else {}

        resolved_rows.append(
            {
                "plant_index": plant_idx,
                "source_query": src_query,
                "bmpdd_query_name": bmpdd_query,
                "compound_name_original": orig_name,
                "compound_name_query": query_name,
                "pubchem_cid_original": orig_cid,
                "resolved_cid": res_cid or "",
                "match_type": match_type,
                "resolution_method": res_method,
                "candidate_cids": candidate_cids_str,
                "canonical_smiles": props.get("canonical_smiles", ""),
                "isomeric_smiles": props.get("isomeric_smiles", ""),
                "inchi": props.get("inchi", ""),
                "inchikey": props.get("inchikey", ""),
                "molecular_formula": props.get("molecular_formula", ""),
                "molecular_weight": props.get("molecular_weight", ""),
                "source_page_url": src_url,
                "resolved_timestamp": timestamp_iso,
            }
        )

    # 8. Write resolved dataset
    fieldnames = [
        "plant_index",
        "source_query",
        "bmpdd_query_name",
        "compound_name_original",
        "compound_name_query",
        "pubchem_cid_original",
        "resolved_cid",
        "match_type",
        "resolution_method",
        "candidate_cids",
        "canonical_smiles",
        "isomeric_smiles",
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

    # 9. Write multiple matches review file
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

    # 10. Write attrition metrics
    attrition_records = [
        {
            "step": "1_input_rows",
            "description": "Total input plant-compound pairs evaluated",
            "row_count": len(rows),
            "notes": f"Limit: {limit}, Stratified: {stratified}",
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
            "step": "7_structures_resolved",
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

    logger.info("=" * 70)
    logger.info("STAGE 7A EXECUTION SUMMARY:")
    logger.info(f"  Total Rows Evaluated:       {len(rows)}")
    logger.info(f"  CID-based (Direct):         {match_counts['CID-based']}")
    logger.info(f"  Exact Match (Name):         {match_counts['exact_match']}")
    logger.info(f"  Multiple Matches (Review):  {match_counts['multiple_matches']}")
    logger.info(f"  No Match (404):             {match_counts['no_match']}")
    logger.info(f"  Skipped Non-Specific:       {match_counts['skipped_nonspecific']}")
    logger.info(
        f"  Total Successfully Resolved:{match_counts['CID-based'] + match_counts['exact_match']}"
    )
    logger.info(f"  Network Calls Made:         {resolver.network_calls_count}")
    logger.info(f"  Cache Hits:                 {resolver.cache_hits_count}")
    logger.info("=" * 70)

    return match_counts, resolver.network_calls_count, resolver.cache_hits_count


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Stage 7A Step 1: Resolve Chemical Structures from PubChem PUG-REST"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of rows for testing (default: all rows)",
    )
    parser.add_argument(
        "--unstratified",
        action="store_true",
        help="Take sequential head rows instead of stratified sample when --limit is set",
    )
    args = parser.parse_args()

    run_resolution(limit=args.limit, stratified=not args.unstratified)
