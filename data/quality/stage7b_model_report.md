# Stage 7B Dry Run Report (Target: COX1)
**Authority:** `docs/thesis_design_note.md` (and logged amendments)  
**Execution Timestamp:** 2026-09-25T17:58:54.444003+00:00 UTC  
**Master MPBD SHA-256 (Start & End):** `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` / `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` (**VERIFIED / UNCHANGED**)  
**Frozen Config SHA-256:** `9828C13AC8D7CB5C531F211BAEF5110ABFCE33644D714040F7DD8AAF6BAEBFF8`  

---

## 1. Executive Summary

- **Models Evaluated:** Strictly two model families: RandomForestClassifier (fixed 4-point grid: `n_estimators` in {300, 600}, `max_features` in {'sqrt', 0.1}, `class_weight='balanced'`, seed 42) and a 1-Nearest-Neighbour Tanimoto baseline. No other model family was trained.
- **Scaffold Split:** Bemis-Murcko scaffold grouped cross-validation (acyclic molecules grouped into `'acyclic'`). Grid point selected by mean validation AUPRC.
- **Pre-Evaluation Freeze:** Model architectures, chosen hyperparameters, probability cutoffs, training content hashes, and environment package versions were frozen and committed to `stage7b_config_frozen.json` before evaluating any external flora labels.
- **External Set Governance:** External flora molecules were filtered to those with $\ge 1$ HIGH-tier link in `plant_compound_links_confidence.csv`. COX-1 and COX-2 external evaluations are reported purely descriptively (Spearman rank correlation; no AUROC/AUPRC claimed). XO and MAO-A serve as the main quantitative external evaluations (AUROC, AUPRC, and 1,000-resample bootstrap 95% CIs).
- **Reference Compound Exclusions:** Run (a) executed as-is (N=31, 4 actives). Run (b) executed excluding reference compounds (N=29, 2 actives: Suprofen and Trolox excluded).

---

## 2. Internal Cross-Validation Performance (ChEMBL Training Pool)

| Target | Threshold | Training N (Act/Inact) | Best RF Grid Point | Mean Val AUROC | Mean Val AUPRC | Mean Val Brier | 1-NN Val AUROC | 1-NN Val AUPRC | 1-NN Val Brier | ChEMBL NP N | ChEMBL NP AUROC | ChEMBL NP AUPRC | Opt Cutoff (Max F1) | Opt F1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **COX-1 (PTGS1)** | T=6 | 1458 (325/1133) | `n_est=300, max_feat=sqrt` | **0.6592** | **0.3878** | 0.1786 | 0.6197 | 0.2998 | 0.2654 | 94 (23 act) | 0.7722 | 0.6273 | `0.34` | 0.4252 |

> **Note on Natural Product Flag:** The `natural_product = 1` flag in ChEMBL is coarse and utilized strictly to stratify the ChEMBL internal evaluation across natural vs synthetic small molecules. It is not used as evidence about Bangladesh flora compounds.

### Per-Fold Internal Validation Breakdown

| Target | Threshold | Fold 1 AUROC / AUPRC | Fold 2 AUROC / AUPRC | Fold 3 AUROC / AUPRC | Fold 4 AUROC / AUPRC | Fold 5 AUROC / AUPRC | Mean AUROC | Mean AUPRC |
|---|---|---|---|---|---|---|---|---|
| **COX-1 (PTGS1)** | T=6 | 0.665 / 0.354 | 0.654 / 0.421 | N/A (dry run) | N/A (dry run) | N/A (dry run) | **0.6592** | **0.3878** |

### Calibration Tables (10 Bins, Out-of-Fold Validation Predictions)

#### Calibration: `COX1_T6`

| Probability Bin | Bin Range | Sample Count | Positives | Mean Predicted Probability | Empirical Positive Rate |
|---|---|---|---|---|---|
| [0.0, 0.1) | [0.0, 0.1] | 126 | 18 | 0.0607 | 0.1429 |
| [0.1, 0.2) | [0.1, 0.2] | 300 | 35 | 0.1540 | 0.1167 |
| [0.2, 0.3) | [0.2, 0.3] | 340 | 62 | 0.2437 | 0.1824 |
| [0.3, 0.4) | [0.3, 0.4] | 269 | 59 | 0.3518 | 0.2193 |
| [0.4, 0.5) | [0.4, 0.5] | 190 | 54 | 0.4361 | 0.2842 |
| [0.5, 0.6) | [0.5, 0.6] | 100 | 31 | 0.5456 | 0.3100 |
| [0.6, 0.7) | [0.6, 0.7] | 48 | 22 | 0.6521 | 0.4583 |
| [0.7, 0.8) | [0.7, 0.8] | 55 | 25 | 0.7470 | 0.4545 |
| [0.8, 0.9) | [0.8, 0.9] | 21 | 12 | 0.8300 | 0.5714 |
| [0.9, 1.0] | [0.9, 1.0] | 9 | 7 | 0.9352 | 0.7778 |

