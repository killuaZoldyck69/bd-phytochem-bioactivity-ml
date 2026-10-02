#!/usr/bin/env python3
"""
scripts/rerun_pre_cutoff_chemotype_audit.py
============================================
Evaluates the selection/collider bias flagged in Section 4.5/4.6:
Does the chemotype-transfer relationship (nearest-neighbour Tanimoto similarity to
ChEMBL training pools vs. literature evidence tiers) hold up when evaluated BEFORE
applying the model's predicted probability cutoff?

Compares:
1. Post-Cutoff Link Level (Original thesis cohort: N=1,167 links)
2. Post-Cutoff Structure Level (Unique structures passing cutoff: N=319)
3. Pre-Cutoff Audited Structures (N=319 unique structures evaluated across full ChEMBL training pools)
4. Pre-Cutoff Audited Compound-Target Pairs (N=1,276 pairs across all 4 targets)
5. Pre-Cutoff Audited Pairs on Prioritized Target (N=340 pairs)

Outputs:
- data/quality/pre_vs_post_cutoff_evidence_tests.csv
- data/quality/pre_vs_post_cutoff_descriptive_stats.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

REPO_ROOT = Path(__file__).resolve().parent.parent
SCREENING_SUMMARY_CSV = REPO_ROOT / "data/processed/modeling/compound_screening_summary.csv"
STAGE8_CANDIDATE_CSV = REPO_ROOT / "data/processed/modeling/stage8_integrated_candidate_evidence.csv"
OUTPUT_DIR = REPO_ROOT / "data/quality"

STATUS_ORDER = [
    "LEVEL_A_EXACT_TARGET",
    "LEVEL_B_RELATED_ENDPOINT",
    "CONTRADICTED",
    "NO_RELEVANT_REPORT_FOUND",
]

TIER_RANK = {
    "LEVEL_A_EXACT_TARGET": 4,
    "LEVEL_B_RELATED_ENDPOINT": 3,
    "CONTRADICTED": 2,
    "NO_RELEVANT_REPORT_FOUND": 1,
}


def compute_descriptive_stats(vals: np.ndarray) -> dict:
    n = len(vals)
    if n == 0:
        return {"N": 0, "mean": np.nan, "std": np.nan, "median": np.nan, "IQR": np.nan, "min": np.nan, "max": np.nan}
    q1 = float(np.percentile(vals, 25))
    q3 = float(np.percentile(vals, 75))
    return {
        "N": n,
        "mean": round(float(np.mean(vals)), 4),
        "std": round(float(np.std(vals, ddof=1)), 4) if n > 1 else 0.0,
        "median": round(float(np.median(vals)), 4),
        "IQR": round(q3 - q1, 4),
        "min": round(float(np.min(vals)), 4),
        "max": round(float(np.max(vals)), 4),
        "Q1": round(q1, 4),
        "Q3": round(q3, 4),
    }


def run_tests(df: pd.DataFrame, metric_col: str, group_col: str = "evidence_status") -> dict:
    groups = [df[df[group_col] == st][metric_col].dropna().values for st in STATUS_ORDER]
    kw = stats.kruskal(*groups)

    vals_a = df[df[group_col] == "LEVEL_A_EXACT_TARGET"][metric_col].dropna().values
    vals_e = df[df[group_col] == "NO_RELEVANT_REPORT_FOUND"][metric_col].dropna().values

    mw = stats.mannwhitneyu(vals_a, vals_e, alternative="two-sided")
    r_biserial = 1 - (2 * mw.statistic) / (len(vals_a) * len(vals_e))

    return {
        "kruskal_h": float(kw.statistic),
        "kruskal_p": float(kw.pvalue),
        "mannwhitney_u": float(mw.statistic),
        "mannwhitney_p": float(mw.pvalue),
        "rank_biserial_r": float(r_biserial),
        "n_level_a": len(vals_a),
        "n_level_e": len(vals_e),
        "median_level_a": float(np.median(vals_a)),
        "median_level_e": float(np.median(vals_e)),
    }


def main():
    print("=" * 80)
    print("PRE-CUTOFF VS. POST-CUTOFF CHEMOTYPE-TRANSFER AUDIT")
    print("=" * 80)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df_screen = pd.read_csv(SCREENING_SUMMARY_CSV)
    df_screen_t6 = df_screen[df_screen["threshold"] == 6].copy()

    df_stage8 = pd.read_csv(STAGE8_CANDIDATE_CSV)
    print(f"Loaded {len(df_screen_t6):,} screening predictions across 7,315 molecules.")
    print(f"Loaded {len(df_stage8):,} candidate link records across 319 unique structures.\n")

    # Map each structure to its highest literature evidence tier
    lit_map = df_stage8.groupby("flat_inchikey")["evidence_status"].apply(lambda s: max(s, key=lambda x: TIER_RANK[x])).to_dict()

    # 1. Post-cutoff link level (Original thesis Section 4.5)
    t_post_link = run_tests(df_stage8, "nearest_neighbor_similarity", "evidence_status")
    t_post_link["specification"] = "1. Post-Cutoff Links (Original Section 4.5)"
    t_post_link["selection_condition"] = "Filtered to prob >= cutoff, strict domain, HIGH links"
    t_post_link["total_N"] = len(df_stage8)

    # 2. Post-cutoff unique structures (N=319)
    comp_mean_nn_post = df_stage8.groupby("flat_inchikey")["nearest_neighbor_similarity"].mean()
    df_post_struct = pd.DataFrame({
        "flat_inchikey": list(lit_map.keys()),
        "evidence_status": list(lit_map.values()),
        "nn_similarity": [comp_mean_nn_post[c] for c in lit_map.keys()]
    })
    t_post_struct = run_tests(df_post_struct, "nn_similarity", "evidence_status")
    t_post_struct["specification"] = "2. Post-Cutoff Unique Structures (Deduplicated)"
    t_post_struct["selection_condition"] = "Passed model cutoff on at least one target"
    t_post_struct["total_N"] = len(df_post_struct)

    # 3. Pre-cutoff unique structures (N=319, unconditioned on model pass)
    # Compute true mean NN similarity to ChEMBL training pools across all 4 targets from the full screening dataset
    comp_mean_nn_pre = df_screen_t6.groupby("inchikey_connectivity")["nn_similarity"].mean()
    df_pre_struct = pd.DataFrame({
        "flat_inchikey": list(lit_map.keys()),
        "evidence_status": list(lit_map.values()),
        "nn_similarity": [comp_mean_nn_pre[c] for c in lit_map.keys()]
    })
    t_pre_struct = run_tests(df_pre_struct, "nn_similarity", "evidence_status")
    t_pre_struct["specification"] = "3. Pre-Cutoff Unique Structures (Unconditioned Baseline)"
    t_pre_struct["selection_condition"] = "Independent of cutoff; mean NN across 4 targets"
    t_pre_struct["total_N"] = len(df_pre_struct)

    # 4. Pre-cutoff on all 1,276 compound-target pairs (319 cpds x 4 targets)
    df_lit_screen = df_screen_t6[df_screen_t6["inchikey_connectivity"].isin(lit_map)].copy()
    df_lit_screen["evidence_status"] = df_lit_screen["inchikey_connectivity"].map(lit_map)
    t_pre_all_ct = run_tests(df_lit_screen, "nn_similarity", "evidence_status")
    t_pre_all_ct["specification"] = "4. Pre-Cutoff Compound-Target Pairs (All 4 Targets)"
    t_pre_all_ct["selection_condition"] = "319 structures evaluated across all 4 targets (68% inactive)"
    t_pre_all_ct["total_N"] = len(df_lit_screen)

    # 5. Pre-cutoff on audited compound-target pairs (N=340)
    ct_lit_map = df_stage8.drop_duplicates(subset=["flat_inchikey", "target"]).set_index(["flat_inchikey", "target"])["evidence_status"].to_dict()
    df_screen_t6["ct_key"] = list(zip(df_screen_t6["inchikey_connectivity"], df_screen_t6["target"]))
    df_audited_ct = df_screen_t6[df_screen_t6["ct_key"].isin(ct_lit_map)].copy()
    df_audited_ct["evidence_status"] = df_audited_ct["ct_key"].map(ct_lit_map)
    t_pre_audited_ct = run_tests(df_audited_ct, "nn_similarity", "evidence_status")
    t_pre_audited_ct["specification"] = "5. Pre-Cutoff Audited Target Pairs (Prioritized Target)"
    t_pre_audited_ct["selection_condition"] = "Specific target where candidate was prioritized"
    t_pre_audited_ct["total_N"] = len(df_audited_ct)

    summary_rows = [t_post_link, t_post_struct, t_pre_struct, t_pre_all_ct, t_pre_audited_ct]
    df_summary = pd.DataFrame(summary_rows)
    cols_order = [
        "specification", "selection_condition", "total_N", "n_level_a", "n_level_e",
        "median_level_a", "median_level_e", "mannwhitney_u", "mannwhitney_p", "rank_biserial_r",
        "kruskal_h", "kruskal_p"
    ]
    df_summary = df_summary[cols_order]
    df_summary.to_csv(OUTPUT_DIR / "pre_vs_post_cutoff_evidence_tests.csv", index=False)
    print(f"Saved hypothesis testing summary to {OUTPUT_DIR / 'pre_vs_post_cutoff_evidence_tests.csv'}")

    # Descriptive statistics per group for Pre-Cutoff Unique Structures
    desc_rows = []
    for st in STATUS_ORDER:
        v_pre = df_pre_struct[df_pre_struct["evidence_status"] == st]["nn_similarity"].values
        res_pre = compute_descriptive_stats(v_pre)
        res_pre["specification"] = "Pre_Cutoff_Structures_N319"
        res_pre["evidence_status"] = st
        desc_rows.append(res_pre)

        v_post = df_post_struct[df_post_struct["evidence_status"] == st]["nn_similarity"].values
        res_post = compute_descriptive_stats(v_post)
        res_post["specification"] = "Post_Cutoff_Structures_N319"
        res_post["evidence_status"] = st
        desc_rows.append(res_post)

    df_desc = pd.DataFrame(desc_rows)
    df_desc = df_desc[["specification", "evidence_status", "N", "mean", "std", "median", "IQR", "min", "max", "Q1", "Q3"]]
    df_desc.to_csv(OUTPUT_DIR / "pre_vs_post_cutoff_descriptive_stats.csv", index=False)
    print(f"Saved descriptive statistics to {OUTPUT_DIR / 'pre_vs_post_cutoff_descriptive_stats.csv'}\n")

    print("=" * 80)
    print("HYPOTHESIS TESTING SUMMARY (PRE-CUTOFF VS POST-CUTOFF)")
    print("=" * 80)
    print(df_summary[["specification", "total_N", "median_level_a", "median_level_e", "mannwhitney_p", "rank_biserial_r", "kruskal_p"]].to_string(index=False))


if __name__ == "__main__":
    main()
