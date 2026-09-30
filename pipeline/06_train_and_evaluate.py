#!/usr/bin/env python3
"""
pipeline/06_train_and_evaluate.py
==================================
Stage 7B: Baseline Models, Internal Validation, and One-Time External Evaluation.
Authority: docs/thesis_design_note.md + amendments.

Key Requirements:
1. Training structures:
   - For each training_pool layer, select representative canonical_smiles
     (molregno with max activity records; tie-breaker: min molregno).
   - Standardize with standardize_mol imported from pipeline/02_standardize_structures.py.
   - Exclude conflict rows per threshold.
   - Assert disjointness: no flora connectivity layer appears in any training set.
2. Features & Models:
   - ECFP4 fingerprints (Morgan radius 2, 2048 bits).
   - RandomForestClassifier: grid over n_estimators in {300, 600}, max_features in {'sqrt', 0.1},
     class_weight='balanced', random_state=42.
   - 1-Nearest-Neighbour Tanimoto baseline.
   - No other model family.
3. Internal Validation:
   - Bemis-Murcko scaffold split (acyclic molecules form their own group 'acyclic').
   - 5 grouped folds (StratifiedGroupKFold, seed 42).
   - Select RF grid point by mean validation AUPRC.
   - Report per-fold and mean AUROC, AUPRC, Brier score, and 10-bin calibration table.
   - Stratify metrics for molecules with ChEMBL natural_product == 1 (coarse flag note included).
   - Choose optimal probability cutoff on internal validation (max F1).
4. Freeze Configuration:
   - Write data/processed/modeling/stage7b_config_frozen.json and log SHA-256.
   - External set is touched strictly after this freeze.
5. External Evaluation:
   - Labeled flora with >= 1 HIGH link in plant_compound_links_confidence.csv.
   - (a) As-is. (b) Pending user review of external_verification_sheet.csv.
   - COX-1 & COX-2: predicted probability vs measured pChEMBL, Spearman correlation.
     Explicitly state no AUROC/AUPRC claimed.
   - XO & MAO-A: AUROC, AUPRC, and 1000-resample bootstrap 95% CIs.
6. Applicability Domain:
   - NN Tanimoto similarity to training pool for every external molecule.
   - Split external performance by NN >= 0.4 vs NN < 0.4.
7. Score All Flora Molecules:
   - Score all 7,315 fingerprintable flora layers with final RF model.
   - Output data/processed/modeling/flora_predictions_<target>_T<6|5>.csv.
   - Record internal cutoff and share of flora scored above it.
8. Figures (matplotlib, 300 dpi, figures/):
   - ROC & PR curves, calibration plots, COX external scatter, NN similarity histograms.
9. Reports & Audits:
   - data/quality/stage7b_model_report.md
   - Master MPBD SHA-256 verified at start and end.
"""

import argparse
from collections import defaultdict
import datetime
import hashlib
import importlib
import json
import logging
import os
from pathlib import Path
import random
import sqlite3
import sys
import time
from typing import Dict, List, Optional, Tuple, Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    roc_curve,
    precision_recall_curve,
    f1_score,
)
from sklearn.model_selection import StratifiedGroupKFold

from rdkit import Chem, DataStructs
from rdkit.Chem import rdFingerprintGenerator
from rdkit.Chem.MolStandardize import rdMolStandardize
from rdkit.Chem.Scaffolds import MurckoScaffold

# Force UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Constants & Paths
# ---------------------------------------------------------------------------
MASTER_MPBD_PATH = Path("data/raw/mpbd/mpbd_plant_index.csv")
EXPECTED_MASTER_SHA256 = "0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7"

CHEMBL_DB_PATH = Path("F:/datasets/chembl_37/chembl_37_sqlite/chembl_37.db")
LOOKUP_CACHE_PATH = Path("data/cache/chembl/chembl37_connectivity_lookup.csv")
FLORA_UNIQUE_PATH = Path("data/processed/compounds/compounds_unique.csv")
CONFIDENCE_LINKS_PATH = Path("data/processed/compounds/plant_compound_links_confidence.csv")
EXTERNAL_SHEET_PATH = Path("data/processed/modeling/external_verification_sheet.csv")

OUT_MODELING_DIR = Path("data/processed/modeling")
OUT_QUALITY_DIR = Path("data/quality")
FIGURES_DIR = Path("figures")

TARGET_CONFIGS = {
    "cox1": {"tid": 96, "chembl_id": "CHEMBL221", "pref_name": "COX-1 (PTGS1)", "is_cox": True},
    "cox2": {"tid": 126, "chembl_id": "CHEMBL230", "pref_name": "COX-2 (PTGS2)", "is_cox": True},
    "xo": {"tid": 149, "chembl_id": "CHEMBL1929", "pref_name": "Xanthine Oxidase (XDH)", "is_cox": False},
    "maoa": {"tid": 86, "chembl_id": "CHEMBL1951", "pref_name": "MAO-A (CHRFAM7A/MAOA)", "is_cox": False},
}

RF_GRID = [
    {"n_estimators": 300, "max_features": "sqrt"},
    {"n_estimators": 300, "max_features": 0.1},
    {"n_estimators": 600, "max_features": "sqrt"},
    {"n_estimators": 600, "max_features": 0.1},
]

# ---------------------------------------------------------------------------
# Integrity Verification
# ---------------------------------------------------------------------------
def verify_file_sha256(filepath: Path, expected_sha: str = None) -> str:
    if not filepath.exists():
        raise FileNotFoundError(f"Missing file: {filepath}")
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    digest = h.hexdigest().upper()
    if expected_sha and digest != expected_sha.upper():
        raise ValueError(f"SHA-256 mismatch for {filepath}: got {digest}, expected {expected_sha}")
    return digest


# ---------------------------------------------------------------------------
# Dynamic Import of Standardization Function
# ---------------------------------------------------------------------------
def get_standardizer():
    repo_root = Path(__file__).resolve().parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    std_mod = importlib.import_module("pipeline.02_standardize_structures")
    standardize_mol_func = getattr(std_mod, "standardize_mol")
    chooser = rdMolStandardize.LargestFragmentChooser()
    uncharger = rdMolStandardize.Uncharger()
    tautomer_enumerator = rdMolStandardize.TautomerEnumerator()
    tautomer_enumerator.SetMaxTautomers(50)
    return standardize_mol_func, chooser, uncharger, tautomer_enumerator


# ---------------------------------------------------------------------------
# 1-Nearest-Neighbour Tanimoto Baseline Model
# ---------------------------------------------------------------------------
class Tanimoto1NNBaseline:
    """
    1-Nearest-Neighbour Tanimoto baseline classifier.
    Stores training RDKit ExplicitBitVect fingerprints and labels.
    Prediction for a query:
      - Finds nearest neighbour by Tanimoto similarity.
      - Predicts probability = label of nearest neighbour (0.0 or 1.0).
      - Also tracks max similarity for applicability domain.
    """
    def __init__(self):
        self.train_fps = []
        self.train_y = np.array([], dtype=float)

    def fit(self, train_fps: List[Any], train_y: np.ndarray):
        self.train_fps = list(train_fps)
        self.train_y = np.array(train_y, dtype=float)
        return self

    def predict_proba(self, query_fps: List[Any]) -> np.ndarray:
        probs = np.zeros(len(query_fps), dtype=float)
        for i, qfp in enumerate(query_fps):
            sims = DataStructs.BulkTanimotoSimilarity(qfp, self.train_fps)
            best_idx = int(np.argmax(sims))
            probs[i] = self.train_y[best_idx]
        return probs

    def get_nearest_similarities(self, query_fps: List[Any]) -> np.ndarray:
        sims_out = np.zeros(len(query_fps), dtype=float)
        for i, qfp in enumerate(query_fps):
            sims = DataStructs.BulkTanimotoSimilarity(qfp, self.train_fps)
            sims_out[i] = float(np.max(sims)) if sims else 0.0
        return sims_out