---

## 3. External Flora Evaluation (One-Time Touch Post-Freeze)

### Summary of External Sets & Performance

| Target & Run | Threshold | Flora Tested (Act/Inact) | Evaluation Protocol | External AUROC [95% CI] | External AUPRC [95% CI] | Spearman Rank rho (p-value) | In-Domain (NN >= 0.4) N (Act) | In-Domain Perf | Out-of-Domain (NN < 0.4) N (Act) | Out-of-Domain Perf |
|---|---|---|---|---|---|---|---|---|---|---|
| **COX-1 Run (a)** [As-Is] | T=6 | 31 (4/27) | Descriptive (Spearman Rank) | Descriptive only (no claim) N/A | Descriptive only (no claim) N/A | -0.0686 (7.14e-01) | 19 (3) | -0.2817 (p=0.243) | 12 (1) | +0.2028 (p=0.527) |
| **COX-1 Run (b)** [Excl Ref] | T=6 | 29 (2/27) | Descriptive (Spearman Rank) | Descriptive only (no claim) N/A | Descriptive only (no claim) N/A | -0.1912 (3.20e-01) | 18 (2) | -0.4801 (p=0.044) | 11 (0) | +0.4364 (p=0.180) |

> **Governance Protocol Verification & Delta Report:**
> - **Run (a) (As-Is):** Evaluated against all 31 non-conflict flora layers with $\ge 1$ HIGH-tier link.
> - **Run (b) (Excluding Reference Compounds):** Evaluated excluding 2 pharmacological reference standards (`is_reference_compound = 1` in `data/processed/modeling/external_verification_sheet.csv`):
>   1. `MDKGKXOCJGEUJW` (Suprofen): Approved NSAID reference control (assay: human whole blood, IC50 = 560 nM, pChEMBL = 6.25).
>   2. `GLEVLJDDWXEYCO` (Trolox): Synthetic antioxidant reference standard (assay: IC50 = 130 nM, pChEMBL = 6.89).
> - **Run Delta ($\Delta$):** Spearman $\rho$ worsened from -0.0686 to -0.1912 across all compounds, and in-domain $\rho$ worsened from -0.2817 to -0.4801 ($p=0.0437$) because Suprofen was the only active compound correctly predicted with high probability ($0.8367$). The two remaining true actives are natural polyphenols (Moracin M, prob=0.1467; Pterostilbene, prob=0.0900).

### COX Targets Detailed Predictions vs Measured Potency

#### Target: `COX1_T6` (All External Molecules Tested)

