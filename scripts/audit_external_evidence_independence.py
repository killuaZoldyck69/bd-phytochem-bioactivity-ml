#!/usr/bin/env python3
"""
scripts/audit_external_evidence_independence.py
================================================
Comprehensive audit of ChEMBL training pool vs. external Bangladeshi flora evaluation sets.

Calculates:
1. MPBD compounds initially retrieved
2. Fingerprintable compounds (reconciling to 7,315)
3. Full InChIKey stereochemical overlap against ChEMBL target training pool
4. Connectivity-layer only overlap (14-char InChIKey)
5. Remaining truly held-out compounds
6. Qualifying external bioactivity labels (all and high-tier link scope)
7. Evidence independence: tracing underlying ChEMBL activity records to publication doc_ids
   shared with the target training pool.

Outputs:
- data/quality/external_independence_flow_table.csv
- data/quality/external_compound_evidence_audit.csv
"""

from collections import defaultdict
import os
from pathlib import Path
import sqlite3
import sys

import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator

# Constants & Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
CHEMBL_DB = Path("F:/datasets/chembl_37/chembl_37_sqlite/chembl_37.db")
FLORA_UNIQUE_PATH = REPO_ROOT / "data/processed/compounds/compounds_unique.csv"
CONFIDENCE_LINKS_PATH = REPO_ROOT / "data/processed/compounds/plant_compound_links_confidence.csv"
MODELING_DIR = REPO_ROOT / "data/processed/modeling"
QUALITY_DIR = REPO_ROOT / "data/quality"

TARGETS = {
    "COX-1": {"slug": "cox1", "tid": 96, "chembl_id": "CHEMBL221"},
    "COX-2": {"slug": "cox2", "tid": 126, "chembl_id": "CHEMBL230"},
    "XO": {"slug": "xo", "tid": 149, "chembl_id": "CHEMBL1929"},
    "MAO-A": {"slug": "maoa", "tid": 86, "chembl_id": "CHEMBL1951"},
}

THRESHOLDS = [6, 5]