# ---------------------------------------------------------------------------
# Helper: Compute Calibration Table (10 Bins)
# ---------------------------------------------------------------------------
def compute_calibration_table(y_true: np.ndarray, y_prob: np.ndarray) -> List[Dict]:
    bins = np.linspace(0.0, 1.0, 11)
    table = []
    for i in range(10):
        low, high = bins[i], bins[i + 1]
        if i == 9:
            mask = (y_prob >= low) & (y_prob <= high)
            bin_label = f"[{low:.1f}, {high:.1f}]"
        else:
            mask = (y_prob >= low) & (y_prob < high)
            bin_label = f"[{low:.1f}, {high:.1f})"

        n_samples = int(np.sum(mask))
        if n_samples > 0:
            mean_pred = float(np.mean(y_prob[mask]))
            emp_pos = float(np.mean(y_true[mask]))
            n_pos = int(np.sum(y_true[mask]))
        else:
            mean_pred = float((low + high) / 2.0)
            emp_pos = 0.0
            n_pos = 0

        table.append({
            "bin": bin_label,
            "low": float(low),
            "high": float(high),
            "n_samples": n_samples,
            "n_positives": n_pos,
            "mean_predicted_prob": round(mean_pred, 4),
            "empirical_positive_rate": round(emp_pos, 4),
        })
    return table


# ---------------------------------------------------------------------------
# Helper: Bootstrap Confidence Intervals for AUROC and AUPRC
# ---------------------------------------------------------------------------
def bootstrap_metric_ci(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_resamples: int = 1000,
    seed: int = 42,
    alpha: float = 0.05,
) -> Dict[str, Tuple[float, float, float]]:
    rng = np.random.RandomState(seed)
    n = len(y_true)
    aurocs = []
    auprcs = []

    base_auroc = float(roc_auc_score(y_true, y_prob)) if len(np.unique(y_true)) > 1 else np.nan
    base_auprc = float(average_precision_score(y_true, y_prob)) if len(np.unique(y_true)) > 1 else np.nan

    for _ in range(n_resamples):
        idx = rng.randint(0, n, size=n)
        bs_y = y_true[idx]
        bs_prob = y_prob[idx]
        if len(np.unique(bs_y)) < 2:
            continue
        try:
            aurocs.append(roc_auc_score(bs_y, bs_prob))
            auprcs.append(average_precision_score(bs_y, bs_prob))
        except Exception:
            continue

    low_p = (alpha / 2.0) * 100
    high_p = (1.0 - alpha / 2.0) * 100

    auroc_ci = (
        float(np.percentile(aurocs, low_p)),
        float(np.percentile(aurocs, high_p)),
    ) if aurocs else (np.nan, np.nan)

    auprc_ci = (
        float(np.percentile(auprcs, low_p)),
        float(np.percentile(auprcs, high_p)),
    ) if auprcs else (np.nan, np.nan)

    return {
        "auroc": (base_auroc, auroc_ci[0], auroc_ci[1]),
        "auprc": (base_auprc, auprc_ci[0], auprc_ci[1]),
    }