| Connectivity Layer | Measured Median pChEMBL | True Active (T) | Predicted Probability | NN Tanimoto to Training Pool | Domain Status (>= 0.4) |
|---|---|---|---|---|---|
| `DTOSIQBPPRVQHS` | 5.40 | 0 | 0.2167 | 0.6471 | IN-DOMAIN |
| `FAKRSMQSSFJEIM` | 4.77 | 0 | 0.4100 | 0.2182 | OUT-OF-DOMAIN |
| `GLEVLJDDWXEYCO` | 6.89 | 1 | 0.3133 | 0.1897 | OUT-OF-DOMAIN |
| `ILEDWLMCKZNDJK` | 4.24 | 0 | 0.2433 | 0.3947 | OUT-OF-DOMAIN |
| `ILRCGYURZSFMEG` | 4.14 | 0 | 0.3167 | 0.3676 | OUT-OF-DOMAIN |
| `LHPRYOJTASOZGJ` | 6.30 | 1 | 0.1467 | 0.6000 | IN-DOMAIN |
| `LUKBXSAWLPMMSZ` | 5.96 | 0 | 0.1100 | 0.7083 | IN-DOMAIN |
| `MDKGKXOCJGEUJW` | 6.25 | 1 | 0.8367 | 0.5714 | IN-DOMAIN |
| `OYHQOLUKZRVURQ` | 4.89 | 0 | 0.2600 | 0.5135 | IN-DOMAIN |
| `PANKHBYNKQNAHN` | 4.55 | 0 | 0.4567 | 0.1795 | OUT-OF-DOMAIN |
| `PCMORTLOPMLEFB` | 4.41 | 0 | 0.3933 | 0.5789 | IN-DOMAIN |
| `PDHAOJSHSJQANO` | 5.85 | 0 | 0.2467 | 0.4839 | IN-DOMAIN |
| `PFTAWBLQPZVEMU` | 4.26 | 0 | 0.1367 | 0.6226 | IN-DOMAIN |
| `QBLQLKNOKUHRCH` | 5.23 | 0 | 0.2533 | 0.4583 | IN-DOMAIN |
| `QJVXKWHHAMZTBY` | 4.44 | 0 | 0.3567 | 0.3699 | OUT-OF-DOMAIN |
| `QWCNQXNAFCBLLV` | 4.18 | 0 | 0.3033 | 0.6136 | IN-DOMAIN |
| `RAKJVIPCCGXHHS` | 4.19 | 0 | 0.2833 | 0.5909 | IN-DOMAIN |
| `RECUKUPTGUEGMW` | 5.40 | 0 | 0.4500 | 0.3103 | OUT-OF-DOMAIN |
| `RRAFCDWBNXTKKO` | 4.96 | 0 | 0.4133 | 0.3953 | OUT-OF-DOMAIN |
| `RSYUFYQTACJFML` | 5.01 | 0 | 0.1467 | 0.5849 | IN-DOMAIN |
| `SCCDQYPEOIRVGX` | 5.52 | 0 | 0.3967 | 0.3125 | OUT-OF-DOMAIN |
| `SFLMUHDGSQZDOW` | 4.12 | 0 | 0.4433 | 0.4028 | IN-DOMAIN |
| `SUTUBQHKZRNZRA` | 4.75 | 0 | 0.0800 | 0.5897 | IN-DOMAIN |
| `TZBJGXHYKVUXJN` | 4.10 | 0 | 0.3433 | 0.3478 | OUT-OF-DOMAIN |
| `UWQYBLOHTQWSQD` | 4.21 | 0 | 0.2633 | 0.6610 | IN-DOMAIN |
| `VFLDPWHFBUODDF` | 4.76 | 0 | 0.3200 | 0.6000 | IN-DOMAIN |
| `VLEUZFDZJKSGMX` | 6.16 | 1 | 0.0900 | 0.6897 | IN-DOMAIN |
| `XMOCLSLCDHWDHP` | 4.02 | 0 | 0.1700 | 0.4737 | IN-DOMAIN |
| `YKPUWZUDDOIDPM` | 5.62 | 0 | 0.3700 | 0.2969 | OUT-OF-DOMAIN |
| `YNVJOQCPHWKWSO` | 4.30 | 0 | 0.1933 | 0.4524 | IN-DOMAIN |
| `ZSYPIPFQOQGYHH` | 4.85 | 0 | 0.2333 | 0.3864 | OUT-OF-DOMAIN |

---

## 4. Applicability Domain & Flora Molecule Scoring

All 7,315 fingerprintable flora layers were scored with the frozen final models:

| Target | Threshold | Total Flora Scored | Internal Cutoff (Max F1) | Flora Above Cutoff (%) | Flora in Domain (NN >= 0.4) (%) | Flora Tolerant Domain (NN >= 0.3) (%) | Predictions CSV Path |
|---|---|---|---|---|---|---|---|
| **COX-1 (PTGS1)** | T=6 | 7,315 | `0.34` | Report CSV | Report CSV | Report CSV | [`data/processed/modeling/flora_predictions_cox1_T6.csv`](file:///data/processed/modeling/flora_predictions_cox1_T6.csv) |

> **Strict Scope Constraint:** Predictions written to `data/processed/modeling/flora_predictions_*.csv` are stored solely for downstream use. No plant-level enrichment or aggregation has been executed in this stage.

---

## 5. Artifact & Integrity Ledger

- **Master MPBD SHA-256 (Start):** `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7`
- **Master MPBD SHA-256 (End):** `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` (**MATCH**)
- **Frozen Config SHA-256:** `9828C13AC8D7CB5C531F211BAEF5110ABFCE33644D714040F7DD8AAF6BAEBFF8`
- **ChEMBL Database Mode:** Strictly read-only (`mode=ro`). Zero disk writes or schema mutations.
- **Generated Figures:**
  - [`figures/roc_curves.png`](file:///f:/bmppd-thesis/figures/roc_curves.png) (ROC curves per target, 300 dpi)
  - [`figures/pr_curves.png`](file:///f:/bmppd-thesis/figures/pr_curves.png) (PR curves per target, 300 dpi)
  - [`figures/calibration_plots.png`](file:///f:/bmppd-thesis/figures/calibration_plots.png) (10-bin calibration diagrams, 300 dpi)
  - [`figures/cox_external_predicted_vs_measured.png`](file:///f:/bmppd-thesis/figures/cox_external_predicted_vs_measured.png) (Scatter plot of COX predicted probability vs measured pChEMBL, 300 dpi)
  - [`figures/flora_nn_similarity_histograms.png`](file:///f:/bmppd-thesis/figures/flora_nn_similarity_histograms.png) (Flora vs ChEMBL training pool similarity distribution, 300 dpi)