def main():
    print("=" * 80)
    print("AUDITING CHÈMBL TRAINING POOLS & EXTERNAL FLORA EVALUATION SETS")
    print("=" * 80)

    if not CHEMBL_DB.exists():
        raise FileNotFoundError(f"ChEMBL SQLite database missing at {CHEMBL_DB}")

    QUALITY_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load flora unique molecules and featurize to reconcile 7,315 fingerprintable compounds
    print(f"Loading flora unique compounds from {FLORA_UNIQUE_PATH}...")
    df_flora = pd.read_csv(FLORA_UNIQUE_PATH)
    n_initial_unique = len(df_flora)
    print(f"MPBD Unique Compounds (Stage 1): {n_initial_unique:,}")

    fp_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    fingerprintable_indices = []
    for idx, r in df_flora.iterrows():
        smi = r["smiles_standardized"] if pd.notna(r["smiles_standardized"]) and str(r["smiles_standardized"]).strip() else r["smiles_flat"]
        if pd.isna(smi) or not str(smi).strip():
            continue
        mol = Chem.MolFromSmiles(str(smi))
        if mol:
            fingerprintable_indices.append(idx)

    df_fp = df_flora.loc[fingerprintable_indices].copy()
    n_fingerprintable = len(df_fp)
    print(f"Fingerprintable Compounds (Stage 2): {n_fingerprintable:,}")
    assert n_fingerprintable == 7315, f"Expected 7,315 fingerprintable compounds, got {n_fingerprintable}"

    flora_conn_set = set(df_fp["inchikey_connectivity"].dropna())

    # High-tier flora layers
    df_conf = pd.read_csv(CONFIDENCE_LINKS_PATH)
    high_tier_conn = set(df_conf[df_conf["link_tier"] == "HIGH"]["inchikey_connectivity"].dropna())
    print(f"Flora layers with >= 1 HIGH-tier plant link: {len(high_tier_conn):,}")

    # Connect to ChEMBL
    db_uri = f"file:{CHEMBL_DB.as_posix()}?mode=ro"
    conn = sqlite3.connect(db_uri, uri=True)
    cur = conn.cursor()

    flow_table_rows = []
    compound_audit_rows = []

    for tgt_name, tgt_cfg in TARGETS.items():
        slug = tgt_cfg["slug"]
        tid = tgt_cfg["tid"]
        chembl_id = tgt_cfg["chembl_id"]
        print(f"\nProcessing Target: {tgt_name} ({chembl_id}, tid={tid})...")

        # Load master labels file generated in Stage 7A / Step 04
        labels_path = MODELING_DIR / f"cox_datacheck_labels_{slug}.csv"
        df_labels = pd.read_csv(labels_path)

        # Fetch qualifying activity records directly from ChEMBL 37
        cur.execute("""
            SELECT 
                a.activity_id,
                a.molregno,
                cs.standard_inchi_key,
                substr(cs.standard_inchi_key, 1, 14) AS conn,
                a.pchembl_value,
                a.doc_id,
                d.chembl_id AS doc_chembl_id,
                d.title AS doc_title,
                d.year AS doc_year,
                d.doi AS doc_doi
            FROM assays ass
            JOIN activities a ON ass.assay_id = a.assay_id
            JOIN compound_structures cs ON a.molregno = cs.molregno
            LEFT JOIN docs d ON a.doc_id = d.doc_id
            WHERE ass.tid = ?
              AND ass.assay_type IN ('B', 'F')
              AND ass.confidence_score IN (8, 9)
              AND a.standard_relation = '='
              AND a.standard_units = 'nM'
              AND a.standard_type IN ('IC50', 'Ki', 'Kd', 'EC50')
              AND a.potential_duplicate = 0
              AND a.data_validity_comment IS NULL
              AND a.pchembl_value IS NOT NULL
        """, (tid,))
        act_rows = cur.fetchall()
        df_act = pd.DataFrame(act_rows, columns=[
            "activity_id", "molregno", "full_key", "conn", "pchembl_value",
            "doc_id", "doc_chembl_id", "doc_title", "doc_year", "doc_doi"
        ])
        print(f"  Fetched {len(df_act):,} qualifying activity rows from ChEMBL.")

        for T in THRESHOLDS:
            conf_col = f"conflict_T{T}"
            lbl_col = f"label_T{T}"

            # Pipeline training pool: connectivity layers not in flora and not conflicted
            pool_df = df_labels[(df_labels["split"] == "training_pool") & (df_labels[conf_col] == False)].copy()
            pool_conn = set(pool_df["inchikey_connectivity"])

            # ChEMBL activity records for training pool
            train_acts = df_act[df_act["conn"].isin(pool_conn)]
            train_docs = set(train_acts["doc_id"].dropna())
            train_full_keys = set(train_acts["full_key"].dropna())

            # Flora molecules evaluated
            # All qualifying in ChEMBL for this target (non-conflict)
            flora_labeled_df = df_labels[(df_labels["split"] == "flora") & (df_labels[conf_col] == False)].copy()
            flora_labeled_conn = set(flora_labeled_df["inchikey_connectivity"])

            # High-tier qualifying in ChEMBL (Stage 7B evaluation scope)
            flora_high_df = flora_labeled_df[flora_labeled_df["inchikey_connectivity"].isin(high_tier_conn)].copy()
            flora_high_conn = set(flora_high_df["inchikey_connectivity"])

            # Overlap analysis of all 7,315 flora molecules against training pool:
            # Stage 3: Full InChIKey overlap
            full_overlap_conn = set(df_fp[df_fp["inchikey"].isin(train_full_keys)]["inchikey_connectivity"])
            # Stage 4: Connectivity layer overlap
            conn_overlap_conn = set(df_fp[df_fp["inchikey_connectivity"].isin(pool_conn)]["inchikey_connectivity"])
            # Connectivity only
            conn_only_overlap_conn = conn_overlap_conn - full_overlap_conn
            # Stage 5: Truly held out
            truly_held_out_conn = flora_conn_set - conn_overlap_conn

            # Total qualifying in ChEMBL among flora:
            # Check overlap of raw ChEMBL activities with flora
            raw_target_full_keys = set(df_act["full_key"].dropna())
            raw_target_conn_keys = set(df_act["conn"].dropna())

            raw_full_overlap = set(df_fp[df_fp["inchikey"].isin(raw_target_full_keys)]["inchikey_connectivity"])
            raw_conn_overlap = set(df_fp[df_fp["inchikey_connectivity"].isin(raw_target_conn_keys)]["inchikey_connectivity"])
            raw_conn_only = raw_conn_overlap - raw_full_overlap

            # Evidence independence calculation for labeled flora
            flora_acts = df_act[df_act["conn"].isin(flora_labeled_conn)]

            indep_all_conn = set()
            shared_all_conn = set()
            for c in flora_labeled_conn:
                c_docs = set(flora_acts[flora_acts["conn"] == c]["doc_id"].dropna())
                if c_docs.intersection(train_docs):
                    shared_all_conn.add(c)
                else:
                    indep_all_conn.add(c)

            indep_high_conn = set()
            shared_high_conn = set()
            for c in flora_high_conn:
                c_docs = set(flora_acts[flora_acts["conn"] == c]["doc_id"].dropna())
                if c_docs.intersection(train_docs):
                    shared_high_conn.add(c)
                else:
                    indep_high_conn.add(c)

            # Record flow table row
            flow_table_rows.append({
                "Target": tgt_name,
                "ChEMBL_TID": tid,
                "ChEMBL_Target_ID": chembl_id,
                "Threshold": f"T={T}",
                "1_MPBD_Initial_Unique": n_initial_unique,
                "2_Fingerprintable_Scope": n_fingerprintable,
                "ChEMBL_Target_Pool_FullKeys": len(raw_target_full_keys),
                "ChEMBL_Target_Pool_ConnLayers": len(raw_target_conn_keys),
                "Raw_Full_InChIKey_Overlap": len(raw_full_overlap),
                "Raw_Conn_Only_Overlap": len(raw_conn_only),
                "Raw_Total_Conn_Overlap": len(raw_conn_overlap),
                "3_Overlap_Training_Full_InChIKey": len(full_overlap_conn),
                "4_Overlap_Training_Conn_Only": len(conn_only_overlap_conn),
                "5_Remaining_Truly_Held_Out": len(truly_held_out_conn),
                "Training_Pool_ConnLayers": len(pool_conn),
                "Training_Pool_Unique_Docs": len(train_docs),
                "6_HeldOut_With_Qualifying_Label_All": len(flora_labeled_conn),
                "6_HeldOut_With_Qualifying_Label_HighTier": len(flora_high_conn),
                "7_Evidence_Independent_Labels_All": len(indep_all_conn),
                "7_Evidence_Shared_Pub_Labels_All": len(shared_all_conn),
                "7_Evidence_Independent_Labels_HighTier": len(indep_high_conn),
                "7_Evidence_Shared_Pub_Labels_HighTier": len(shared_high_conn),
                "Survival_Rate_HighTier_Pct": round(len(indep_high_conn) / len(flora_high_conn) * 100.0, 2) if flora_high_conn else 0.0,
            })

            # Record compound-level audit rows
            for _, r in flora_labeled_df.iterrows():
                c = r["inchikey_connectivity"]
                c_acts = flora_acts[flora_acts["conn"] == c]
                c_docs = set(c_acts["doc_id"].dropna())
                shared_doc_ids = c_docs.intersection(train_docs)
                is_indep = (len(shared_doc_ids) == 0)

                shared_chembl_docs = [str(x) for x in c_acts[c_acts["doc_id"].isin(shared_doc_ids)]["doc_chembl_id"].unique()]
                all_chembl_docs = [str(x) for x in c_acts["doc_chembl_id"].unique()]

                f_meta = df_fp[df_fp["inchikey_connectivity"] == c].iloc[0]
                compound_name = str(f_meta["compound_names"]).split("|")[0] if pd.notna(f_meta["compound_names"]) else "Unknown"
                full_inchikey = f_meta["inchikey"] if pd.notna(f_meta["inchikey"]) else ""

                compound_audit_rows.append({
                    "target": tgt_name,
                    "target_chembl_id": chembl_id,
                    "threshold": f"T={T}",
                    "inchikey_connectivity": c,
                    "full_inchikey": full_inchikey,
                    "compound_name": compound_name,
                    "is_high_tier_link": (c in high_tier_conn),
                    "n_chembl_activity_records": len(c_acts),
                    "median_pchembl": r["median_pchembl"],
                    "min_pchembl": r["min_pchembl"],
                    "max_pchembl": r["max_pchembl"],
                    "label": int(r[lbl_col]),
                    "evidence_independent": is_indep,
                    "n_total_publications": len(c_docs),
                    "n_shared_publications_with_training": len(shared_doc_ids),
                    "all_publication_chembl_ids": "|".join(all_chembl_docs),
                    "shared_publication_chembl_ids": "|".join(shared_chembl_docs) if shared_chembl_docs else "NONE",
                })

    # Save CSVs
    flow_df = pd.DataFrame(flow_table_rows)
    flow_csv_path = QUALITY_DIR / "external_independence_flow_table.csv"
    flow_df.to_csv(flow_csv_path, index=False)
    print(f"\nSaved flow table to: {flow_csv_path}")

    audit_df = pd.DataFrame(compound_audit_rows)
    audit_csv_path = QUALITY_DIR / "external_compound_evidence_audit.csv"
    audit_df.to_csv(audit_csv_path, index=False)
    print(f"Saved compound-level evidence audit to: {audit_csv_path}")

    print("\n" + "=" * 80)
    print("FLOW TABLE SUMMARY")
    print("=" * 80)
    cols_display = [
        "Target", "Threshold", "1_MPBD_Initial_Unique", "2_Fingerprintable_Scope",
        "Raw_Full_InChIKey_Overlap", "Raw_Conn_Only_Overlap", "5_Remaining_Truly_Held_Out",
        "6_HeldOut_With_Qualifying_Label_HighTier", "7_Evidence_Independent_Labels_HighTier",
        "Survival_Rate_HighTier_Pct"
    ]
    print(flow_df[cols_display].to_string(index=False))


if __name__ == "__main__":
    main()
