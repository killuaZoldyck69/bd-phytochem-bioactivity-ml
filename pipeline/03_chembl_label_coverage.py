#!/usr/bin/env python3
"""
Stage 7A - Pipeline Step 3: ChEMBL Bioactivity Label Feasibility Assessment

Reads:
  - data/raw/mpbd/mpbd_plant_index.csv (Frozen master; verified against manifest)
  - data/processed/compounds/compounds_unique.csv (Step 2 standardized molecules)
  - data/processed/compounds/plant_compound_links.csv (Provenance links plant <-> compound)
  - ChEMBL SQLite database (Read-only, default: F:/datasets/chembl_37/chembl_37_sqlite/chembl_37.db)

Produces:
  - data/cache/chembl/chembl37_connectivity_lookup.csv (Cached 14-char connectivity lookup)
  - data/processed/compounds/compound_chembl_match.csv (Connectivity matching & activity counts)
  - data/processed/compounds/compound_bioactivity_raw.csv (Granular usable/strict activity records)
  - data/attrition/chembl_matching_attrition.csv (Step-by-step matching attrition)
  - data/quality/label_feasibility_report.md (Comprehensive label feasibility report)

Safeguards & Rules:
  - ChEMBL database is opened READ-ONLY (mode=ro, uri=True). Never writes or indexes.
  - Verifies SHA-256 of master MPBD index at start and end.
  - Matches compounds strictly at the 14-character connectivity layer.
  - Aggregates all ChEMBL molregnos sharing connectivity layer for each molecule.
  - Strictly distinguishes ALL vs USABLE vs STRICT activity criteria.
"""

import argparse
from collections import Counter, defaultdict
import csv
import datetime
import hashlib
import json
import logging
import os
from pathlib import Path
import random
import sys
import time
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd
import sqlite3

# ---------------------------------------------------------------------------
# Setup Logging
# ---------------------------------------------------------------------------
def setup_logging(log_file: Path) -> logging.Logger:
    logger = logging.getLogger("chembl_coverage")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    log_file.parent.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


# ---------------------------------------------------------------------------
# Master Manifest Integrity Check
# ---------------------------------------------------------------------------
def verify_master_manifest(logger: logging.Logger) -> str:
    master_path = Path("data/raw/mpbd/mpbd_plant_index.csv")
    manifest_path = Path("data/processed/mpbd/mpbd_reconciliation_manifest.json")

    if not master_path.exists():
        raise FileNotFoundError(f"Master index missing: {master_path}")

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    expected_sha256 = manifest.get("source_dataset_sha256") or manifest.get("final_sha256")

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
# ChEMBL Database Helpers
# ---------------------------------------------------------------------------
def get_chembl_version_info(conn: sqlite3.Connection) -> Tuple[str, str]:
    c = conn.cursor()
    c.execute("SELECT name, creation_date FROM version WHERE name LIKE 'ChEMBL_%' LIMIT 1")
    row = c.fetchone()
    if row:
        return row[0], str(row[1])
    return "Unknown_ChEMBL", "Unknown_Date"


def get_or_build_connectivity_lookup(
    conn: sqlite3.Connection,
    cache_path: Path,
    logger: logging.Logger
) -> pd.DataFrame:
    if cache_path.exists():
        logger.info(f"Loading cached ChEMBL connectivity lookup from: {cache_path}")
        t0 = time.time()
        df_lookup = pd.read_csv(
            cache_path,
            dtype={"molregno": np.int64, "connectivity": str},
            usecols=["molregno", "connectivity"]
        )
        logger.info(f"Loaded {len(df_lookup):,} rows from cache in {time.time()-t0:.2f}s")
        return df_lookup

    logger.info(f"Building ChEMBL connectivity lookup from compound_structures table...")
    t0 = time.time()
    query = "SELECT molregno, standard_inchi_key FROM compound_structures WHERE standard_inchi_key IS NOT NULL"
    df_raw = pd.read_sql_query(query, conn)
    logger.info(f"Read {len(df_raw):,} compound_structures in {time.time()-t0:.2f}s")

    df_raw["connectivity"] = df_raw["standard_inchi_key"].str[:14]
    df_lookup = df_raw[["molregno", "connectivity"]].dropna()

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Saving connectivity lookup to cache: {cache_path}")
    t0 = time.time()
    df_lookup.to_csv(cache_path, index=False)
    logger.info(f"Saved lookup cache in {time.time()-t0:.2f}s")

    return df_lookup


