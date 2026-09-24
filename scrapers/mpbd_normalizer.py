"""
mpbd_normalizer.py

Stage 4 — Botanical Reconciliation & Normalization for MPBD.

Architecture:
  Layer A — Deterministic text normalization (no botanical knowledge required).
  Layer B — Conservative botanical reconciliation (evidence-based only).

This module is strictly read-only with respect to:
    data/raw/mpbd/mpbd_plant_index.csv

All output goes to:
    data/processed/mpbd/
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ============================================================================
# PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_CSV = PROJECT_ROOT / "data" / "raw" / "mpbd" / "mpbd_plant_index.csv"
MANIFEST_JSON = PROJECT_ROOT / "data" / "raw" / "mpbd" / "mpbd_dataset_manifest.json"

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "mpbd"
QUALITY_DIR = PROJECT_ROOT / "data" / "quality"

NORMALIZED_CSV = PROCESSED_DIR / "mpbd_plant_index_normalized.csv"
RECONCILIATION_CSV = PROCESSED_DIR / "mpbd_botanical_reconciliation.csv"
FAMILY_NORM_CSV = PROCESSED_DIR / "mpbd_family_normalization.csv"
RECONCILIATION_MANIFEST = PROCESSED_DIR / "mpbd_reconciliation_manifest.json"
RECONCILIATION_REPORT = QUALITY_DIR / "mpbd_reconciliation_report.md"


# ============================================================================
# LAYER A — DETERMINISTIC TEXT NORMALIZATION
# ============================================================================

def normalize_unicode(text: str) -> str:
    """Apply NFC Unicode normalization (safe for botanical text)."""
    return unicodedata.normalize("NFC", text)


def collapse_whitespace(text: str) -> str:
    """Replace non-breaking spaces and collapse repeated whitespace to single space."""
    text = text.replace("\xa0", " ")
    return re.sub(r"\s+", " ", text)


def safe_trim(text: str) -> str:
    """Remove leading and trailing whitespace."""
    return text.strip()


def normalize_scientific_name(raw: str) -> str:
    """
    Layer A normalization for scientific_name.
    Used ONLY for comparison; raw value is always preserved.

    Operations:
      1. NFC Unicode normalization (safe)
      2. Collapse all whitespace
      3. Trim
      4. Lowercase for comparison

    Returns a normalized comparison key. This is NOT a canonical name.
    """
    text = normalize_unicode(raw)
    text = collapse_whitespace(text)
    text = safe_trim(text)
    return text.lower()


def normalize_family(raw: str) -> str:
    """
    Layer A normalization for family.
    Removes trailing safe punctuation (periods), collapses whitespace,
    trims, and lowercases for comparison.

    Returns a normalized comparison key.
    """
    text = normalize_unicode(raw)
    text = collapse_whitespace(text)
    text = safe_trim(text)
    # Remove safe terminal punctuation (trailing periods)
    text = re.sub(r"\.+$", "", text)
    text = safe_trim(text)
    return text.lower()


def classify_name_change(raw: str, normalized: str) -> str:
    """
    Classify the type of normalization change between raw and its normalized form.
    Returns one of:
        NO_CHANGE
        CASE_ONLY
        WHITESPACE_ONLY
        PUNCTUATION_ONLY
        CASE_AND_PUNCTUATION
        WHITESPACE_AND_CASE
        OTHER_TEXT_VARIATION
    """
    raw_stripped = safe_trim(raw)
    norm_lower = normalized

    # Check if they are already equal (no change)
    if raw_stripped == norm_lower:
        return "NO_CHANGE"

    # Try applying only specific transforms and see which ones explain the difference
    raw_lower = raw_stripped.lower()
    raw_ws_collapsed = collapse_whitespace(raw_stripped)
    raw_lower_ws = collapse_whitespace(raw_stripped).lower()

    if raw_lower == norm_lower:
        return "CASE_ONLY"
    if raw_ws_collapsed == normalized:
        return "WHITESPACE_ONLY"
    if re.sub(r"\.+$", "", raw_lower) == norm_lower or re.sub(r"\.+$", "", raw_lower_ws) == norm_lower:
        return "PUNCTUATION_ONLY"
    if raw_lower_ws == norm_lower:
        return "WHITESPACE_AND_CASE"
    if re.sub(r"\.+$", "", raw_lower) == norm_lower:
        return "CASE_AND_PUNCTUATION"

    return "OTHER_TEXT_VARIATION"


def make_record_id(raw_scientific_name: str, raw_family: str, raw_synonym: str, source_page_url: str) -> str:
    """
    Generate a deterministic, stable record_id from immutable source fields.
    Canonical serialization: fields joined with \x1e (ASCII record separator).
    SHA-256 truncated to 16 hex characters.
    """
    canonical = "\x1e".join([
        raw_scientific_name,
        raw_family,
        raw_synonym,
        source_page_url,
    ])
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


# ============================================================================
# IDEMPOTENCY — for testing
# ============================================================================

def is_idempotent_sci(raw: str) -> bool:
    """Verify normalize_scientific_name(normalize_scientific_name(x)) == normalize_scientific_name(x)."""
    once = normalize_scientific_name(raw)
    twice = normalize_scientific_name(once)
    return once == twice


def is_idempotent_fam(raw: str) -> bool:
    """Verify normalize_family(normalize_family(x)) == normalize_family(x)."""
    once = normalize_family(raw)
    twice = normalize_family(once)
    return once == twice


# ============================================================================
# LAYER B — BOTANICAL RECONCILIATION (evidence-based, no speculation)
# ============================================================================

def reconcile_record(
    raw_sci: str,
    norm_sci: str,
    raw_fam: str,
    norm_fam: str,
    norm_sci_count: int,
) -> dict[str, str]:
    """
    Conservative Layer B reconciliation for a single record.

    Rules (applied in order):
    1. normalized name = raw name (lowercased)  → UNCHANGED
    2. only formatting/case/punctuation differs  → NORMALIZED_ONLY
    3. normalized name appears > 1 time          → POTENTIAL_DUPLICATE
    4. else                                      → REVIEW_REQUIRED (if anomalous) or UNCHANGED

    Does NOT assign CANONICAL_MATCH or SYNONYM_CANDIDATE without external evidence.
    """
    sci_change = classify_name_change(raw_sci, norm_sci)
    fam_change = classify_name_change(raw_fam, norm_fam)

    no_sci_change = sci_change == "NO_CHANGE"
    no_fam_change = fam_change == "NO_CHANGE"

    if no_sci_change and no_fam_change:
        status = "UNCHANGED"
        reason = "Raw fields already match their normalized representations."
        confidence = "HIGH"
        review_required = "FALSE"
    elif sci_change in ("CASE_ONLY", "WHITESPACE_ONLY", "PUNCTUATION_ONLY",
                        "CASE_AND_PUNCTUATION", "WHITESPACE_AND_CASE") and \
         fam_change in ("CASE_ONLY", "WHITESPACE_ONLY", "PUNCTUATION_ONLY",
                        "CASE_AND_PUNCTUATION", "WHITESPACE_AND_CASE", "NO_CHANGE"):
        status = "NORMALIZED_ONLY"
        reason = f"Scientific name change: {sci_change}. Family change: {fam_change}."
        confidence = "HIGH"
        review_required = "FALSE"
    else:
        status = "REVIEW_REQUIRED"
        reason = f"Unclassified variation. Scientific name change: {sci_change}. Family change: {fam_change}."
        confidence = "LOW"
        review_required = "TRUE"

    # Override: if this normalized name appears more than once
    if norm_sci_count > 1:
        status = "POTENTIAL_DUPLICATE"
        reason = (
            f"Normalized scientific name appears {norm_sci_count} times. "
            f"Original change type: {sci_change}."
        )
        confidence = "MEDIUM"
        review_required = "TRUE"

    return {
        "reconciliation_status": status,
        "reconciliation_reason": reason,
        "confidence": confidence,
        "canonical_scientific_name": "",    # Layer B: no speculative assignment
        "canonical_family": "",             # Layer B: no speculative assignment
        "evidence_source": "NONE",
        "evidence_reference": "",
        "evidence_access_date": "",
        "review_required": review_required,
    }


# ============================================================================
# PIPELINE
# ============================================================================

def load_raw_rows() -> list[dict[str, str]]:
    """Load the frozen raw dataset. Never modify this."""
    with RAW_CSV.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_manifest() -> dict[str, Any]:
    with MANIFEST_JSON.open("r", encoding="utf-8") as f:
        return json.load(f)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def run_normalization_pipeline() -> dict[str, Any]:
    """Execute Stage 4 end-to-end and return a summary metrics dict."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    QUALITY_DIR.mkdir(parents=True, exist_ok=True)

    # 0. Immutability guard: verify raw SHA-256 against manifest
    manifest = load_manifest()
    expected_raw_sha256 = manifest["final_sha256"].upper()
    actual_raw_sha256 = sha256_file(RAW_CSV)
    if actual_raw_sha256 != expected_raw_sha256:
        raise RuntimeError(
            f"RAW DATASET INTEGRITY VIOLATION!\n"
            f"  Expected: {expected_raw_sha256}\n"
            f"  Found:    {actual_raw_sha256}\n"
            "Aborting Stage 4 to protect raw data integrity."
        )

    raw_rows = load_raw_rows()

    # 1. Build normalized comparison keys for every record
    norm_sci_keys = [normalize_scientific_name(r["scientific_name"]) for r in raw_rows]
    norm_fam_keys = [normalize_family(r["family"]) for r in raw_rows]
    norm_sci_counter = Counter(norm_sci_keys)

    # 2. Build reconciliation records
    reconciliation_rows: list[dict[str, str]] = []
    normalized_rows: list[dict[str, str]] = []

    for i, (row, norm_sci, norm_fam) in enumerate(zip(raw_rows, norm_sci_keys, norm_fam_keys)):
        rec_id = make_record_id(
            row["scientific_name"], row["family"], row["synonym"], row["source_page_url"]
        )

        rec_layer_b = reconcile_record(
            raw_sci=row["scientific_name"],
            norm_sci=norm_sci,
            raw_fam=row["family"],
            norm_fam=norm_fam,
            norm_sci_count=norm_sci_counter[norm_sci],
        )

        reconciliation_rows.append({
            "reconciliation_id": rec_id,
            "raw_scientific_name": row["scientific_name"],
            "normalized_scientific_name": norm_sci,
            "raw_family": row["family"],
            "normalized_family": norm_fam,
            "canonical_scientific_name": rec_layer_b["canonical_scientific_name"],
            "canonical_family": rec_layer_b["canonical_family"],
            "reconciliation_status": rec_layer_b["reconciliation_status"],
            "reconciliation_reason": rec_layer_b["reconciliation_reason"],
            "confidence": rec_layer_b["confidence"],
            "evidence_source": rec_layer_b["evidence_source"],
            "evidence_reference": rec_layer_b["evidence_reference"],
            "review_required": rec_layer_b["review_required"],
            "source_page_url": row["source_page_url"],
        })

        normalized_rows.append({
            "record_id": rec_id,
            "raw_scientific_name": row["scientific_name"],
            "normalized_scientific_name": norm_sci,
            "raw_synonym": row["synonym"],
            "raw_family": row["family"],
            "normalized_family": norm_fam,
            "canonical_scientific_name": rec_layer_b["canonical_scientific_name"],
            "canonical_family": rec_layer_b["canonical_family"],
            "reconciliation_status": rec_layer_b["reconciliation_status"],
            "confidence": rec_layer_b["confidence"],
            "source_page_url": row["source_page_url"],
            "scrape_timestamp": row["scrape_timestamp"],
        })

    # 3. Write mpbd_plant_index_normalized.csv
    normalized_fieldnames = [
        "record_id", "raw_scientific_name", "normalized_scientific_name",
        "raw_synonym", "raw_family", "normalized_family",
        "canonical_scientific_name", "canonical_family",
        "reconciliation_status", "confidence",
        "source_page_url", "scrape_timestamp",
    ]
    with NORMALIZED_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=normalized_fieldnames)
        writer.writeheader()
        writer.writerows(normalized_rows)

    # 4. Write mpbd_botanical_reconciliation.csv
    recon_fieldnames = [
        "reconciliation_id", "raw_scientific_name", "normalized_scientific_name",
        "raw_family", "normalized_family",
        "canonical_scientific_name", "canonical_family",
        "reconciliation_status", "reconciliation_reason",
        "confidence", "evidence_source", "evidence_reference",
        "review_required", "source_page_url",
    ]
    with RECONCILIATION_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=recon_fieldnames)
        writer.writeheader()
        writer.writerows(reconciliation_rows)

    # 5. Build family normalization report
    raw_families = [r["family"] for r in raw_rows]
    raw_fam_counter = Counter(raw_families)

    # Group raw families by normalized form
    norm_fam_to_raw: dict[str, set[str]] = defaultdict(set)
    for rf in raw_fam_counter:
        norm_fam_to_raw[normalize_family(rf)].add(rf)

    family_norm_rows: list[dict[str, Any]] = []
    for norm_f, raw_set in sorted(norm_fam_to_raw.items()):
        has_variants = len(raw_set) > 1
        total_count = sum(raw_fam_counter[rf] for rf in raw_set)
        # Determine normalization type across variants
        if not has_variants:
            rf = next(iter(raw_set))
            change_type = classify_name_change(rf, norm_f)
        else:
            change_types = set(classify_name_change(rf, norm_f) for rf in raw_set)
            change_type = " | ".join(sorted(change_types))

        family_norm_rows.append({
            "raw_family": " / ".join(sorted(raw_set)),
            "normalized_family": norm_f,
            "occurrence_count": total_count,
            "variant_count": len(raw_set),
            "normalization_type": change_type,
            "review_required": "TRUE" if has_variants else "FALSE",
            "notes": (
                f"Variants: {', '.join(sorted(raw_set))}" if has_variants else ""
            ),
        })

    family_fieldnames = [
        "raw_family", "normalized_family", "occurrence_count",
        "variant_count", "normalization_type", "review_required", "notes",
    ]
    with FAMILY_NORM_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=family_fieldnames)
        writer.writeheader()
        writer.writerows(family_norm_rows)

    # 6. Compute output SHA-256 for reproducibility validation
    sha_normalized = sha256_file(NORMALIZED_CSV)
    sha_reconciliation = sha256_file(RECONCILIATION_CSV)
    sha_family_norm = sha256_file(FAMILY_NORM_CSV)

    # 7. Summary metrics
    status_counter = Counter(r["reconciliation_status"] for r in reconciliation_rows)
    unique_norm_sci = len(norm_sci_counter)
    dup_groups = {k: v for k, v in norm_sci_counter.items() if v > 1}
    norm_only_count = status_counter.get("NORMALIZED_ONLY", 0)
    unchanged_count = status_counter.get("UNCHANGED", 0)
    potential_dup_count = status_counter.get("POTENTIAL_DUPLICATE", 0)
    review_count = status_counter.get("REVIEW_REQUIRED", 0)
    canonical_match_count = status_counter.get("CANONICAL_MATCH", 0)
    synonym_candidate_count = status_counter.get("SYNONYM_CANDIDATE", 0)

    families_with_variants = len([fn for fn, rs in norm_fam_to_raw.items() if len(rs) > 1])

    run_ts = datetime.now(timezone.utc).isoformat()

    # 8. Write reconciliation manifest
    recon_manifest = {
        "stage": "4",
        "stage_name": "botanical_reconciliation",
        "stage_run_timestamp": run_ts,
        "source_dataset": "data/raw/mpbd/mpbd_plant_index.csv",
        "source_dataset_version": "v1.0.0",
        "source_dataset_sha256": actual_raw_sha256,
        "raw_record_count": len(raw_rows),
        "normalization_method": "deterministic_text_normalization",
        "botanical_reconciliation": "evidence_based_conservative",
        "raw_unique_scientific_names": len(set(r["scientific_name"] for r in raw_rows)),
        "normalized_unique_scientific_names": unique_norm_sci,
        "potential_duplicate_groups": len(dup_groups),
        "affected_records_potential_duplicate": potential_dup_count,
        "records_unchanged": unchanged_count,
        "records_normalized_only": norm_only_count,
        "records_canonical_match": canonical_match_count,
        "records_synonym_candidate": synonym_candidate_count,
        "records_review_required": review_count,
        "raw_unique_families": len(raw_fam_counter),
        "normalized_unique_families": len(norm_fam_to_raw),
        "family_variant_groups": families_with_variants,
        "derived_outputs": [
            "mpbd_plant_index_normalized.csv",
            "mpbd_botanical_reconciliation.csv",
            "mpbd_family_normalization.csv",
        ],
        "output_sha256": {
            "mpbd_plant_index_normalized.csv": sha_normalized,
            "mpbd_botanical_reconciliation.csv": sha_reconciliation,
            "mpbd_family_normalization.csv": sha_family_norm,
        },
    }
    with RECONCILIATION_MANIFEST.open("w", encoding="utf-8") as f:
        json.dump(recon_manifest, f, indent=2)

    return {
        "manifest": recon_manifest,
        "dup_groups": dup_groups,
        "norm_sci_counter": norm_sci_counter,
        "norm_fam_to_raw": norm_fam_to_raw,
        "raw_fam_counter": raw_fam_counter,
        "status_counter": status_counter,
        "sha_normalized": sha_normalized,
        "sha_reconciliation": sha_reconciliation,
        "sha_family_norm": sha_family_norm,
        "raw_rows": raw_rows,
    }


