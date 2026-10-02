#!/usr/bin/env python3
"""
scripts/rerun_structure_level_evidence_tests.py
================================================
Re-runs Section 4.5 statistical analysis (Mann-Whitney U and Kruskal-Wallis tests)
comparing nearest-neighbour (NN) Tanimoto similarity to the ChEMBL training pool
across literature-evidence tiers at both:
  1. The original LINK level (N=1,167 plant-compound-target links)
  2. The UNIQUE MOLECULAR STRUCTURE level (N=319 unique connectivity layers)
  3. The UNIQUE COMPOUND-TARGET level (N=340 unique pairs)

Outputs:
  - data/quality/section4_5_link_vs_structure_statistics.csv
  - data/quality/section4_5_hypothesis_tests_comparison.csv
  - data/quality/section4_5_structure_tier_assignments.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

REPO_ROOT = Path(__file__).resolve().parent.parent
INPUT_CSV = REPO_ROOT / "data/processed/modeling/stage8_integrated_candidate_evidence.csv"
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


def compute_descriptive_stats(series: pd.Series) -> dict:
    vals = series.dropna().values
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
    groups = [df[df[group_col] == st][metric_col].values for st in STATUS_ORDER]
    kw = stats.kruskal(*groups)

    vals_a = df[df[group_col] == "LEVEL_A_EXACT_TARGET"][metric_col].values
    vals_e = df[df[group_col] == "NO_RELEVANT_REPORT_FOUND"][metric_col].values

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
    }


def main():
    print("=" * 80)
    print("SECTION 4.5: EVIDENCE TIER VS NN SIMILARITY (LINK VS STRUCTURE DEDUPLICATION)")
    print("=" * 80)

    df_links = pd.read_csv(INPUT_CSV)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loaded {len(df_links):,} candidate links from {INPUT_CSV}")
    print(f"Unique 14-char connectivity structures: {df_links['flat_inchikey'].nunique():,}")
    print(f"Unique full InChIKeys: {df_links['full_inchikey'].nunique():,}")
    print(f"Unique compound-target pairs: {df_links.groupby(['flat_inchikey', 'target']).ngroups:,}")

    # -------------------------------------------------------------------------
    # 1. Structure-level aggregation (Deterministic Highest-Evidence Rule)
    # -------------------------------------------------------------------------
    # Rule: assign each structure the highest evidence tier among its candidate links
    struct_records = []
    for c, grp in df_links.groupby("flat_inchikey"):
        best_status = max(grp["evidence_status"], key=lambda x: TIER_RANK[x])
        tiers_present = sorted(list(grp["evidence_status"].unique()), key=lambda x: -TIER_RANK[x])
        is_mixed = len(tiers_present) > 1

        struct_records.append({
            "flat_inchikey": c,
            "full_inchikey": grp["full_inchikey"].iloc[0],
            "compound_name": grp["compound"].iloc[0],
            "n_links": len(grp),
            "targets": "|".join(sorted(grp["target"].unique())),
            "evidence_status_highest": best_status,
            "evidence_status_mixed": "MIXED" if is_mixed else best_status,
            "tiers_observed": "|".join(tiers_present),
            "nn_similarity_mean": float(grp["nearest_neighbor_similarity"].mean()),
            "nn_similarity_max": float(grp["nearest_neighbor_similarity"].max()),
            "pchembl_pred_mean": float(grp["pchembl_prediction"].mean()),
        })

    df_struct = pd.DataFrame(struct_records)
    df_struct.to_csv(OUTPUT_DIR / "section4_5_structure_tier_assignments.csv", index=False)
    print(f"Saved structure tier assignments to {OUTPUT_DIR / 'section4_5_structure_tier_assignments.csv'}")

    # -------------------------------------------------------------------------
    # 2. Compound-Target level aggregation
    # -------------------------------------------------------------------------
    df_ct = df_links.drop_duplicates(subset=["flat_inchikey", "target"]).copy()

    # -------------------------------------------------------------------------
    # 3. Descriptive Stats Table
    # -------------------------------------------------------------------------
    stat_rows = []

    # A. Link-level
    for st in STATUS_ORDER + ["ALL_CANDIDATES"]:
        sub = df_links if st == "ALL_CANDIDATES" else df_links[df_links["evidence_status"] == st]
        res = compute_descriptive_stats(sub["nearest_neighbor_similarity"])
        res["level"] = "1_Link_Level"
        res["evidence_status"] = st
        stat_rows.append(res)

    # B. Structure-level (Highest Tier, Mean NN)
    for st in STATUS_ORDER + ["ALL_CANDIDATES"]:
        sub = df_struct if st == "ALL_CANDIDATES" else df_struct[df_struct["evidence_status_highest"] == st]
        res = compute_descriptive_stats(sub["nn_similarity_mean"])
        res["level"] = "2_Structure_Level_HighestTier"
        res["evidence_status"] = st
        stat_rows.append(res)

    # C. Compound-Target level
    for st in STATUS_ORDER + ["ALL_CANDIDATES"]:
        sub = df_ct if st == "ALL_CANDIDATES" else df_ct[df_ct["evidence_status"] == st]
        res = compute_descriptive_stats(sub["nearest_neighbor_similarity"])
        res["level"] = "3_Compound_Target_Level"
        res["evidence_status"] = st
        stat_rows.append(res)

    df_stats_all = pd.DataFrame(stat_rows)
    cols_order = ["level", "evidence_status", "N", "mean", "std", "median", "IQR", "min", "max", "Q1", "Q3"]
    df_stats_all = df_stats_all[cols_order]
    df_stats_all.to_csv(OUTPUT_DIR / "section4_5_link_vs_structure_statistics.csv", index=False)
    print(f"Saved descriptive stats to {OUTPUT_DIR / 'section4_5_link_vs_structure_statistics.csv'}")

    # -------------------------------------------------------------------------
    # 4. Hypothesis Tests Comparison
    # -------------------------------------------------------------------------
    tests_summary = []

    # 1. Link level
    t_link = run_tests(df_links, "nearest_neighbor_similarity", "evidence_status")
    t_link["unit_of_analysis"] = "Link Level (Original N=1,167)"
    tests_summary.append(t_link)

    # 2. Structure level (Highest Tier, Mean NN)
    t_struct_mean = run_tests(df_struct, "nn_similarity_mean", "evidence_status_highest")
    t_struct_mean["unit_of_analysis"] = "Structure Level (N=319, Highest Tier, Mean NN)"
    tests_summary.append(t_struct_mean)

    # 3. Structure level (Highest Tier, Max NN)
    t_struct_max = run_tests(df_struct, "nn_similarity_max", "evidence_status_highest")
    t_struct_max["unit_of_analysis"] = "Structure Level (N=319, Highest Tier, Max NN)"
    tests_summary.append(t_struct_max)

    # 4. Structure level (Mixed Category Rule, Mean NN)
    # Run across 4 standard tiers excluding the 3 mixed compounds
    df_mixed_sub = df_struct[df_struct["evidence_status_mixed"] != "MIXED"]
    t_struct_mixed = run_tests(df_mixed_sub, "nn_similarity_mean", "evidence_status_mixed")
    t_struct_mixed["unit_of_analysis"] = "Structure Level (N=316, Mixed Excluded, Mean NN)"
    tests_summary.append(t_struct_mixed)

    # 5. Compound-Target level
    t_ct = run_tests(df_ct, "nearest_neighbor_similarity", "evidence_status")
    t_ct["unit_of_analysis"] = "Compound-Target Level (N=340)"
    tests_summary.append(t_ct)

    df_tests = pd.DataFrame(tests_summary)
    cols_test = ["unit_of_analysis", "kruskal_h", "kruskal_p", "mannwhitney_u", "mannwhitney_p", "rank_biserial_r", "n_level_a", "n_level_e"]
    df_tests = df_tests[cols_test]
    df_tests.to_csv(OUTPUT_DIR / "section4_5_hypothesis_tests_comparison.csv", index=False)
    print(f"Saved hypothesis tests comparison to {OUTPUT_DIR / 'section4_5_hypothesis_tests_comparison.csv'}")

    print("\n" + "=" * 80)
    print("HYPOTHESIS TESTS COMPARISON TABLE")
    print("=" * 80)
    print(df_tests.to_string(index=False))


if __name__ == "__main__":
    main()