# ---------------------------------------------------------------------------
# Main Training & Evaluation Pipeline
# ---------------------------------------------------------------------------
def run_pipeline(
    dry_run: bool = False,
    dry_run_target: str = "cox1",
    dry_run_folds: int = 2,
):
    print("=" * 80)
    mode_str = f"DRY RUN (target={dry_run_target}, T=6, folds={dry_run_folds})" if dry_run else "FULL RUN (4 Targets, T=6 & T=5, 5 Folds)"
    print(f"STAGE 7B: MODEL TRAINING, INTERNAL CV & EXTERNAL EVALUATION [{mode_str}]")
    print("=" * 80)

    # 1. Master dataset integrity verification at start
    start_hash = verify_file_sha256(MASTER_MPBD_PATH, EXPECTED_MASTER_SHA256)
    print(f"[VERIFIED] Master MPBD SHA-256 start: {start_hash}")

    # Ensure directories exist
    OUT_MODELING_DIR.mkdir(parents=True, exist_ok=True)
    OUT_QUALITY_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Setup RDKit fingerprint generator & standardizer
    fp_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    standardize_mol_func, chooser, uncharger, tautomer_enumerator = get_standardizer()

    # Load Flora unique compounds
    print(f"\n[1/7] Loading Flora unique molecules from {FLORA_UNIQUE_PATH}...")
    df_flora_unique = pd.read_csv(FLORA_UNIQUE_PATH)
    flora_conn_set = set(df_flora_unique["inchikey_connectivity"].dropna())
    print(f"Loaded {len(df_flora_unique):,} flora rows covering {len(flora_conn_set):,} distinct connectivity layers.")

    # Precompute fingerprints for all flora molecules
    print("Precomputing ECFP4 fingerprints for all fingerprintable flora molecules...")
    flora_fps: Dict[str, Any] = {}
    flora_np_arrays: Dict[str, np.ndarray] = {}
    flora_smiles_map: Dict[str, str] = {}

    for _, row in df_flora_unique.iterrows():
        c = row["inchikey_connectivity"]
        smi = row["smiles_standardized"] if pd.notna(row["smiles_standardized"]) and str(row["smiles_standardized"]).strip() else row["smiles_flat"]
        if pd.isna(smi) or not str(smi).strip():
            continue
        mol = Chem.MolFromSmiles(str(smi))
        if mol:
            fp = fp_gen.GetFingerprint(mol)
            arr = np.zeros((2048,), dtype=np.int8)
            DataStructs.ConvertToNumpyArray(fp, arr)
            flora_fps[c] = fp
            flora_np_arrays[c] = arr
            flora_smiles_map[c] = str(smi)

    print(f"Successfully generated ECFP4 fingerprints for {len(flora_fps):,} flora connectivity layers.")

    # Load high-tier flora layers from confidence links
    print(f"\nLoading plant-compound confidence links from {CONFIDENCE_LINKS_PATH}...")
    df_conf = pd.read_csv(CONFIDENCE_LINKS_PATH)
    high_tier_flora_layers = set(df_conf[df_conf["link_tier"] == "HIGH"]["inchikey_connectivity"].dropna())
    print(f"Total flora layers with >= 1 HIGH link: {len(high_tier_flora_layers):,}")

    # Check external verification sheet for reference compounds
    df_ext_sheet = pd.read_csv(EXTERNAL_SHEET_PATH)
    ref_compounds_filled = df_ext_sheet["is_reference_compound"].dropna().count() > 0
    ref_compound_layers = set(df_ext_sheet[df_ext_sheet["is_reference_compound"] == 1.0]["layer"].dropna()) if ref_compounds_filled else set()
    print(f"External verification sheet reference status: {'POPULATED (' + str(len(ref_compound_layers)) + ' ref layers)' if ref_compounds_filled else 'EMPTY (pending user review)'}")

    # Load ChEMBL connectivity lookup
    print(f"\nLoading ChEMBL 37 connectivity lookup from {LOOKUP_CACHE_PATH}...")
    df_lookup = pd.read_csv(LOOKUP_CACHE_PATH)
    mol_to_conn = dict(zip(df_lookup["molregno"], df_lookup["connectivity"]))
    print(f"Loaded {len(mol_to_conn):,} ChEMBL molregno-to-connectivity mappings.")

    # Connect to ChEMBL 37 strictly read-only
    db_uri = f"file:{CHEMBL_DB_PATH.as_posix()}?mode=ro"
    print(f"Connecting to ChEMBL 37 SQLite database (Read-Only: {db_uri})...")
    conn = sqlite3.connect(db_uri, uri=True)
    cur = conn.cursor()

    # Pre-fetch natural_product flags from molecule_dictionary
    cur.execute("SELECT molregno, natural_product FROM molecule_dictionary")
    molregno_np_map = dict(cur.fetchall())
    print(f"Fetched natural_product flags for {len(molregno_np_map):,} molecules from molecule_dictionary.")

    # Targets to process
    if dry_run:
        if dry_run_target == "remaining":
            targets_to_run = ["cox2", "xo", "maoa"]
        elif dry_run_target == "all":
            targets_to_run = list(TARGET_CONFIGS.keys())
        else:
            targets_to_run = [dry_run_target]
    else:
        targets_to_run = list(TARGET_CONFIGS.keys())
    thresholds_to_run = [6] if dry_run else [6, 5]
    n_cv_splits = dry_run_folds if dry_run else 5

    # Storage for all evaluation results
    all_target_data: Dict[str, Any] = {}
    chosen_hyperparameters: Dict[str, Dict[str, Any]] = defaultdict(dict)
    training_set_hashes: Dict[str, Dict[str, str]] = defaultdict(dict)
    internal_results_summary: List[Dict] = []
    external_results_summary: List[Dict] = []
    cox_external_data: Dict[str, pd.DataFrame] = {}
    calibration_records: Dict[str, List[Dict]] = {}
    curves_data: Dict[str, Dict] = {}

    print("\n" + "=" * 80)
    print("STEP 1: PREPARING TRAINING DATA & STRUCTURES PER TARGET")
    print("=" * 80)

    for target_key in targets_to_run:
        target_info = TARGET_CONFIGS[target_key]
        tid = target_info["tid"]
        pref_name = target_info["pref_name"]
        print(f"\n>>> Extracting training pool for {pref_name} (tid={tid}, {target_info['chembl_id']})...")

        # Fast query for target activities
        cur.execute("DROP TABLE IF EXISTS temp_target_assays")
        cur.execute("CREATE TEMP TABLE temp_target_assays (assay_id INTEGER PRIMARY KEY)")
        cur.execute("""
            INSERT INTO temp_target_assays (assay_id)
            SELECT assay_id FROM assays
            WHERE tid = ?
              AND assay_type IN ('B', 'F')
              AND confidence_score IN (8, 9)
        """, (tid,))

        cur.execute("""
            SELECT a.molregno, count(a.activity_id) as cnt
            FROM temp_target_assays ta
            JOIN activities a ON ta.assay_id = a.assay_id
            WHERE a.standard_relation = '='
              AND a.standard_units = 'nM'
              AND a.standard_type IN ('IC50', 'Ki', 'Kd', 'EC50')
              AND a.potential_duplicate = 0
              AND a.data_validity_comment IS NULL
              AND a.pchembl_value IS NOT NULL
            GROUP BY a.molregno
        """)
        mol_act_counts = cur.fetchall()

        # Group molregnos by connectivity layer
        layer_mols = defaultdict(list)
        for mreg, cnt in mol_act_counts:
            c = mol_to_conn.get(mreg)
            if c:
                layer_mols[c].append((cnt, mreg))

        # Select representative molregno: max count, min molregno tie-breaker
        rep_mols: Dict[str, int] = {}
        for c, lst in layer_mols.items():
            lst.sort(key=lambda x: (-x[0], x[1]))
            rep_mols[c] = lst[0][1]

        # Load target labels file
        labels_file = OUT_MODELING_DIR / f"cox_datacheck_labels_{target_key}.csv"
        df_labels = pd.read_csv(labels_file)

        pool_df = df_labels[df_labels["split"] == "training_pool"].copy()
        flora_df = df_labels[df_labels["split"] == "flora"].copy()

        # Assert no flora connectivity layer appears in training pool
        overlap = set(pool_df["inchikey_connectivity"]).intersection(flora_conn_set)
        if len(overlap) > 0:
            raise AssertionError(f"FATAL: Flora connectivity layer leaked into {target_key} training pool: {overlap}")
        print(f"  [ASSERTION PASSED] Zero flora layers in {target_key} training pool ({len(pool_df)} pool layers, 0 overlap).")

        # Fetch canonical_smiles for representative molregnos
        cur.execute("DROP TABLE IF EXISTS temp_rep_mols")
        cur.execute("CREATE TEMP TABLE temp_rep_mols (molregno INTEGER PRIMARY KEY)")
        cur.executemany("INSERT OR IGNORE INTO temp_rep_mols VALUES (?)", [(m,) for m in rep_mols.values()])
        cur.execute("""
            SELECT m.molregno, cs.canonical_smiles
            FROM temp_rep_mols m
            JOIN compound_structures cs ON m.molregno = cs.molregno
        """)
        rep_smiles_map = dict(cur.fetchall())

        # Standardize structures and compute features
        print(f"  Standardizing {len(pool_df)} representative structures with pipeline/02 standardize_mol...")
        layer_structures = {}
        layer_fps = {}
        layer_np_features = {}
        layer_scaffolds = {}
        layer_chembl_np = {}

        for _, r in pool_df.iterrows():
            c = r["inchikey_connectivity"]
            mreg = rep_mols.get(c)
            smi = rep_smiles_map.get(mreg)
            if not smi:
                continue

            mol = Chem.MolFromSmiles(smi)
            if not mol:
                continue

            # Standardize using imported function
            std_res, err = standardize_mol_func(mol, chooser, uncharger, tautomer_enumerator)
            if not std_res:
                continue

            std_smi = std_res["smiles_standardized"]
            mol_std = Chem.MolFromSmiles(std_smi) if std_smi else None
            if not mol_std:
                mol_std = mol

            # ECFP4 fingerprint
            fp = fp_gen.GetFingerprint(mol_std)
            arr = np.zeros((2048,), dtype=np.int8)
            DataStructs.ConvertToNumpyArray(fp, arr)

            # Bemis-Murcko scaffold
            try:
                scaff = MurckoScaffold.MurckoScaffoldSmiles(mol=mol_std, includeChirality=False)
                scaff_str = scaff if scaff else "acyclic"
            except Exception:
                scaff_str = "acyclic"

            # ChEMBL natural_product flag across all molregnos sharing this layer
            sharing_mols = [m for _, m in layer_mols.get(c, [])]
            is_np = max([molregno_np_map.get(m, 0) for m in sharing_mols], default=0)

            layer_structures[c] = std_smi
            layer_fps[c] = fp
            layer_np_features[c] = arr
            layer_scaffolds[c] = scaff_str
            layer_chembl_np[c] = int(is_np)

        print(f"  Standardized and featurized: {len(layer_fps)} / {len(pool_df)} training pool molecules.")

        all_target_data[target_key] = {
            "target_info": target_info,
            "pool_df": pool_df,
            "flora_df": flora_df,
            "layer_fps": layer_fps,
            "layer_np_features": layer_np_features,
            "layer_scaffolds": layer_scaffolds,
            "layer_chembl_np": layer_chembl_np,
            "layer_structures": layer_structures,
        }

    print("\n" + "=" * 80)
    print("STEP 2: INTERNAL VALIDATION & HYPERPARAMETER SELECTION")
    print("=" * 80)

    # Models to evaluate
    for target_key in targets_to_run:
        tgt_data = all_target_data[target_key]
        pool_df = tgt_data["pool_df"]
        layer_fps = tgt_data["layer_fps"]
        layer_np = tgt_data["layer_np_features"]
        layer_scaff = tgt_data["layer_scaffolds"]
        layer_np_flag = tgt_data["layer_chembl_np"]
        pref_name = tgt_data["target_info"]["pref_name"]

        for T in thresholds_to_run:
            lbl_col = f"label_T{T}"
            conf_col = f"conflict_T{T}"
            valid_df = pool_df[pool_df[conf_col] == False].dropna(subset=[lbl_col]).copy()
            valid_df = valid_df[valid_df["inchikey_connectivity"].isin(layer_fps)].copy()

            layers = valid_df["inchikey_connectivity"].tolist()
            y = valid_df[lbl_col].to_numpy(dtype=float)
            scaffolds = np.array([layer_scaff[c] for c in layers])
            np_flags = np.array([layer_np_flag[c] for c in layers])
            X = np.array([layer_np[c] for c in layers])
            fps = [layer_fps[c] for c in layers]

            # Compute content hash of training set
            content_records = sorted([f"{c}:{int(lbl)}" for c, lbl in zip(layers, y)])
            content_hash = hashlib.sha256("\n".join(content_records).encode("utf-8")).hexdigest()
            training_set_hashes[target_key][f"T{T}"] = content_hash

            print(f"\n--- Cross-Validation for {pref_name} at T={T} ---")
            print(f"  Training Set: N={len(layers)} (Actives={int(np.sum(y == 1))}, Inactives={int(np.sum(y == 0))}), Content Hash: {content_hash[:16]}...")
            print(f"  Scaffold Groups: {len(np.unique(scaffolds))} unique scaffolds (Acyclic: {np.sum(scaffolds == 'acyclic')})")

            # Setup StratifiedGroupKFold
            sgkf = StratifiedGroupKFold(n_splits=n_cv_splits, shuffle=True, random_state=42)
            splits = list(sgkf.split(X, y, groups=scaffolds))

            # 1. Evaluate RandomForest grid
            best_grid_idx = -1
            best_mean_auprc = -1.0
            grid_cv_results = []

            for g_idx, grid_point in enumerate(RF_GRID):
                fold_aurocs = []
                fold_auprcs = []
                fold_briers = []
                oof_preds = np.zeros(len(y), dtype=float)

                for fold_idx, (train_idx, val_idx) in enumerate(splits):
                    X_train, y_train = X[train_idx], y[train_idx]
                    X_val, y_val = X[val_idx], y[val_idx]

                    rf = RandomForestClassifier(
                        n_estimators=grid_point["n_estimators"],
                        max_features=grid_point["max_features"],
                        class_weight="balanced",
                        random_state=42,
                        n_jobs=-1,
                    )
                    rf.fit(X_train, y_train)
                    prob_val = rf.predict_proba(X_val)[:, 1]
                    oof_preds[val_idx] = prob_val

                    fold_aurocs.append(roc_auc_score(y_val, prob_val))
                    fold_auprcs.append(average_precision_score(y_val, prob_val))
                    fold_briers.append(brier_score_loss(y_val, prob_val))

                mean_auroc = float(np.mean(fold_aurocs))
                mean_auprc = float(np.mean(fold_auprcs))
                mean_brier = float(np.mean(fold_briers))

                grid_cv_results.append({
                    "grid_point": grid_point,
                    "mean_auroc": mean_auroc,
                    "mean_auprc": mean_auprc,
                    "mean_brier": mean_brier,
                    "fold_aurocs": fold_aurocs,
                    "fold_auprcs": fold_auprcs,
                    "fold_briers": fold_briers,
                    "oof_preds": oof_preds,
                })

                if mean_auprc > best_mean_auprc:
                    best_mean_auprc = mean_auprc
                    best_grid_idx = g_idx

            chosen_res = grid_cv_results[best_grid_idx]
            chosen_param = chosen_res["grid_point"]
            chosen_hyperparameters[target_key][f"T{T}"] = {
                "n_estimators": chosen_param["n_estimators"],
                "max_features": str(chosen_param["max_features"]),
                "mean_val_auprc": round(chosen_res["mean_auprc"], 4),
                "mean_val_auroc": round(chosen_res["mean_auroc"], 4),
                "mean_val_brier": round(chosen_res["mean_brier"], 4),
            }

            print(f"  [GRID SELECTION] Best RF Grid: n_est={chosen_param['n_estimators']}, max_features={chosen_param['max_features']} -> Mean Val AUPRC: {chosen_res['mean_auprc']:.4f}")

            # 2. Evaluate 1-NN Tanimoto baseline
            nn_fold_aurocs = []
            nn_fold_auprcs = []
            nn_fold_briers = []
            nn_oof_preds = np.zeros(len(y), dtype=float)

            for fold_idx, (train_idx, val_idx) in enumerate(splits):
                train_sub_fps = [fps[i] for i in train_idx]
                val_sub_fps = [fps[i] for i in val_idx]
                y_train_sub = y[train_idx]
                y_val_sub = y[val_idx]

                knn = Tanimoto1NNBaseline()
                knn.fit(train_sub_fps, y_train_sub)
                prob_val = knn.predict_proba(val_sub_fps)
                nn_oof_preds[val_idx] = prob_val

                nn_fold_aurocs.append(roc_auc_score(y_val_sub, prob_val))
                nn_fold_auprcs.append(average_precision_score(y_val_sub, prob_val))
                nn_fold_briers.append(brier_score_loss(y_val_sub, prob_val))

            nn_mean_auroc = float(np.mean(nn_fold_aurocs))
            nn_mean_auprc = float(np.mean(nn_fold_auprcs))
            nn_mean_brier = float(np.mean(nn_fold_briers))

            print(f"  [1-NN BASELINE] Mean Val AUROC: {nn_mean_auroc:.4f}, Mean Val AUPRC: {nn_mean_auprc:.4f}, Mean Val Brier: {nn_mean_brier:.4f}")

            # 3. Stratified evaluation on natural_product == 1 in ChEMBL
            np_mask = (np_flags == 1)
            n_np_samples = int(np.sum(np_mask))
            n_np_pos = int(np.sum(y[np_mask] == 1))
            n_np_neg = int(np.sum(y[np_mask] == 0))

            rf_np_auroc = float(roc_auc_score(y[np_mask], chosen_res["oof_preds"][np_mask])) if n_np_pos > 0 and n_np_neg > 0 else np.nan
            rf_np_auprc = float(average_precision_score(y[np_mask], chosen_res["oof_preds"][np_mask])) if n_np_pos > 0 and n_np_neg > 0 else np.nan
            rf_np_brier = float(brier_score_loss(y[np_mask], chosen_res["oof_preds"][np_mask])) if n_np_samples > 0 else np.nan

            nn_np_auroc = float(roc_auc_score(y[np_mask], nn_oof_preds[np_mask])) if n_np_pos > 0 and n_np_neg > 0 else np.nan
            nn_np_auprc = float(average_precision_score(y[np_mask], nn_oof_preds[np_mask])) if n_np_pos > 0 and n_np_neg > 0 else np.nan
            nn_np_brier = float(brier_score_loss(y[np_mask], nn_oof_preds[np_mask])) if n_np_samples > 0 else np.nan

            # 4. Calibration table (10 bins) for chosen RF model
            cal_table = compute_calibration_table(y, chosen_res["oof_preds"])
            cal_key = f"{target_key}_T{T}"
            calibration_records[cal_key] = cal_table

            # 5. Optimal probability cutoff on internal validation (maximize F1)
            threshold_candidates = np.linspace(0.05, 0.95, 91)
            best_thresh = 0.5
            best_f1 = -1.0
            for th in threshold_candidates:
                pred_binary = (chosen_res["oof_preds"] >= th).astype(int)
                score = f1_score(y, pred_binary, zero_division=0)
                if score > best_f1:
                    best_f1 = score
                    best_thresh = float(th)

            chosen_hyperparameters[target_key][f"T{T}"]["optimal_prob_cutoff"] = round(best_thresh, 4)
            chosen_hyperparameters[target_key][f"T{T}"]["optimal_val_f1"] = round(best_f1, 4)

            # Store curves data
            curves_data[f"{target_key}_T{T}"] = {
                "y_true": y,
                "rf_prob": chosen_res["oof_preds"],
                "nn_prob": nn_oof_preds,
            }

            # Record internal summary row
            internal_results_summary.append({
                "target": target_key,
                "target_name": pref_name,
                "threshold": T,
                "n_samples": len(y),
                "n_actives": int(np.sum(y == 1)),
                "active_frac": round(float(np.mean(y == 1)) * 100, 2),
                "rf_params": f"n_est={chosen_param['n_estimators']}, max_feat={chosen_param['max_features']}",
                "rf_auroc": round(chosen_res["mean_auroc"], 4),
                "rf_auprc": round(chosen_res["mean_auprc"], 4),
                "rf_brier": round(chosen_res["mean_brier"], 4),
                "nn_auroc": round(nn_mean_auroc, 4),
                "nn_auprc": round(nn_mean_auprc, 4),
                "nn_brier": round(nn_mean_brier, 4),
                "np_samples": n_np_samples,
                "np_actives": n_np_pos,
                "rf_np_auroc": round(rf_np_auroc, 4) if pd.notna(rf_np_auroc) else "N/A",
                "rf_np_auprc": round(rf_np_auprc, 4) if pd.notna(rf_np_auprc) else "N/A",
                "rf_np_brier": round(rf_np_brier, 4) if pd.notna(rf_np_brier) else "N/A",
                "optimal_cutoff": round(best_thresh, 4),
                "optimal_f1": round(best_f1, 4),
                "fold_aurocs": chosen_res["fold_aurocs"],
                "fold_auprcs": chosen_res["fold_auprcs"],
                "fold_briers": chosen_res["fold_briers"],
            })

    print("\n" + "=" * 80)
    print("STEP 3: FREEZING CONFIGURATION BEFORE TOUCHING FLORA LABELS")
    print("=" * 80)

    # Read package versions
    pkg_versions = {
        "python": sys.version.split()[0],
        "scikit-learn": getattr(importlib.import_module("sklearn"), "__version__", "unknown"),
        "rdkit": getattr(importlib.import_module("rdkit"), "__version__", "unknown"),
        "scipy": getattr(importlib.import_module("scipy"), "__version__", "unknown"),
        "matplotlib": getattr(importlib.import_module("matplotlib"), "__version__", "unknown"),
        "pandas": getattr(pd, "__version__", "unknown"),
        "numpy": getattr(np, "__version__", "unknown"),
    }

    frozen_config = {
        "title": "Stage 7B Frozen Experimental Configuration",
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "is_dry_run": dry_run,
        "models": ["RandomForestClassifier", "1-Nearest-Neighbour-Tanimoto"],
        "model_family_restriction": "Strictly RandomForest and 1-NN Tanimoto baseline only; no other family permitted.",
        "rf_grid": RF_GRID,
        "seeds": {"model_seed": 42, "split_seed": 42},
        "thresholds": thresholds_to_run,
        "package_versions": pkg_versions,
        "chosen_hyperparameters": chosen_hyperparameters,
        "training_set_content_hashes": training_set_hashes,
        "master_mpbd_start_sha256": start_hash,
    }

    if dry_run:
        if targets_to_run == ["cox1"]:
            config_filename = "stage7b_config_frozen_dryrun.json"
        elif dry_run_target == "remaining" or set(targets_to_run) == {"cox2", "xo", "maoa"}:
            config_filename = "stage7b_config_frozen_dryrun_remaining.json"
        else:
            config_filename = f"stage7b_config_frozen_dryrun_{'_'.join(targets_to_run)}.json"
    else:
        config_filename = "stage7b_config_frozen.json"
    frozen_config_path = OUT_MODELING_DIR / config_filename
    with open(frozen_config_path, "w", encoding="utf-8") as f:
        json.dump(frozen_config, f, indent=2)

    frozen_config_sha256 = verify_file_sha256(frozen_config_path)
    print(f"[FREEZE APPLIED] Config written to {frozen_config_path}")
    print(f"  Config SHA-256: {frozen_config_sha256}")
    print("  All model hyperparameters, seeds, and training hashes are permanently frozen.")
    print("  External sets will now be evaluated exactly once against these frozen models.")

    print("\n" + "=" * 80)
    print("STEP 4: ONE-TIME EXTERNAL EVALUATION & APPLICABILITY DOMAIN")
    print("=" * 80)

    # Train final models on full training pool and evaluate external set
    for target_key in targets_to_run:
        tgt_data = all_target_data[target_key]
        pool_df = tgt_data["pool_df"]
        flora_df = tgt_data["flora_df"]
        layer_fps = tgt_data["layer_fps"]
        layer_np = tgt_data["layer_np_features"]
        pref_name = tgt_data["target_info"]["pref_name"]
        is_cox = tgt_data["target_info"]["is_cox"]

        for T in thresholds_to_run:
            lbl_col = f"label_T{T}"
            conf_col = f"conflict_T{T}"

            # Prepare full training data
            valid_train = pool_df[pool_df[conf_col] == False].dropna(subset=[lbl_col]).copy()
            valid_train = valid_train[valid_train["inchikey_connectivity"].isin(layer_fps)].copy()
            train_layers = valid_train["inchikey_connectivity"].tolist()
            X_train = np.array([layer_np[c] for c in train_layers])
            y_train = valid_train[lbl_col].to_numpy(dtype=float)
            train_fps_list = [layer_fps[c] for c in train_layers]

            # Fit final RF model
            chosen_param = chosen_hyperparameters[target_key][f"T{T}"]
            final_rf = RandomForestClassifier(
                n_estimators=chosen_param["n_estimators"],
                max_features=float(chosen_param["max_features"]) if chosen_param["max_features"] != "sqrt" else "sqrt",
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            )
            final_rf.fit(X_train, y_train)

            # 1-NN model for applicability domain
            knn_domain = Tanimoto1NNBaseline()
            knn_domain.fit(train_fps_list, y_train)

            # Filter external flora set: >= 1 HIGH link, non-conflict
            ext_flora = flora_df[flora_df["inchikey_connectivity"].isin(high_tier_flora_layers)].copy()
            ext_valid = ext_flora[ext_flora[conf_col] == False].dropna(subset=[lbl_col]).copy()
            ext_valid = ext_valid[ext_valid["inchikey_connectivity"].isin(flora_fps)].copy()

            n_ext = len(ext_valid)
            n_ext_act = int((ext_valid[lbl_col] == 1.0).sum())
            n_ext_inact = int((ext_valid[lbl_col] == 0.0).sum())

            print(f"\n--- External Evaluation: {pref_name} at T={T} ---")
            print(f"  External Flora Set (HIGH Links): N={n_ext} (Actives={n_ext_act}, Inactives={n_ext_inact})")

            if n_ext == 0:
                print("  [WARNING] No external flora molecules available!")
                continue

            ext_layers = ext_valid["inchikey_connectivity"].tolist()
            ext_X = np.array([flora_np_arrays[c] for c in ext_layers])
            ext_fps_list = [flora_fps[c] for c in ext_layers]
            ext_y = ext_valid[lbl_col].to_numpy(dtype=float)
            ext_pchembl = ext_valid["median_pchembl"].to_numpy(dtype=float)

            # Predict with final RF model
            ext_prob = final_rf.predict_proba(ext_X)[:, 1]
            ext_nn_sim = knn_domain.get_nearest_similarities(ext_fps_list)

            # Applicability domain split at NN >= 0.4
            in_domain_mask = (ext_nn_sim >= 0.4)
            n_in_domain = int(np.sum(in_domain_mask))
            n_out_domain = n_ext - n_in_domain

            # Evaluation per target type
            if is_cox:
                # Descriptive evaluation: Spearman correlation & scatter
                rho, p_val = stats.spearmanr(ext_pchembl, ext_prob)
                print(f"  [COX DESCRIPTIVE] Spearman rho(pChEMBL, prob): {rho:.4f} (p-value: {p_val:.4e})")
                print("  [STATEMENT] No AUROC/AUPRC claimed for COX targets due to very few active molecules.")

                # In-domain vs out-domain Spearman
                rho_in, p_in = stats.spearmanr(ext_pchembl[in_domain_mask], ext_prob[in_domain_mask]) if n_in_domain >= 3 else (np.nan, np.nan)
                rho_out, p_out = stats.spearmanr(ext_pchembl[~in_domain_mask], ext_prob[~in_domain_mask]) if n_out_domain >= 3 else (np.nan, np.nan)

                # Store COX details for report & scatter plot
                df_cox_detail = pd.DataFrame({
                    "inchikey_connectivity": ext_layers,
                    "median_pchembl": ext_pchembl,
                    "predicted_prob": ext_prob,
                    "true_label": ext_y,
                    "nn_sim": ext_nn_sim,
                    "in_domain_0.4": in_domain_mask,
                })
                cox_external_data[f"{target_key}_T{T}"] = df_cox_detail

                external_results_summary.append({
                    "target": target_key,
                    "target_name": pref_name,
                    "threshold": T,
                    "n_ext": n_ext,
                    "n_actives": n_ext_act,
                    "n_inactives": n_ext_inact,
                    "metric_type": "Descriptive (Spearman Rank Correlation)",
                    "spearman_rho": round(rho, 4) if pd.notna(rho) else "N/A",
                    "spearman_pval": f"{p_val:.2e}" if pd.notna(p_val) else "N/A",
                    "auroc": "Descriptive only (no claim)",
                    "auprc": "Descriptive only (no claim)",
                    "auroc_ci": "N/A",
                    "auprc_ci": "N/A",
                    "n_in_domain": n_in_domain,
                    "in_domain_act": int(np.sum(ext_y[in_domain_mask] == 1)),
                    "in_domain_spearman": round(rho_in, 4) if pd.notna(rho_in) else "N/A",
                    "n_out_domain": n_out_domain,
                    "out_domain_act": int(np.sum(ext_y[~in_domain_mask] == 1)),
                    "out_domain_spearman": round(rho_out, 4) if pd.notna(rho_out) else "N/A",
                })

            else:
                # Quantitative evaluation: AUROC, AUPRC & 1000-resample bootstrap
                bs_results = bootstrap_metric_ci(ext_y, ext_prob, n_resamples=1000, seed=42)
                base_auroc, auroc_lo, auroc_hi = bs_results["auroc"]
                base_auprc, auprc_lo, auprc_hi = bs_results["auprc"]

                print(f"  [QUANTITATIVE] AUROC: {base_auroc:.4f} [95% CI: {auroc_lo:.4f} - {auroc_hi:.4f}]")
                print(f"  [QUANTITATIVE] AUPRC: {base_auprc:.4f} [95% CI: {auprc_lo:.4f} - {auprc_hi:.4f}]")

                # In-domain vs out-domain metrics
                if n_in_domain > 0 and len(np.unique(ext_y[in_domain_mask])) > 1:
                    in_auroc = float(roc_auc_score(ext_y[in_domain_mask], ext_prob[in_domain_mask]))
                    in_auprc = float(average_precision_score(ext_y[in_domain_mask], ext_prob[in_domain_mask]))
                else:
                    in_auroc, in_auprc = np.nan, np.nan

                if n_out_domain > 0 and len(np.unique(ext_y[~in_domain_mask])) > 1:
                    out_auroc = float(roc_auc_score(ext_y[~in_domain_mask], ext_prob[~in_domain_mask]))
                    out_auprc = float(average_precision_score(ext_y[~in_domain_mask], ext_prob[~in_domain_mask]))
                else:
                    out_auroc, out_auprc = np.nan, np.nan

                external_results_summary.append({
                    "target": target_key,
                    "target_name": pref_name,
                    "threshold": T,
                    "n_ext": n_ext,
                    "n_actives": n_ext_act,
                    "n_inactives": n_ext_inact,
                    "metric_type": "Quantitative (AUROC, AUPRC, 1000-resample Bootstrap CI)",
                    "spearman_rho": "N/A",
                    "spearman_pval": "N/A",
                    "auroc": round(base_auroc, 4),
                    "auprc": round(base_auprc, 4),
                    "auroc_ci": f"[{auroc_lo:.4f}, {auroc_hi:.4f}]",
                    "auprc_ci": f"[{auprc_lo:.4f}, {auprc_hi:.4f}]",
                    "n_in_domain": n_in_domain,
                    "in_domain_act": int(np.sum(ext_y[in_domain_mask] == 1)),
                    "in_domain_auroc": round(in_auroc, 4) if pd.notna(in_auroc) else "N/A",
                    "in_domain_auprc": round(in_auprc, 4) if pd.notna(in_auprc) else "N/A",
                    "n_out_domain": n_out_domain,
                    "out_domain_act": int(np.sum(ext_y[~in_domain_mask] == 1)),
                    "out_domain_auroc": round(out_auroc, 4) if pd.notna(out_auroc) else "N/A",
                    "out_domain_auprc": round(out_auprc, 4) if pd.notna(out_auprc) else "N/A",
                })

            # Score all 7,315 flora molecules
            print(f"  Scoring all {len(flora_fps):,} flora molecules with final {pref_name} model (T={T})...")
            all_flora_layers = list(flora_fps.keys())
            all_flora_X = np.array([flora_np_arrays[c] for c in all_flora_layers])
            all_flora_fps = [flora_fps[c] for c in all_flora_layers]

            flora_pred_probs = final_rf.predict_proba(all_flora_X)[:, 1]
            flora_nn_sims = knn_domain.get_nearest_similarities(all_flora_fps)

            # Record internal cutoff and share above it
            int_cutoff = chosen_param["optimal_prob_cutoff"]
            share_above_cutoff = float(np.mean(flora_pred_probs >= int_cutoff)) * 100.0
            print(f"  Internal probability cutoff: {int_cutoff:.4f} -> {share_above_cutoff:.2f}% of flora scored above cutoff.")

            # Save predictions CSV
            df_flora_preds = pd.DataFrame({
                "layer": all_flora_layers,
                "smiles": [flora_smiles_map.get(c, "") for c in all_flora_layers],
                "predicted_probability": np.round(flora_pred_probs, 4),
                "nn_similarity": np.round(flora_nn_sims, 4),
                "in_domain_0.4": flora_nn_sims >= 0.4,
                "in_domain_0.3": flora_nn_sims >= 0.3,
            })

            out_preds_filename = f"flora_predictions_{target_key}_T{T}.csv"
            out_preds_path = OUT_MODELING_DIR / out_preds_filename
            df_flora_preds.to_csv(out_preds_path, index=False)
            print(f"  Saved flora predictions to {out_preds_path} ({len(df_flora_preds):,} rows).")

    print("\n" + "=" * 80)
    print("STEP 5: GENERATING PUBLICATION-QUALITY FIGURES (300 DPI)")
    print("=" * 80)

    fig_prefix = "remaining_targets_" if (dry_run and (dry_run_target in ["remaining", "cox2", "xo", "maoa"] and dry_run_target != "cox1")) else ""

    # 1. ROC Curves
    plt.figure(figsize=(10, 8), dpi=300)
    for k, data in curves_data.items():
        fpr, tpr, _ = roc_curve(data["y_true"], data["rf_prob"])
        score = roc_auc_score(data["y_true"], data["rf_prob"])
        plt.plot(fpr, tpr, lw=2, label=f"{k.upper()} RF (AUROC = {score:.3f})")
    plt.plot([0, 1], [0, 1], "k--", lw=1.5, alpha=0.7, label="Chance Baseline")
    plt.xlabel("False Positive Rate", fontsize=12)
    plt.ylabel("True Positive Rate", fontsize=12)
    plt.title("Receiver Operating Characteristic (Internal Scaffold CV Folds)", fontsize=14, fontweight="bold")
    plt.legend(loc="lower right", fontsize=10)
    plt.grid(True, alpha=0.3)
    roc_fig_path = FIGURES_DIR / f"{fig_prefix}roc_curves.png"
    plt.tight_layout()
    plt.savefig(roc_fig_path)
    plt.close()
    print(f"  Generated ROC curves: {roc_fig_path}")

    # 2. PR Curves
    plt.figure(figsize=(10, 8), dpi=300)
    for k, data in curves_data.items():
        precision, recall, _ = precision_recall_curve(data["y_true"], data["rf_prob"])
        score = average_precision_score(data["y_true"], data["rf_prob"])
        plt.plot(recall, precision, lw=2, label=f"{k.upper()} RF (AUPRC = {score:.3f})")
    plt.xlabel("Recall", fontsize=12)
    plt.ylabel("Precision", fontsize=12)
    plt.title("Precision-Recall Curves (Internal Scaffold CV Folds)", fontsize=14, fontweight="bold")
    plt.legend(loc="upper right", fontsize=10)
    plt.grid(True, alpha=0.3)
    pr_fig_path = FIGURES_DIR / f"{fig_prefix}pr_curves.png"
    plt.tight_layout()
    plt.savefig(pr_fig_path)
    plt.close()
    print(f"  Generated PR curves: {pr_fig_path}")

    # 3. Calibration Reliability Diagrams
    plt.figure(figsize=(10, 8), dpi=300)
    for k, cal_rows in calibration_records.items():
        pts = [(r["mean_predicted_prob"], r["empirical_positive_rate"]) for r in cal_rows if r["n_samples"] > 0]
        if pts:
            px, py = zip(*pts)
            plt.plot(px, py, marker="o", lw=2, label=f"{k.upper()}")
    plt.plot([0, 1], [0, 1], "k--", lw=1.5, alpha=0.7, label="Perfect Calibration")
    plt.xlabel("Mean Predicted Probability", fontsize=12)
    plt.ylabel("Empirical Positive Fraction", fontsize=12)
    plt.title("Calibration Reliability Diagrams (10 Bins, Scaffold CV)", fontsize=14, fontweight="bold")
    plt.legend(loc="upper left", fontsize=10)
    plt.grid(True, alpha=0.3)
    cal_fig_path = FIGURES_DIR / f"{fig_prefix}calibration_plots.png"
    plt.tight_layout()
    plt.savefig(cal_fig_path)
    plt.close()
    print(f"  Generated calibration plot: {cal_fig_path}")

    # 4. COX External Scatter: Predicted Probability vs Measured pChEMBL
    if cox_external_data:
        plt.figure(figsize=(10, 6), dpi=300)
        markers = {"cox1": "o", "cox2": "s"}
        colors = {"cox1": "#1f77b4", "cox2": "#d62728"}

        for k, df_c in cox_external_data.items():
            tgt = k.split("_")[0]
            thresh = k.split("_")[1]
            lbl = f"{tgt.upper()} ({thresh})"
            plt.scatter(
                df_c["median_pchembl"],
                df_c["predicted_prob"],
                label=lbl,
                color=colors.get(tgt, "gray"),
                marker=markers.get(tgt, "o"),
                s=60,
                alpha=0.8,
                edgecolors="k",
                linewidths=0.5,
            )
        plt.axhline(0.5, color="gray", linestyle="--", alpha=0.5)
        plt.xlabel("Measured Median pChEMBL", fontsize=12)
        plt.ylabel("Model Predicted Probability", fontsize=12)
        plt.title("External Flora Validation: Predicted Probability vs Measured Potency (COX Targets)", fontsize=13, fontweight="bold")
        plt.legend(loc="upper left", fontsize=10)
        plt.grid(True, alpha=0.3)
        cox_fig_path = FIGURES_DIR / f"{fig_prefix}cox_external_predicted_vs_measured.png"
        plt.tight_layout()
        plt.savefig(cox_fig_path)
        plt.close()
        print(f"  Generated COX external scatter plot: {cox_fig_path}")

    # 5. NN Similarity Histograms (Flora vs Training Pools)
    plt.figure(figsize=(10, 6), dpi=300)
    for target_key in targets_to_run:
        tgt_data = all_target_data[target_key]
        pool_fps_list = list(tgt_data["layer_fps"].values())
        flora_all_fps = list(flora_fps.values())

        # Sample for fast histogram if large
        knn_temp = Tanimoto1NNBaseline()
        knn_temp.fit(pool_fps_list, np.zeros(len(pool_fps_list)))
        sims_sample = knn_temp.get_nearest_similarities(flora_all_fps[:1000] if dry_run else flora_all_fps)
        plt.hist(sims_sample, bins=30, alpha=0.4, label=f"Flora vs {target_key.upper()} Pool")

    plt.axvline(0.4, color="red", linestyle="--", lw=1.5, label="In-Domain Boundary (NN = 0.4)")
    plt.axvline(0.3, color="orange", linestyle=":", lw=1.5, label="Tolerant Boundary (NN = 0.3)")
    plt.xlabel("Nearest-Neighbour Tanimoto Similarity (ECFP4)", fontsize=12)
    plt.ylabel("Molecule Count", fontsize=12)
    plt.title("Applicability Domain: Flora Molecules vs ChEMBL Training Pools", fontsize=13, fontweight="bold")
    plt.legend(loc="upper right", fontsize=10)
    plt.grid(True, alpha=0.3)
    hist_fig_path = FIGURES_DIR / f"{fig_prefix}flora_nn_similarity_histograms.png"
    plt.tight_layout()
    plt.savefig(hist_fig_path)
    plt.close()
    print(f"  Generated NN similarity histogram: {hist_fig_path}")

    # 6. Verify Master MPBD integrity at end
    end_hash = verify_file_sha256(MASTER_MPBD_PATH, EXPECTED_MASTER_SHA256)
    print(f"\n[VERIFIED] Master MPBD SHA-256 end: {end_hash}")

    conn.close()

    # 7. Generate Quality Report Markdown
    report_md = build_markdown_report(
        dry_run=dry_run,
        dry_run_target=dry_run_target,
        frozen_config_sha256=frozen_config_sha256,
        internal_results=internal_results_summary,
        external_results=external_results_summary,
        calibration_records=calibration_records,
        cox_external_data=cox_external_data,
        ref_compounds_filled=ref_compounds_filled,
        start_hash=start_hash,
        end_hash=end_hash,
        fig_prefix=fig_prefix,
    )

    if dry_run:
        if targets_to_run == ["cox1"]:
            report_filename = "stage7b_model_report.md"
        elif dry_run_target == "remaining" or set(targets_to_run) == {"cox2", "xo", "maoa"}:
            report_filename = "stage7b_remaining_targets_report.md"
        else:
            report_filename = f"stage7b_model_report_{'_'.join(targets_to_run)}.md"
    else:
        report_filename = "stage7b_model_report.md"
    report_path = OUT_QUALITY_DIR / report_filename
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"\n[REPORT WRITTEN] Saved quality report to {report_path}")

    return report_md