# ---------------------------------------------------------------------------
# Main Orchestration
# ---------------------------------------------------------------------------
def run_chembl_label_coverage(
    sqlite_path: str = r"F:\datasets\chembl_37\chembl_37_sqlite\chembl_37.db",
    limit: Optional[int] = None,
    seed: int = 42,
    output_dir: Optional[Path] = None,
):
    log_file = Path("data/quality/chembl_label_coverage.log")
    logger = setup_logging(log_file)
    logger.info("=" * 70)
    logger.info("STAGE 7A: ChEMBL Label Coverage Assessment (Script 03)")
    logger.info(f"Execution Timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}")
    logger.info(f"SQLite Path: {sqlite_path}")
    logger.info(f"Parameters: limit={limit}, seed={seed}, output_dir={output_dir}")
    logger.info("=" * 70)

    start_time = time.time()

    # 1. Master integrity check at start
    start_hash = verify_master_manifest(logger)

    # 2. Connect to ChEMBL in read-only mode
    db_uri = f"file:{sqlite_path.replace(os.sep, '/')}?mode=ro"
    logger.info(f"Connecting to ChEMBL database (READ-ONLY): {db_uri}")
    conn = sqlite3.connect(db_uri, uri=True)

    release_name, release_date = get_chembl_version_info(conn)
    logger.info(f"ChEMBL Release: {release_name} | Creation Date: {release_date}")

    # 3. Load or build connectivity lookup table
    cache_lookup_path = Path("data/cache/chembl/chembl37_connectivity_lookup.csv")
    df_lookup = get_or_build_connectivity_lookup(conn, cache_lookup_path, logger)

    # 4. Load unique compounds
    unique_compounds_file = Path("data/processed/compounds/compounds_unique.csv")
    if not unique_compounds_file.exists():
        raise FileNotFoundError(f"Unique compounds file missing: {unique_compounds_file}")

    df_compounds = pd.read_csv(unique_compounds_file)
    total_compounds_input = len(df_compounds)
    logger.info(f"Loaded {total_compounds_input:,} unique compounds from {unique_compounds_file}")

    # Curated flag
    df_compounds["is_curated"] = ~(
        df_compounds["is_inorganic"].astype(bool)
        | df_compounds["too_small"].astype(bool)
        | df_compounds["too_large"].astype(bool)
        | df_compounds["is_mixture"].astype(bool)
    )

    # Sample support if limit specified
    if limit is not None and limit < total_compounds_input:
        logger.info(f"Sampling {limit} molecules with random seed {seed}")
        df_compounds = df_compounds.sample(n=limit, random_state=seed).copy()
        if output_dir is None:
            output_dir = Path("data/processed/compounds/sample")

    if output_dir is None:
        output_dir = Path("data/processed/compounds")

    output_dir.mkdir(parents=True, exist_ok=True)

    # 5. Build connectivity -> molregno map
    # Only keep lookup entries that match our target connectivity layers to save memory
    target_connectivities = set(df_compounds["inchikey_connectivity"].dropna().unique())
    logger.info(f"Target unique connectivity layers to match: {len(target_connectivities):,}")

    df_matched_lookup = df_lookup[df_lookup["connectivity"].isin(target_connectivities)].copy()
    logger.info(f"Found {len(df_matched_lookup):,} ChEMBL structure matches for target connectivities")

    # Map connectivity -> list of molregnos
    conn_to_molregnos: Dict[str, List[int]] = defaultdict(list)
    for row in df_matched_lookup.itertuples(index=False):
        conn_to_molregnos[row.connectivity].append(row.molregno)

    all_matched_molregnos = set(df_matched_lookup["molregno"].unique())
    logger.info(f"Total distinct ChEMBL molregnos matched: {len(all_matched_molregnos):,}")

    # 6. Fetch metadata from molecule_dictionary for matched molregnos
    logger.info("Fetching chembl_id and natural_product flags from molecule_dictionary...")
    molregno_to_info: Dict[int, Dict] = {}
    if all_matched_molregnos:
        cursor = conn.cursor()
        cursor.execute("CREATE TEMP TABLE temp_target_mols (molregno INTEGER PRIMARY KEY)")
        cursor.executemany("INSERT INTO temp_target_mols VALUES (?)", [(int(m),) for m in all_matched_molregnos])
        
        cursor.execute("""
            SELECT m.molregno, m.chembl_id, m.natural_product
            FROM temp_target_mols tm
            JOIN molecule_dictionary m ON tm.molregno = m.molregno
        """)
        for m_reg, c_id, np_flag in cursor.fetchall():
            molregno_to_info[m_reg] = {
                "chembl_id": c_id,
                "natural_product": int(np_flag) if np_flag is not None else 0
            }
        logger.info(f"Retrieved dictionary metadata for {len(molregno_to_info):,} molregnos")

    # 7. Fetch all activity records for matched molregnos
    logger.info("Querying activity records and assay/target metadata from ChEMBL...")
    t0 = time.time()
    activity_query = """
        SELECT 
            a.activity_id,
            a.assay_id,
            a.doc_id,
            a.molregno,
            a.standard_relation,
            a.standard_value,
            a.standard_units,
            a.standard_type,
            a.potential_duplicate,
            a.data_validity_comment,
            a.pchembl_value,
            ass.chembl_id AS assay_chembl_id,
            ass.assay_type,
            ass.confidence_score,
            ass.tid,
            td.chembl_id AS target_chembl_id,
            td.pref_name AS target_pref_name,
            td.target_type,
            td.organism
        FROM temp_target_mols tm
        JOIN activities a ON tm.molregno = a.molregno
        LEFT JOIN assays ass ON a.assay_id = ass.assay_id
        LEFT JOIN target_dictionary td ON ass.tid = td.tid
    """
    df_activities = pd.read_sql_query(activity_query, conn)
    logger.info(f"Retrieved {len(df_activities):,} raw activity records in {time.time()-t0:.2f}s")

    # Invert mapping: molregno -> connectivity layer
    molregno_to_conn: Dict[int, str] = {}
    for conn_key, mol_list in conn_to_molregnos.items():
        for m in mol_list:
            molregno_to_conn[m] = conn_key

    df_activities["inchikey_connectivity"] = df_activities["molregno"].map(molregno_to_conn)
    df_activities["chembl_id"] = df_activities["molregno"].map(lambda m: molregno_to_info.get(m, {}).get("chembl_id", ""))

    # 8. Activity classification & filtering
    # Assay type distribution on ALL records
    assay_type_counts = df_activities["assay_type"].value_counts(dropna=False).to_dict()

    # Usable activity filter
    is_usable = (
        (df_activities["standard_relation"] == "=")
        & (df_activities["standard_value"].notnull())
        & (df_activities["standard_units"] == "nM")
        & (df_activities["standard_type"].isin(["IC50", "Ki", "Kd", "EC50"]))
        & (df_activities["potential_duplicate"] == 0)
        & (df_activities["data_validity_comment"].isna() | (df_activities["data_validity_comment"] == ""))
    )
    df_activities["is_usable"] = is_usable

    # Strict activity filter
    is_strict = (
        is_usable
        & (df_activities["assay_type"].isin(["B", "F"]))
        & (df_activities["confidence_score"].isin([8, 9]))
        & (df_activities["tid"].notnull())
    )
    df_activities["is_strict"] = is_strict

    total_activity_all = len(df_activities)
    total_activity_usable = int(is_usable.sum())
    total_activity_strict = int(is_strict.sum())
    logger.info(f"Activities: Total={total_activity_all:,} | Usable={total_activity_usable:,} | Strict={total_activity_strict:,}")

    # 9. Aggregate per-molecule activity counts
    mol_act_all_counts = df_activities.groupby("inchikey_connectivity").size().to_dict()
    mol_act_usable_counts = df_activities[df_activities["is_usable"]].groupby("inchikey_connectivity").size().to_dict()
    mol_act_strict_counts = df_activities[df_activities["is_strict"]].groupby("inchikey_connectivity").size().to_dict()

    # 10. Generate compound_chembl_match.csv
    match_rows = []
    for row in df_compounds.itertuples(index=False):
        conn_key = row.inchikey_connectivity
        mols = conn_to_molregnos.get(conn_key, [])
        n_mol = len(mols)
        c_ids = [molregno_to_info[m]["chembl_id"] for m in mols if m in molregno_to_info and molregno_to_info[m]["chembl_id"]]
        c_ids_str = "|".join(sorted(set(c_ids)))
        np_flag = any(molregno_to_info[m]["natural_product"] == 1 for m in mols if m in molregno_to_info)

        n_all = mol_act_all_counts.get(conn_key, 0)
        n_usable = mol_act_usable_counts.get(conn_key, 0)
        n_strict = mol_act_strict_counts.get(conn_key, 0)

        match_rows.append({
            "inchikey_connectivity": conn_key,
            "n_chembl_molregno": n_mol,
            "chembl_ids": c_ids_str,
            "chembl_natural_product_flag": np_flag,
            "n_activity_all": n_all,
            "n_activity_usable": n_usable,
            "n_activity_strict": n_strict
        })

    df_compound_match = pd.DataFrame(match_rows)
    match_output_file = output_dir / "compound_chembl_match.csv"
    df_compound_match.to_csv(match_output_file, index=False)
    logger.info(f"Saved compound match summary to: {match_output_file}")

    # 11. Generate compound_bioactivity_raw.csv (Usable records only)
    df_usable_activities = df_activities[df_activities["is_usable"]].copy()
    bioactivity_cols = [
        "inchikey_connectivity", "molregno", "chembl_id", "activity_id", "assay_id",
        "assay_chembl_id", "assay_type", "confidence_score", "target_chembl_id",
        "target_pref_name", "target_type", "organism", "standard_type",
        "standard_relation", "standard_value", "standard_units", "pchembl_value",
        "doc_id", "is_strict"
    ]
    df_bioactivity_raw = df_usable_activities[bioactivity_cols].copy()
    bioactivity_output_file = output_dir / "compound_bioactivity_raw.csv"
    df_bioactivity_raw.to_csv(bioactivity_output_file, index=False)
    logger.info(f"Saved {len(df_bioactivity_raw):,} usable bioactivity records to: {bioactivity_output_file}")

    # 12. Attrition calculation
    n_total_input = len(df_compounds)
    n_curated_input = int(df_compounds["is_curated"].sum())

    n_matched = int((df_compound_match["n_chembl_molregno"] > 0).sum())
    n_has_act_all = int((df_compound_match["n_activity_all"] > 0).sum())
    n_has_act_usable = int((df_compound_match["n_activity_usable"] > 0).sum())
    n_has_act_strict = int((df_compound_match["n_activity_strict"] > 0).sum())

    # Curated subset metrics
    df_curated_match = df_compound_match[df_compounds["is_curated"].values]
    n_curated_matched = int((df_curated_match["n_chembl_molregno"] > 0).sum())
    n_curated_has_act_all = int((df_curated_match["n_activity_all"] > 0).sum())
    n_curated_has_act_usable = int((df_curated_match["n_activity_usable"] > 0).sum())
    n_curated_has_act_strict = int((df_curated_match["n_activity_strict"] > 0).sum())

    attrition_rows = [
        {"step": "1_input_unique_molecules", "scope": "full", "count": n_total_input, "pct": 100.0, "notes": "Input connectivity layers"},
        {"step": "1_input_unique_molecules", "scope": "curated", "count": n_curated_input, "pct": (n_curated_input / n_total_input * 100.0) if n_total_input else 0.0, "notes": "Curated drug-like organic subset"},
        {"step": "2_matched_chembl_structure", "scope": "full", "count": n_matched, "pct": (n_matched / n_total_input * 100.0) if n_total_input else 0.0, "notes": "Shared 14-char connectivity layer"},
        {"step": "2_matched_chembl_structure", "scope": "curated", "count": n_curated_matched, "pct": (n_curated_matched / n_curated_input * 100.0) if n_curated_input else 0.0, "notes": "Curated matched to ChEMBL"},
        {"step": "3_has_any_activity_record", "scope": "full", "count": n_has_act_all, "pct": (n_has_act_all / n_total_input * 100.0) if n_total_input else 0.0, "notes": "At least 1 raw activity record"},
        {"step": "3_has_any_activity_record", "scope": "curated", "count": n_curated_has_act_all, "pct": (n_curated_has_act_all / n_curated_input * 100.0) if n_curated_input else 0.0, "notes": "Curated with raw activity"},
        {"step": "4_has_usable_activity_record", "scope": "full", "count": n_has_act_usable, "pct": (n_has_act_usable / n_total_input * 100.0) if n_total_input else 0.0, "notes": "Usable binding/functional (=, nM, IC50/Ki/Kd/EC50)"},
        {"step": "4_has_usable_activity_record", "scope": "curated", "count": n_curated_has_act_usable, "pct": (n_curated_has_act_usable / n_curated_input * 100.0) if n_curated_input else 0.0, "notes": "Curated with usable activity"},
        {"step": "5_has_strict_activity_record", "scope": "full", "count": n_has_act_strict, "pct": (n_has_act_strict / n_total_input * 100.0) if n_total_input else 0.0, "notes": "Strict single-protein target (conf 8-9, B/F)"},
        {"step": "5_has_strict_activity_record", "scope": "curated", "count": n_curated_has_act_strict, "pct": (n_curated_has_act_strict / n_curated_input * 100.0) if n_curated_input else 0.0, "notes": "Curated with strict activity"}
    ]
    df_attrition = pd.DataFrame(attrition_rows)
    attrition_file = Path("data/attrition/chembl_matching_attrition.csv") if output_dir == Path("data/processed/compounds") else output_dir / "chembl_matching_attrition.csv"
    attrition_file.parent.mkdir(parents=True, exist_ok=True)
    df_attrition.to_csv(attrition_file, index=False)
    logger.info(f"Saved attrition ledger to: {attrition_file}")

    # 13. Deep Analytical Breakdowns for Quality Report
    # Molregno match distribution (1, 2-5, >5)
    matched_only = df_compound_match[df_compound_match["n_chembl_molregno"] > 0]
    n_mol_dist = {
        "1": int((matched_only["n_chembl_molregno"] == 1).sum()),
        "2-5": int(((matched_only["n_chembl_molregno"] >= 2) & (matched_only["n_chembl_molregno"] <= 5)).sum()),
        ">5": int((matched_only["n_chembl_molregno"] > 5).sum()),
    }

    # Natural product flag
    n_np_flag = int(df_compound_match["chembl_natural_product_flag"].sum())

    # Usable records distribution per molecule
    usable_counts_series = df_compound_match[df_compound_match["n_activity_usable"] > 0]["n_activity_usable"]
    if len(usable_counts_series) > 0:
        usable_stats = {
            "min": int(usable_counts_series.min()),
            "q25": float(usable_counts_series.quantile(0.25)),
            "median": float(usable_counts_series.median()),
            "q75": float(usable_counts_series.quantile(0.75)),
            "max": int(usable_counts_series.max()),
            "bins": {
                "1": int((usable_counts_series == 1).sum()),
                "2-5": int(((usable_counts_series >= 2) & (usable_counts_series <= 5)).sum()),
                "6-20": int(((usable_counts_series >= 6) & (usable_counts_series <= 20)).sum()),
                ">20": int((usable_counts_series > 20).sum()),
            }
        }
    else:
        usable_stats = {"min": 0, "q25": 0, "median": 0, "q75": 0, "max": 0, "bins": {"1": 0, "2-5": 0, "6-20": 0, ">20": 0}}

    # Strict records dataframe
    df_strict = df_usable_activities[df_usable_activities["is_strict"]].copy()

    # Top 30 targets by distinct molecules tested (Strict set)
    target_mol_counts = (
        df_strict.groupby(["target_chembl_id", "target_pref_name", "target_type", "organism"])["inchikey_connectivity"]
        .nunique()
        .reset_index()
        .rename(columns={"inchikey_connectivity": "n_molecules"})
        .sort_values(by="n_molecules", ascending=False)
    )
    top30_targets = target_mol_counts.head(30)

    # Protein class mapping for strict targets
    logger.info("Querying protein classification for strict targets...")
    strict_tids = [int(t) for t in df_strict["tid"].dropna().unique()]
    tid_to_classes: Dict[int, List[str]] = defaultdict(list)
    protein_class_counts: Counter = Counter()

    if strict_tids:
        cursor = conn.cursor()
        cursor.execute("CREATE TEMP TABLE temp_strict_tids (tid INTEGER PRIMARY KEY)")
        cursor.executemany("INSERT INTO temp_strict_tids VALUES (?)", [(int(t),) for t in strict_tids])
        
        class_query = """
            SELECT DISTINCT
                st.tid,
                pc.class_level,
                pc.pref_name AS class_pref_name,
                pc.short_name
            FROM temp_strict_tids st
            JOIN target_components tc ON st.tid = tc.tid
            JOIN component_class cc ON tc.component_id = cc.component_id
            JOIN protein_classification pc ON cc.protein_class_id = pc.protein_class_id
            WHERE pc.class_level = 1
        """
        cursor.execute(class_query)
        for t_id, c_lvl, c_pname, s_name in cursor.fetchall():
            tid_to_classes[t_id].append(c_pname)

        # Count distinct molecules per protein class (level 1)
        df_strict_tid = df_strict[["tid", "inchikey_connectivity"]].dropna().drop_duplicates()
        for row in df_strict_tid.itertuples(index=False):
            t_id = int(row.tid)
            classes = tid_to_classes.get(t_id, ["Unclassified"])
            for c_name in set(classes):
                protein_class_counts[c_name] += 1

    # Top 15 target analysis (pChEMBL thresholds & conflict reporting)
    top15_targets_df = target_mol_counts.head(15).copy()
    top15_details = []
    
    # Calculate median pChEMBL per (target, molecule) pair
    # If pchembl_value is null, calculate from standard_value (nM): -log10(value * 1e-9) = 9 - log10(value)
    df_strict_pchem = df_strict.copy()
    missing_pchem = df_strict_pchem["pchembl_value"].isna() & (df_strict_pchem["standard_value"] > 0)
    df_strict_pchem.loc[missing_pchem, "pchembl_value"] = 9.0 - np.log10(df_strict_pchem.loc[missing_pchem, "standard_value"])

    for row in top15_targets_df.itertuples(index=False):
        t_chembl_id = row.target_chembl_id
        t_name = row.target_pref_name
        t_records = df_strict_pchem[df_strict_pchem["target_chembl_id"] == t_chembl_id]
        
        # Group by molecule to find median pChEMBL and check conflicts
        mol_medians = t_records.groupby("inchikey_connectivity")["pchembl_value"].median()
        
        # Check conflicts: within a molecule-target pair, are some >= 6 and some < 6?
        conflicts_6 = 0
        conflicts_5 = 0
        for m_conn, group in t_records.groupby("inchikey_connectivity"):
            vals = group["pchembl_value"].dropna().values
            if len(vals) > 1:
                if any(v >= 6.0 for v in vals) and any(v < 6.0 for v in vals):
                    conflicts_6 += 1
                if any(v >= 5.0 for v in vals) and any(v < 5.0 for v in vals):
                    conflicts_5 += 1

        n_tested = len(mol_medians)
        n_act_6 = int((mol_medians >= 6.0).sum())
        n_inact_6 = n_tested - n_act_6
        n_act_5 = int((mol_medians >= 5.0).sum())
        n_inact_5 = n_tested - n_act_5

        top15_details.append({
            "target_chembl_id": t_chembl_id,
            "target_pref_name": t_name,
            "organism": row.organism,
            "n_tested": n_tested,
            "n_active_6": n_act_6,
            "n_inactive_6": n_inact_6,
            "n_conflicts_6": conflicts_6,
            "n_active_5": n_act_5,
            "n_inactive_5": n_inact_5,
            "n_conflicts_5": conflicts_5,
        })

    # Overall candidate ML task feasibility
    # Task 1: Each of top 15 single targets
    # Task 2: "Active against ANY target at pChEMBL >= 6 (strict)" vs "Tested but never active at pChEMBL >= 6"
    all_strict_mol_medians = df_strict_pchem.groupby(["inchikey_connectivity", "target_chembl_id"])["pchembl_value"].median().reset_index()
    all_tested_mols = set(all_strict_mol_medians["inchikey_connectivity"].unique())
    active_any_mols = set(all_strict_mol_medians[all_strict_mol_medians["pchembl_value"] >= 6.0]["inchikey_connectivity"].unique())
    never_active_mols = all_tested_mols - active_any_mols

    # Task 3: "Any usable activity record exists" (binary: has >=1 usable record vs matched with 0 usable records)
    has_usable_mols = set(df_compound_match[df_compound_match["n_activity_usable"] > 0]["inchikey_connectivity"])
    matched_no_usable_mols = set(df_compound_match[(df_compound_match["n_chembl_molregno"] > 0) & (df_compound_match["n_activity_usable"] == 0)]["inchikey_connectivity"])

    # Plant-level coverage
    links_file = Path("data/processed/compounds/plant_compound_links.csv")
    df_links = pd.read_csv(links_file) if links_file.exists() else None
    plant_metrics = {}
    if df_links is not None:
        usable_conns = set(df_compound_match[df_compound_match["n_activity_usable"] > 0]["inchikey_connectivity"])
        strict_conns = set(df_compound_match[df_compound_match["n_activity_strict"] > 0]["inchikey_connectivity"])

        df_links_usable = df_links[df_links["inchikey_connectivity"].isin(usable_conns)]
        df_links_strict = df_links[df_links["inchikey_connectivity"].isin(strict_conns)]

        plants_with_usable = df_links_usable["plant_index"].nunique()
        plants_with_strict = df_links_strict["plant_index"].nunique()

        usable_per_plant = df_links_usable.groupby("plant_index")["inchikey_connectivity"].nunique()
        strict_per_plant = df_links_strict.groupby("plant_index")["inchikey_connectivity"].nunique()

        plant_metrics = {
            "total_plants": df_links["plant_index"].nunique(),
            "plants_with_usable": plants_with_usable,
            "plants_with_strict": plants_with_strict,
            "usable_stats": {
                "min": int(usable_per_plant.min()) if len(usable_per_plant) else 0,
                "median": float(usable_per_plant.median()) if len(usable_per_plant) else 0,
                "max": int(usable_per_plant.max()) if len(usable_per_plant) else 0,
            },
            "strict_stats": {
                "min": int(strict_per_plant.min()) if len(strict_per_plant) else 0,
                "median": float(strict_per_plant.median()) if len(strict_per_plant) else 0,
                "max": int(strict_per_plant.max()) if len(strict_per_plant) else 0,
            }
        }

    # 14. Master integrity check at end
    end_hash = verify_master_manifest(logger)
    total_runtime = time.time() - start_time
    logger.info(f"Execution completed in {total_runtime:.2f} seconds")

    conn.close()

    # 15. Generate Markdown Report
    report_file = Path("data/quality/label_feasibility_report.md") if output_dir == Path("data/processed/compounds") else output_dir / "label_feasibility_report.md"
    generate_markdown_report(
        report_file=report_file,
        release_name=release_name,
        release_date=release_date,
        sqlite_path=sqlite_path,
        start_hash=start_hash,
        total_runtime=total_runtime,
        n_total_input=n_total_input,
        n_curated_input=n_curated_input,
        n_matched=n_matched,
        n_curated_matched=n_curated_matched,
        n_has_act_all=n_has_act_all,
        n_curated_has_act_all=n_curated_has_act_all,
        n_has_act_usable=n_has_act_usable,
        n_curated_has_act_usable=n_curated_has_act_usable,
        n_has_act_strict=n_has_act_strict,
        n_curated_has_act_strict=n_curated_has_act_strict,
        n_mol_dist=n_mol_dist,
        n_np_flag=n_np_flag,
        usable_stats=usable_stats,
        assay_type_counts=assay_type_counts,
        top30_targets=top30_targets,
        protein_class_counts=protein_class_counts,
        top15_details=top15_details,
        active_any_mols=len(active_any_mols),
        never_active_mols=len(never_active_mols),
        has_usable_mols=len(has_usable_mols),
        matched_no_usable_mols=len(matched_no_usable_mols),
        plant_metrics=plant_metrics
    )
    logger.info(f"Report generated at: {report_file}")

    return {
        "release_name": release_name,
        "release_date": release_date,
        "n_total_input": n_total_input,
        "n_curated_input": n_curated_input,
        "n_matched": n_matched,
        "n_has_act_usable": n_has_act_usable,
        "n_has_act_strict": n_has_act_strict,
        "total_runtime": total_runtime
    }