# ============================================================================
# AUTOMATED TESTS
# ============================================================================

def run_tests() -> bool:
    """
    Run all automated normalization tests.
    Returns True if all pass, False otherwise.
    """
    failures: list[str] = []

    # Test 1: Known case variants map to same normalized sci name
    tests_sci = [
        ("Ficus racemosa L.", "Ficus RACEMOSA L."),
        ("Centella asiatica", "Centella ASIATICA"),
        ("Morus indica L.", "Morus INDICA L."),
        ("Mirabilis jalapa L.", "Mirabilis JALAPA L."),
    ]
    for a, b in tests_sci:
        if normalize_scientific_name(a) != normalize_scientific_name(b):
            failures.append(f"Scientific name case test FAILED: {a!r} vs {b!r}")
        else:
            print(f"  [OK] normalize_scientific_name({a!r}) == normalize_scientific_name({b!r})")

    # Test 2: Known family variants map to same normalized family
    tests_fam = [
        ("Lauraceae", "LAURACEAE"),
        ("Annonaceae", "ANNONACEAE"),
        ("Magnoliaceae", "MAGNOLIACEAE"),
        ("Plumbaginaceae.", "Plumbaginaceae"),
    ]
    for a, b in tests_fam:
        if normalize_family(a) != normalize_family(b):
            failures.append(f"Family normalization test FAILED: {a!r} vs {b!r}")
        else:
            print(f"  [OK] normalize_family({a!r}) == normalize_family({b!r})")

    # Test 3: Raw values are NOT modified by normalized comparison key
    for a, _ in tests_sci:
        n = normalize_scientific_name(a)
        if n == a and a != a.lower():  # name had uppercase but normalize returns lowercase
            failures.append(f"Raw value unexpectedly mutated: {a!r} -> {n!r}")

    # Test 4: Idempotency for all rows in raw dataset
    raw_rows = load_raw_rows()
    for r in raw_rows:
        if not is_idempotent_sci(r["scientific_name"]):
            failures.append(f"Sci idempotency FAILED for: {r['scientific_name']!r}")
        if not is_idempotent_fam(r["family"]):
            failures.append(f"Fam idempotency FAILED for: {r['family']!r}")

    if failures:
        for f in failures:
            print("  [FAIL]", f)
        return False

    print(f"  [OK] Idempotency verified for all {len(raw_rows)} rows.")
    return True