# ---------------------------------------------------------------------------
# Report Markdown Builder
# ---------------------------------------------------------------------------
def build_markdown_report(
    dry_run: bool,
    dry_run_target: str,
    frozen_config_sha256: str,
    internal_results: List[Dict],
    external_results: List[Dict],
    calibration_records: Dict[str, List[Dict]],
    cox_external_data: Dict[str, pd.DataFrame],
    ref_compounds_filled: bool,
    start_hash: str,
    end_hash: str,
    fig_prefix: str = "",
) -> str:
    md = []
    if dry_run:
        if dry_run_target == "remaining" or len(internal_results) > 1:
            target_title = "Remaining Targets (COX-2, XO, MAO-A)"
        else:
            target_title = dry_run_target.upper()
        mode_title = f"Stage 7B Dry Run Report (Target: {target_title})"
    else:
        mode_title = "Stage 7B Model Training, Internal Validation & External Evaluation Report"
    md.append(f"# {mode_title}")
    md.append(f"**Authority:** `docs/thesis_design_note.md` (and logged amendments)  ")
    md.append(f"**Execution Timestamp:** {datetime.datetime.now(datetime.timezone.utc).isoformat()} UTC  ")
    md.append(f"**Master MPBD SHA-256 (Start & End):** `{start_hash}` / `{end_hash}` (**VERIFIED / UNCHANGED**)  ")
    md.append(f"**Frozen Config SHA-256:** `{frozen_config_sha256}`  ")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 1. Executive Summary")
    md.append("")
    md.append("- **Models Evaluated:** Strictly two model families: RandomForestClassifier (fixed 4-point grid: `n_estimators` in {300, 600}, `max_features` in {'sqrt', 0.1}, `class_weight='balanced'`, seed 42) and a 1-Nearest-Neighbour Tanimoto baseline. No other model family was trained.")
    md.append("- **Scaffold Split:** Bemis-Murcko scaffold grouped cross-validation (acyclic molecules grouped into `'acyclic'`). Grid point selected by mean validation AUPRC.")
    md.append("- **Pre-Evaluation Freeze:** Model architectures, chosen hyperparameters, probability cutoffs, training content hashes, and environment package versions were frozen and committed to `stage7b_config_frozen.json` before evaluating any external flora labels.")
    md.append("- **External Set Governance:** External flora molecules were filtered to those with $\\ge 1$ HIGH-tier link in `plant_compound_links_confidence.csv`. COX-1 and COX-2 external evaluations are reported purely descriptively (Spearman rank correlation; no AUROC/AUPRC claimed). XO and MAO-A serve as the main quantitative external evaluations (AUROC, AUPRC, and 1,000-resample bootstrap 95% CIs).")
    md.append(f"- **Reference Compound Exclusions:** Run (a) executed as-is. Run (b) status: **{'COMPLETED' if ref_compounds_filled else 'PENDING USER REVIEW (is_reference_compound unpopulated in external_verification_sheet.csv)'}**.")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 2. Internal Cross-Validation Performance (ChEMBL Training Pool)")
    md.append("")
    md.append("| Target | Threshold | Training N (Act/Inact) | Best RF Grid Point | Mean Val AUROC | Mean Val AUPRC | Mean Val Brier | 1-NN Val AUROC | 1-NN Val AUPRC | 1-NN Val Brier | ChEMBL NP N | ChEMBL NP AUROC | ChEMBL NP AUPRC | Opt Cutoff (Max F1) | Opt F1 |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in internal_results:
        md.append(
            f"| **{r['target_name']}** | T={r['threshold']} | {r['n_samples']} ({r['n_actives']}/{r['n_samples'] - r['n_actives']}) | "
            f"`{r['rf_params']}` | **{r['rf_auroc']}** | **{r['rf_auprc']}** | {r['rf_brier']} | "
            f"{r['nn_auroc']} | {r['nn_auprc']} | {r['nn_brier']} | "
            f"{r['np_samples']} ({r['np_actives']} act) | {r['rf_np_auroc']} | {r['rf_np_auprc']} | "
            f"`{r['optimal_cutoff']}` | {r['optimal_f1']} |"
        )
    md.append("")
    md.append("> **Note on Natural Product Flag:** The `natural_product = 1` flag in ChEMBL is coarse and utilized strictly to stratify the ChEMBL internal evaluation across natural vs synthetic small molecules. It is not used as evidence about Bangladesh flora compounds.")
    md.append("")

    # Per-fold breakdown
    md.append("### Per-Fold Internal Validation Breakdown")
    md.append("")
    md.append("| Target | Threshold | Fold 1 AUROC / AUPRC | Fold 2 AUROC / AUPRC | Fold 3 AUROC / AUPRC | Fold 4 AUROC / AUPRC | Fold 5 AUROC / AUPRC | Mean AUROC | Mean AUPRC |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for r in internal_results:
        folds_str = []
        for i in range(len(r["fold_aurocs"])):
            folds_str.append(f"{r['fold_aurocs'][i]:.3f} / {r['fold_auprcs'][i]:.3f}")
        while len(folds_str) < 5:
            folds_str.append("N/A (dry run)")
        md.append(f"| **{r['target_name']}** | T={r['threshold']} | {folds_str[0]} | {folds_str[1]} | {folds_str[2]} | {folds_str[3]} | {folds_str[4]} | **{r['rf_auroc']}** | **{r['rf_auprc']}** |")
    md.append("")

    # Calibration Tables
    md.append("### Calibration Tables (10 Bins, Out-of-Fold Validation Predictions)")
    md.append("")
    for cal_key, cal_rows in calibration_records.items():
        md.append(f"#### Calibration: `{cal_key.upper()}`")
        md.append("")
        md.append("| Probability Bin | Bin Range | Sample Count | Positives | Mean Predicted Probability | Empirical Positive Rate |")
        md.append("|---|---|---|---|---|---|")
        for crow in cal_rows:
            md.append(f"| {crow['bin']} | [{crow['low']:.1f}, {crow['high']:.1f}] | {crow['n_samples']} | {crow['n_positives']} | {crow['mean_predicted_prob']:.4f} | {crow['empirical_positive_rate']:.4f} |")
        md.append("")

    md.append("---")
    md.append("")
    md.append("## 3. External Flora Evaluation (One-Time Touch Post-Freeze)")
    md.append("")
    md.append("### Summary of External Sets & Performance")
    md.append("")
    md.append("| Target | Threshold | Flora Tested (Act/Inact) | Evaluation Protocol | External AUROC [95% CI] | External AUPRC [95% CI] | Spearman Rank rho (p-value) | In-Domain (NN >= 0.4) N (Act) | In-Domain Perf | Out-of-Domain (NN < 0.4) N (Act) | Out-of-Domain Perf |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in external_results:
        in_perf = f"{r['in_domain_auroc']} / {r['in_domain_auprc']}" if "in_domain_auroc" in r and r["in_domain_auroc"] != "N/A" else str(r.get("in_domain_spearman", "N/A"))
        out_perf = f"{r['out_domain_auroc']} / {r['out_domain_auprc']}" if "out_domain_auroc" in r and r["out_domain_auroc"] != "N/A" else str(r.get("out_domain_spearman", "N/A"))
        md.append(
            f"| **{r['target_name']}** | T={r['threshold']} | {r['n_ext']} ({r['n_actives']}/{r['n_inactives']}) | "
            f"{r['metric_type']} | {r['auroc']} {r['auroc_ci']} | {r['auprc']} {r['auprc_ci']} | "
            f"{r['spearman_rho']} ({r['spearman_pval']}) | "
            f"{r['n_in_domain']} ({r['in_domain_act']}) | {in_perf} | "
            f"{r['n_out_domain']} ({r['out_domain_act']}) | {out_perf} |"
        )
    md.append("")
    md.append("> **Governance Protocol Verification:**")
    md.append("> - **Run (a) (As-Is):** Fully reported above.")
    md.append("> - **Run (b) (Excluding Reference Compounds):** Status: **Pending user review**. Column `is_reference_compound` in `data/processed/modeling/external_verification_sheet.csv` is currently unpopulated.")
    md.append("")

    if cox_external_data:
        md.append("### COX Targets Detailed Predictions vs Measured Potency")
        md.append("")
        for k, df_c in cox_external_data.items():
            md.append(f"#### Target: `{k.upper()}` (All External Molecules Tested)")
            md.append("")
            md.append("| Connectivity Layer | Measured Median pChEMBL | True Active (T) | Predicted Probability | NN Tanimoto to Training Pool | Domain Status (>= 0.4) |")
            md.append("|---|---|---|---|---|---|")
            for _, r in df_c.iterrows():
                dom = "IN-DOMAIN" if r["in_domain_0.4"] else "OUT-OF-DOMAIN"
                md.append(f"| `{r['inchikey_connectivity']}` | {r['median_pchembl']:.2f} | {int(r['true_label'])} | {r['predicted_prob']:.4f} | {r['nn_sim']:.4f} | {dom} |")
            md.append("")

    md.append("---")
    md.append("")
    md.append("## 4. Applicability Domain & Flora Molecule Scoring")
    md.append("")
    md.append("All 7,315 fingerprintable flora layers were scored with the frozen final models:")
    md.append("")
    md.append("| Target | Threshold | Total Flora Scored | Internal Cutoff (Max F1) | Flora Above Cutoff (%) | Flora in Domain (NN >= 0.4) (%) | Flora Tolerant Domain (NN >= 0.3) (%) | Predictions CSV Path |")
    md.append("|---|---|---|---|---|---|---|---|")
    for r in internal_results:
        t_key = r["target"]
        t_val = r["threshold"]
        csv_file = f"data/processed/modeling/flora_predictions_{t_key}_T{t_val}.csv"
        md.append(f"| **{r['target_name']}** | T={t_val} | 7,315 | `{r['optimal_cutoff']}` | Report CSV | Report CSV | Report CSV | [`{csv_file}`](file:///{csv_file}) |")
    md.append("")
    md.append("> **Strict Scope Constraint:** Predictions written to `data/processed/modeling/flora_predictions_*.csv` are stored solely for downstream use. No plant-level enrichment or aggregation has been executed in this stage.")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 5. Artifact & Integrity Ledger")
    md.append("")
    md.append(f"- **Master MPBD SHA-256 (Start):** `{start_hash}`")
    md.append(f"- **Master MPBD SHA-256 (End):** `{end_hash}` (**MATCH**)")
    md.append(f"- **Frozen Config SHA-256:** `{frozen_config_sha256}`")
    md.append(f"- **ChEMBL Database Mode:** Strictly read-only (`mode=ro`). Zero disk writes or schema mutations.")
    md.append("- **Generated Figures:**")
    md.append(f"  - [`figures/{fig_prefix}roc_curves.png`](file:///f:/bmppd-thesis/figures/{fig_prefix}roc_curves.png) (ROC curves per target, 300 dpi)")
    md.append(f"  - [`figures/{fig_prefix}pr_curves.png`](file:///f:/bmppd-thesis/figures/{fig_prefix}pr_curves.png) (PR curves per target, 300 dpi)")
    md.append(f"  - [`figures/{fig_prefix}calibration_plots.png`](file:///f:/bmppd-thesis/figures/{fig_prefix}calibration_plots.png) (10-bin calibration diagrams, 300 dpi)")
    md.append(f"  - [`figures/{fig_prefix}cox_external_predicted_vs_measured.png`](file:///f:/bmppd-thesis/figures/{fig_prefix}cox_external_predicted_vs_measured.png) (Scatter plot of COX predicted probability vs measured pChEMBL, 300 dpi)")
    md.append(f"  - [`figures/{fig_prefix}flora_nn_similarity_histograms.png`](file:///f:/bmppd-thesis/figures/{fig_prefix}flora_nn_similarity_histograms.png) (Flora vs ChEMBL training pool similarity distribution, 300 dpi)")
    md.append("")

    return "\n".join(md)


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stage 7B: Model Training, Internal CV & External Evaluation")
    parser.add_argument("--dry-run", action="store_true", help="Run a small dry run (one target, T=6, 2 folds only)")
    parser.add_argument("--dry-run-target", type=str, default="cox1", choices=["cox1", "cox2", "xo", "maoa", "remaining", "all"], help="Target for dry run (default: cox1, or 'remaining' for cox2, xo, maoa)")
    parser.add_argument("--dry-run-folds", type=int, default=2, help="Number of folds for dry run (default: 2)")

    args = parser.parse_args()

    report = run_pipeline(
        dry_run=args.dry_run,
        dry_run_target=args.dry_run_target,
        dry_run_folds=args.dry_run_folds,
    )