# ---------------------------------------------------------------------------
# Report Generator
# ---------------------------------------------------------------------------
def generate_markdown_report(
    report_file: Path,
    release_name: str,
    release_date: str,
    sqlite_path: str,
    start_hash: str,
    total_runtime: float,
    n_total_input: int,
    n_curated_input: int,
    n_matched: int,
    n_curated_matched: int,
    n_has_act_all: int,
    n_curated_has_act_all: int,
    n_has_act_usable: int,
    n_curated_has_act_usable: int,
    n_has_act_strict: int,
    n_curated_has_act_strict: int,
    n_mol_dist: Dict[str, int],
    n_np_flag: int,
    usable_stats: Dict,
    assay_type_counts: Dict,
    top30_targets: pd.DataFrame,
    protein_class_counts: Counter,
    top15_details: List[Dict],
    active_any_mols: int,
    never_active_mols: int,
    has_usable_mols: int,
    matched_no_usable_mols: int,
    plant_metrics: Dict
):
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# Stage 7A: ChEMBL Bioactivity Label Feasibility Assessment Report\n\n")
        f.write(f"- **ChEMBL Release**: `{release_name}` (Creation Date: `{release_date}`)\n")
        f.write(f"- **ChEMBL Database Path**: `{sqlite_path}` (Read-Only URI)\n")
        f.write(f"- **Execution Timestamp**: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n")
        f.write(f"- **Master MPBD SHA-256 (Start & End Verified)**: `{start_hash}`\n")
        f.write(f"- **Total Script Runtime**: {total_runtime:.2f} seconds ({total_runtime/60.0:.2f} minutes)\n\n")
        f.write("---\n\n")

        # 1. Input molecules
        f.write("## 1. Input Molecule Inventory\n\n")
        f.write("| Scope | Molecule Count | % of Total | Definition / Filter |\n")
        f.write("| :--- | :---: | :---: | :--- |\n")
        f.write(f"| **Full Inventory** | **{n_total_input:,}** | 100.0% | All unique 14-char connectivity layers from `compounds_unique.csv` |\n")
        pct_cur = (n_curated_input / n_total_input * 100.0) if n_total_input else 0.0
        f.write(f"| **Curated Drug-Like** | **{n_curated_input:,}** | {pct_cur:.1f}% | Excludes `is_inorganic`, `too_small`, `too_large`, and `is_mixture` |\n\n")
        f.write("---\n\n")

        # 2. Matching overview
        f.write("## 2. ChEMBL Structure Matching\n\n")
        pct_matched = (n_matched / n_total_input * 100.0) if n_total_input else 0.0
        pct_cur_matched = (n_curated_matched / n_curated_input * 100.0) if n_curated_input else 0.0
        f.write(f"- **Matched Molecules (Full Set)**: **{n_matched:,} / {n_total_input:,}** (**{pct_matched:.2f}%**)\n")
        f.write(f"- **Matched Molecules (Curated Set)**: **{n_curated_matched:,} / {n_curated_input:,}** (**{pct_cur_matched:.2f}%**)\n\n")
        f.write("### Distribution of Matched ChEMBL Molregnos per Molecule:\n\n")
        f.write("| Matched Molregno Count | Molecules | % of Matched |\n")
        f.write("| :--- | :---: | :---: |\n")
        for k in ["1", "2-5", ">5"]:
            cnt = n_mol_dist.get(k, 0)
            pct = (cnt / n_matched * 100.0) if n_matched else 0.0
            f.write(f"| **{k}** | {cnt:,} | {pct:.1f}% |\n")
        f.write("\n---\n\n")

        # 3. Natural product flag
        f.write("## 3. Natural Product Cross-Check (`molecule_dictionary.natural_product`)\n\n")
        pct_np = (n_np_flag / n_matched * 100.0) if n_matched else 0.0
        f.write(f"- Molecules flagged `natural_product = 1` in ChEMBL: **{n_np_flag:,}** ({pct_np:.1f}% of matched molecules).\n")
        f.write(f"- Note: ChEMBL's natural product flag is derived from COCONUT and literature curation; absence of a flag does not indicate synthetic origin.\n\n")
        f.write("---\n\n")

        # 4. Activity coverage
        f.write("## 4. Bioactivity Data Coverage\n\n")
        f.write("| Criteria Level | Full Set Molecules | Full % | Curated Molecules | Curated % | Record Definition |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :--- |\n")
        p_all = (n_has_act_all / n_total_input * 100.0) if n_total_input else 0.0
        p_c_all = (n_curated_has_act_all / n_curated_input * 100.0) if n_curated_input else 0.0
        f.write(f"| **ALL Activities** | **{n_has_act_all:,}** | {p_all:.1f}% | **{n_curated_has_act_all:,}** | {p_c_all:.1f}% | Any record in `activities` table |\n")
        p_use = (n_has_act_usable / n_total_input * 100.0) if n_total_input else 0.0
        p_c_use = (n_curated_has_act_usable / n_curated_input * 100.0) if n_curated_input else 0.0
        f.write(f"| **USABLE Records** | **{n_has_act_usable:,}** | {p_use:.1f}% | **{n_curated_has_act_usable:,}** | {p_c_use:.1f}% | `=`, `nM`, IC50/Ki/Kd/EC50, no dup/validity comments |\n")
        p_str = (n_has_act_strict / n_total_input * 100.0) if n_total_input else 0.0
        p_c_str = (n_curated_has_act_strict / n_curated_input * 100.0) if n_curated_input else 0.0
        f.write(f"| **STRICT Records** | **{n_has_act_strict:,}** | {p_str:.1f}% | **{n_curated_has_act_strict:,}** | {p_c_str:.1f}% | Usable AND `assay_type` in (B,F) AND confidence in (8,9) AND single target |\n\n")

        f.write("### Distribution of Usable Activity Records per Molecule (for molecules with >=1 usable record):\n\n")
        f.write(f"- Min: **{usable_stats.get('min', 0)}** | 25th %: **{usable_stats.get('q25', 0):.0f}** | Median: **{usable_stats.get('median', 0):.0f}** | 75th %: **{usable_stats.get('q75', 0):.0f}** | Max: **{usable_stats.get('max', 0):,}**\n\n")
        f.write("| Usable Records Bin | Number of Molecules | % of Labeled Molecules |\n")
        f.write("| :--- | :---: | :---: |\n")
        for b_name in ["1", "2-5", "6-20", ">20"]:
            cnt = usable_stats.get("bins", {}).get(b_name, 0)
            pct = (cnt / n_has_act_usable * 100.0) if n_has_act_usable else 0.0
            f.write(f"| **{b_name} records** | {cnt:,} | {pct:.1f}% |\n")
        f.write("\n---\n\n")

        # 5. Assay type breakdown
        f.write("## 5. Assay-Type Breakdown (All Raw Activity Records)\n\n")
        f.write("| Assay Type Code | Description | Record Count | % of Raw Records |\n")
        f.write("| :---: | :--- | :---: | :---: |\n")
        assay_desc = {
            "B": "Binding (interaction with target)",
            "F": "Functional (cellular/physiological response)",
            "A": "ADME (absorption, metabolism, etc.)",
            "T": "Toxicity (cytotoxicity, in vivo toxicity)",
            "P": "Physicochemical (solubility, permeability, etc.)",
            "U": "Unassigned"
        }
        total_rec = sum(assay_type_counts.values()) if assay_type_counts else 1
        for a_code, a_cnt in sorted(assay_type_counts.items(), key=lambda x: str(x[0])):
            desc = assay_desc.get(str(a_code), "Other / Unassigned")
            pct = (a_cnt / total_rec * 100.0)
            f.write(f"| **{a_code}** | {desc} | {a_cnt:,} | {pct:.1f}% |\n")
        f.write("\n---\n\n")

        # 6. Top 30 Targets
        f.write("## 6. Top 30 Biological Targets (STRICT Set)\n\n")
        f.write("Ranked by number of distinct Bangladeshi medicinal plant molecules tested:\n\n")
        f.write("| Rank | Target ChEMBL ID | Target Name | Target Type | Organism | Distinct Molecules Tested |\n")
        f.write("| :---: | :--- | :--- | :--- | :--- | :---: |\n")
        for idx, row in enumerate(top30_targets.itertuples(index=False), 1):
            f.write(f"| {idx} | `{row.target_chembl_id}` | {row.target_pref_name} | {row.target_type} | *{row.organism}* | **{row.n_molecules:,}** |\n")
        f.write("\n---\n\n")

        # 7. Protein Classification
        f.write("## 7. Target Classification Breakdown\n\n")
        f.write("**Query Used**:\n")
        f.write("```sql\n")
        f.write("SELECT DISTINCT st.tid, pc.class_level, pc.pref_name\n")
        f.write("FROM temp_strict_tids st\n")
        f.write("JOIN target_components tc ON st.tid = tc.tid\n")
        f.write("JOIN component_class cc ON tc.component_id = cc.component_id\n")
        f.write("JOIN protein_classification pc ON cc.protein_class_id = pc.protein_class_id\n")
        f.write("WHERE pc.class_level = 1\n")
        f.write("```\n\n")
        f.write("| Protein Superfamily / Class (Level 1) | Distinct Molecules Tested |\n")
        f.write("| :--- | :---: |\n")
        for p_cls, p_cnt in protein_class_counts.most_common():
            f.write(f"| **{p_cls}** | {p_cnt:,} |\n")
        f.write("\n---\n\n")

        # 8. Top 15 Targets (Thresholds & Conflicts)
        f.write("## 8. Target Bioactivity Distribution (Top 15 Targets, STRICT Set)\n\n")
        f.write("Aggregated by median pChEMBL per (molecule, target) pair:\n\n")
        f.write("| Target Name | Organism | Tested | Active (pChEMBL >= 6) | Inactive (< 6) | Conflicts (6) | Active (pChEMBL >= 5) | Inactive (< 5) | Conflicts (5) |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for d in top15_details:
            f.write(f"| **{d['target_pref_name']}** | *{d['organism']}* | {d['n_tested']:,} | **{d['n_active_6']:,}** | {d['n_inactive_6']:,} | {d['n_conflicts_6']} | **{d['n_active_5']:,}** | {d['n_inactive_5']:,} | {d['n_conflicts_5']} |\n")
        f.write("\n---\n\n")

        # 9. Feasibility Table
        f.write("## 9. Machine Learning Task Feasibility Summary\n\n")
        f.write("| Candidate Task | Total Labeled Molecules | Active Split | Inactive Split | Feasibility Threshold Flags |\n")
        f.write("| :--- | :---: | :---: | :---: | :--- |\n")
        
        # Candidate single targets
        for d in top15_details:
            flags = []
            if d['n_tested'] >= 1000:
                flags.append(">= 1,000")
            elif d['n_tested'] >= 500:
                flags.append(">= 500")
            elif d['n_tested'] >= 200:
                flags.append(">= 200")
            else:
                flags.append("< 200 (Low)")
            flag_str = ", ".join(flags)
            f.write(f"| Target: `{d['target_pref_name']}` | **{d['n_tested']:,}** | {d['n_active_6']:,} ({(d['n_active_6']/d['n_tested']*100 if d['n_tested'] else 0):.1f}%) | {d['n_inactive_6']:,} | `{flag_str}` |\n")

        # Global tasks
        tot_global = active_any_mols + never_active_mols
        g_flags = []
        if tot_global >= 1000: g_flags.append(">= 1,000")
        elif tot_global >= 500: g_flags.append(">= 500")
        elif tot_global >= 200: g_flags.append(">= 200")
        f.write(f"| **Active against ANY target (pChEMBL >= 6, strict)** | **{tot_global:,}** | {active_any_mols:,} ({(active_any_mols/tot_global*100 if tot_global else 0):.1f}%) | {never_active_mols:,} | `{', '.join(g_flags)}` |\n")

        tot_any_use = has_usable_mols + matched_no_usable_mols
        u_flags = []
        if tot_any_use >= 1000: u_flags.append(">= 1,000")
        elif tot_any_use >= 500: u_flags.append(">= 500")
        elif tot_any_use >= 200: u_flags.append(">= 200")
        f.write(f"| **Any usable activity record exists (ChEMBL-tested)** | **{tot_any_use:,}** | {has_usable_mols:,} ({(has_usable_mols/tot_any_use*100 if tot_any_use else 0):.1f}%) | {matched_no_usable_mols:,} | `{', '.join(u_flags)}` |\n\n")
        f.write("---\n\n")

        # 10. Plant-level effects
        f.write("## 10. Plant-Level Representation\n\n")
        if plant_metrics:
            f.write(f"- Total Medicinal Plants Evaluated: **{plant_metrics.get('total_plants', 222)}**\n")
            f.write(f"- Plants with >= 1 molecule having **USABLE** activity: **{plant_metrics.get('plants_with_usable', 0)}** ({plant_metrics.get('plants_with_usable', 0)/plant_metrics.get('total_plants', 222)*100:.1f}%)\n")
            f.write(f"- Plants with >= 1 molecule having **STRICT** activity: **{plant_metrics.get('plants_with_strict', 0)}** ({plant_metrics.get('plants_with_strict', 0)/plant_metrics.get('total_plants', 222)*100:.1f}%)\n\n")
            f.write("### Labeled Molecules per Plant Distribution:\n\n")
            f.write(f"- **Usable Activity**: Min: **{plant_metrics['usable_stats']['min']}** | Median: **{plant_metrics['usable_stats']['median']:.0f}** | Max: **{plant_metrics['usable_stats']['max']}**\n")
            f.write(f"- **Strict Activity**: Min: **{plant_metrics['strict_stats']['min']}** | Median: **{plant_metrics['strict_stats']['median']:.0f}** | Max: **{plant_metrics['strict_stats']['max']}**\n\n")
        f.write("---\n\n")

        # 11. Empirical Risks
        f.write("## 11. Empirical Risks & Scientific Observations\n\n")
        f.write("1. **Label Sparsity**: While a notable fraction of molecules have bioactivity records in ChEMBL, data across specific individual protein targets drops significantly. Only a few top targets achieve >= 200 tested molecules.\n")
        f.write("2. **Severe Class Imbalance**: For single targets at pChEMBL >= 6, active vs inactive ratios exhibit strong skew depending on whether secondary pharmacology or primary screening was performed.\n")
        f.write("3. **Assay Heterogeneity**: Functional assays (cell-based, phenotypic) constitute a substantial volume alongside pure binding assays; strict single-protein target modeling requires filtering to assay types `B` and `F` with high confidence scores.\n\n")


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="ChEMBL Label Coverage Assessment")
    parser.add_argument("--sqlite-path", type=str, default=r"F:\datasets\chembl_37\chembl_37_sqlite\chembl_37.db")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of molecules to evaluate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for sampling")
    parser.add_argument("--output-dir", type=Path, default=None, help="Custom output directory")
    args = parser.parse_args()

    run_chembl_label_coverage(
        sqlite_path=args.sqlite_path,
        limit=args.limit,
        seed=args.seed,
        output_dir=args.output_dir
    )

if __name__ == "__main__":
    main()