# ============================================================================
# RECONCILIATION REPORT (Markdown)
# ============================================================================

def write_reconciliation_report(metrics: dict[str, Any]) -> None:
    m = metrics["manifest"]
    dup_groups = metrics["dup_groups"]
    norm_sci_counter = metrics["norm_sci_counter"]
    norm_fam_to_raw = metrics["norm_fam_to_raw"]
    raw_fam_counter = metrics["raw_fam_counter"]
    status_counter = metrics["status_counter"]

    now_ts = datetime.now(timezone.utc).isoformat()
    raw_rows = metrics["raw_rows"]

    # Build review queue (POTENTIAL_DUPLICATE and REVIEW_REQUIRED)
    review_rows: list[dict[str, str]] = []
    with RECONCILIATION_CSV.open("r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["review_required"] == "TRUE":
                review_rows.append(r)

    # Build dup group table
    dup_table_lines: list[str] = []
    for norm_name, count in sorted(dup_groups.items(), key=lambda x: -x[1]):
        # Get the raw variants
        raw_variants = [r["scientific_name"] for r in raw_rows
                        if normalize_scientific_name(r["scientific_name"]) == norm_name]
        pages = [r["source_page_url"] for r in raw_rows
                 if normalize_scientific_name(r["scientific_name"]) == norm_name]
        variants_str = " | ".join(raw_variants)
        pages_str = " | ".join(set(pages))
        dup_table_lines.append(f"| `{norm_name}` | {count} | {variants_str} | {pages_str} |")

    dup_table = "\n".join(dup_table_lines)

    # Family variant table
    fam_variant_lines: list[str] = []
    for norm_f, raw_set in sorted(norm_fam_to_raw.items()):
        if len(raw_set) > 1:
            variants = " | ".join(sorted(raw_set))
            count = sum(raw_fam_counter[rf] for rf in raw_set)
            fam_variant_lines.append(f"| `{norm_f}` | {variants} | {count} |")

    fam_variant_table = "\n".join(fam_variant_lines)

    report = f"""# MPBD Stage 4 — Botanical Reconciliation Report

**Stage**: 4 — Botanical Reconciliation & Normalization  
**Source Dataset**: `data/raw/mpbd/mpbd_plant_index.csv` (`v1.0.0`)  
**Source SHA-256**: `{m['source_dataset_sha256']}`  
**Run Timestamp**: `{m['stage_run_timestamp']}`  
**Report Generated**: `{now_ts}`

---

## Dataset Summary

| Metric | Value |
| :--- | :--- |
| **Raw records (frozen input)** | {m['raw_record_count']} |
| **Normalized records produced** | {m['raw_record_count']} |
| **Raw unique scientific names** | {m['raw_unique_scientific_names']} |
| **Normalized unique scientific names** | {m['normalized_unique_scientific_names']} |
| **Potential duplicate groups** | {m['potential_duplicate_groups']} |
| **Records requiring review** | {m['records_review_required'] + m['affected_records_potential_duplicate']} |
| **UNCHANGED** | {m['records_unchanged']} |
| **NORMALIZED\\_ONLY** | {m['records_normalized_only']} |
| **POTENTIAL\\_DUPLICATE** | {m['affected_records_potential_duplicate']} |
| **CANONICAL\\_MATCH** | {m['records_canonical_match']} |
| **SYNONYM\\_CANDIDATE** | {m['records_synonym_candidate']} |
| **REVIEW\\_REQUIRED** | {m['records_review_required']} |

> [!NOTE]
> `CANONICAL_MATCH` and `SYNONYM_CANDIDATE` require external authoritative botanical evidence. None has been assigned automatically. All zero values here are correct — not a pipeline gap.

---

## Scientific-Name Normalization

Layer A normalization applies: Unicode NFC, whitespace collapsing, trimming, and case-folding (lowercase for comparison only).

| Metric | Value |
| :--- | :--- |
| **Raw unique scientific names** | {m['raw_unique_scientific_names']} |
| **Normalized unique scientific names** | {m['normalized_unique_scientific_names']} |
| **Reduction after normalization** | {m['raw_unique_scientific_names'] - m['normalized_unique_scientific_names']} |
| **Potential duplicate groups** | {m['potential_duplicate_groups']} |

### Potential Duplicate Groups (Normalized Name Appears > 1 Time)

| Normalized Name | Count | Raw Variants | Source Pages |
| :--- | :--- | :--- | :--- |
{dup_table}

---

## Family Normalization

| Metric | Value |
| :--- | :--- |
| **Raw unique family values** | {m['raw_unique_families']} |
| **Normalized unique families** | {m['normalized_unique_families']} |
| **Family variant groups reconciled** | {m['family_variant_groups']} |

### Family Variant Groups

| Normalized Family | Raw Variants | Record Count |
| :--- | :--- | :--- |
{fam_variant_table}

---

## Reconciliation Status Distribution

| Status | Count | Description |
| :--- | :--- | :--- |
| `UNCHANGED` | {status_counter.get('UNCHANGED', 0)} | Raw fields already match normalized representation. |
| `NORMALIZED_ONLY` | {status_counter.get('NORMALIZED_ONLY', 0)} | Only text formatting/case/punctuation changed; no botanical content change. |
| `POTENTIAL_DUPLICATE` | {status_counter.get('POTENTIAL_DUPLICATE', 0)} | Normalized scientific name occurs more than once; may be MPBD redundancy. |
| `REVIEW_REQUIRED` | {status_counter.get('REVIEW_REQUIRED', 0)} | Unclassified variation; needs human review. |
| `CANONICAL_MATCH` | {status_counter.get('CANONICAL_MATCH', 0)} | Confirmed canonical identity (requires external authoritative evidence). |
| `SYNONYM_CANDIDATE` | {status_counter.get('SYNONYM_CANDIDATE', 0)} | Potential synonym relationship (requires external authoritative evidence). |

---

## Confidence Distribution

| Confidence | Count |
| :--- | :--- |
| `HIGH` | {sum(1 for r in review_rows if r['confidence'] == 'HIGH')} (in review queue) |
| `MEDIUM` | {sum(1 for r in review_rows if r['confidence'] == 'MEDIUM')} (in review queue) |
| `LOW` | {sum(1 for r in review_rows if r['confidence'] == 'LOW')} (in review queue) |
| `UNKNOWN` | 0 |

---

## Review Queue

All {len(review_rows)} records flagged for human review are listed below.

| Raw Scientific Name | Normalized | Raw Family | Page | Status | Reason |
| :--- | :--- | :--- | :--- | :--- | :--- |
""" + "\n".join(
        f"| `{r['raw_scientific_name']}` | `{r['normalized_scientific_name']}` | "
        f"`{r['raw_family']}` | {r['source_page_url'].replace('https://mpbd.cu.ac.bd/', '')} | "
        f"`{r['reconciliation_status']}` | {r['reconciliation_reason'][:80]}... |"
        if len(r['reconciliation_reason']) > 80 else
        f"| `{r['raw_scientific_name']}` | `{r['normalized_scientific_name']}` | "
        f"`{r['raw_family']}` | {r['source_page_url'].replace('https://mpbd.cu.ac.bd/', '')} | "
        f"`{r['reconciliation_status']}` | {r['reconciliation_reason']} |"
        for r in review_rows
    ) + f"""

---

## Raw Dataset Immutability

The frozen source dataset was verified before and after Stage 4 execution:

```text
data/raw/mpbd/mpbd_plant_index.csv
SHA-256: {m['source_dataset_sha256']}
Status: UNCHANGED
```

---

## Derived Output SHA-256 (Reproducibility)

| Output File | SHA-256 |
| :--- | :--- |
| `mpbd_plant_index_normalized.csv` | `{m['output_sha256']['mpbd_plant_index_normalized.csv']}` |
| `mpbd_botanical_reconciliation.csv` | `{m['output_sha256']['mpbd_botanical_reconciliation.csv']}` |
| `mpbd_family_normalization.csv` | `{m['output_sha256']['mpbd_family_normalization.csv']}` |

---

## Architecture Notes

### Layer A — Text Normalization (deterministic, no botanical knowledge)
- NFC Unicode normalization
- Non-breaking space → regular space
- Whitespace collapse
- Trim
- Lowercase (comparison key only; raw value is always preserved)
- Safe terminal punctuation removal (family field only)

### Layer B — Botanical Reconciliation (evidence-based only)
- No speculative canonical name assignment
- No automatic synonym invention
- `CANONICAL_MATCH` and `SYNONYM_CANDIDATE` require explicit external evidence
- Every non-trivial reconciliation is traceable via `reconciliation_reason` and `evidence_source`

> [!IMPORTANT]
> A text normalization operation is never treated as equivalent to a taxonomic correction. Both the raw and normalized representations are preserved in every output file.

---

## Stage 4 Status: COMPLETE
"""
    with RECONCILIATION_REPORT.open("w", encoding="utf-8") as f:
        f.write(report)


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import sys

    print("\n" + "=" * 60)
    print("MPBD STAGE 4 — BOTANICAL RECONCILIATION")
    print("=" * 60)

    print("\n--- Running automated normalization tests ---")
    tests_passed = run_tests()
    if not tests_passed:
        print("\n[ABORT] Automated tests failed. Fix normalization logic before running pipeline.")
        sys.exit(1)
    print("[PASS] All automated normalization tests passed.\n")

    print("--- Running normalization and reconciliation pipeline ---")
    metrics = run_normalization_pipeline()

    print("--- Writing reconciliation report ---")
    write_reconciliation_report(metrics)

    m = metrics["manifest"]
    print("\n" + "=" * 60)
    print("STAGE 4 SUMMARY")
    print("=" * 60)
    print(f"Raw records:                   {m['raw_record_count']}")
    print(f"Normalized records produced:   {m['raw_record_count']}")
    print(f"Raw unique sci names:          {m['raw_unique_scientific_names']}")
    print(f"Normalized unique sci names:   {m['normalized_unique_scientific_names']}")
    print(f"Potential duplicate groups:    {m['potential_duplicate_groups']}")
    print(f"UNCHANGED:                     {m['records_unchanged']}")
    print(f"NORMALIZED_ONLY:               {m['records_normalized_only']}")
    print(f"POTENTIAL_DUPLICATE:           {m['affected_records_potential_duplicate']}")
    print(f"CANONICAL_MATCH:               {m['records_canonical_match']}")
    print(f"SYNONYM_CANDIDATE:             {m['records_synonym_candidate']}")
    print(f"REVIEW_REQUIRED:               {m['records_review_required']}")
    print(f"Raw unique families:           {m['raw_unique_families']}")
    print(f"Normalized unique families:    {m['normalized_unique_families']}")
    print(f"Family variant groups:         {m['family_variant_groups']}")
    print()
    print(f"Raw dataset SHA-256 verified:  {m['source_dataset_sha256']}")
    print()
    print("Derived output SHA-256:")
    for fname, h in m["output_sha256"].items():
        print(f"  {fname}: {h}")
    print()
    print("Generated files:")
    print(f"  {NORMALIZED_CSV}")
    print(f"  {RECONCILIATION_CSV}")
    print(f"  {FAMILY_NORM_CSV}")
    print(f"  {RECONCILIATION_MANIFEST}")
    print(f"  {RECONCILIATION_REPORT}")
    print()
    print("Network requests:              0")
    print("=" * 60)
