# Stage 7B Dry Run Report (Target: Remaining Targets (COX-2, XO, MAO-A))
**Authority:** `docs/thesis_design_note.md` (and logged amendments)  
**Execution Timestamp:** 2026-09-30T13:39:03.987830+00:00 UTC  
**Master MPBD SHA-256 (Start & End):** `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` / `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` (**VERIFIED / UNCHANGED**)  
**Frozen Config SHA-256:** `ED3C1DC545EE6DEBE364DB93A6AD13E8A13932105F9E12D8533E27F5417B0FDB`  

---

## 1. Executive Summary

- **Models Evaluated:** Strictly two model families: RandomForestClassifier (fixed 4-point grid: `n_estimators` in {300, 600}, `max_features` in {'sqrt', 0.1}, `class_weight='balanced'`, seed 42) and a 1-Nearest-Neighbour Tanimoto baseline. No other model family was trained.
- **Scaffold Split:** Bemis-Murcko scaffold grouped cross-validation (acyclic molecules grouped into `'acyclic'`). Grid point selected by mean validation AUPRC.
- **Pre-Evaluation Freeze:** Model architectures, chosen hyperparameters, probability cutoffs, training content hashes, and environment package versions were frozen and committed to `stage7b_config_frozen.json` before evaluating any external flora labels.
- **External Set Governance:** External flora molecules were filtered to those with $\ge 1$ HIGH-tier link in `plant_compound_links_confidence.csv`. COX-1 and COX-2 external evaluations are reported purely descriptively (Spearman rank correlation; no AUROC/AUPRC claimed). XO and MAO-A serve as the main quantitative external evaluations (AUROC, AUPRC, and 1,000-resample bootstrap 95% CIs).
- **Reference Compound Exclusions:** Run (a) executed as-is. Run (b) status: **COMPLETED**.

---

## 2. Internal Cross-Validation Performance (ChEMBL Training Pool)

| Target | Threshold | Training N (Act/Inact) | Best RF Grid Point | Mean Val AUROC | Mean Val AUPRC | Mean Val Brier | 1-NN Val AUROC | 1-NN Val AUPRC | 1-NN Val Brier | ChEMBL NP N | ChEMBL NP AUROC | ChEMBL NP AUPRC | Opt Cutoff (Max F1) | Opt F1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **COX-2 (PTGS2)** | T=6 | 4122 (2319/1803) | `n_est=600, max_feat=sqrt` | **0.7536** | **0.7815** | 0.2 | 0.6489 | 0.6532 | 0.3467 | 148 (42 act) | 0.7109 | 0.5857 | `0.32` | 0.764 |
| **Xanthine Oxidase (XDH)** | T=6 | 611 (372/239) | `n_est=600, max_feat=sqrt` | **0.8954** | **0.9296** | 0.1326 | 0.7992 | 0.8057 | 0.1899 | 40 (11 act) | 0.5361 | 0.4344 | `0.34` | 0.8648 |
| **MAO-A (CHRFAM7A/MAOA)** | T=6 | 2914 (748/2166) | `n_est=600, max_feat=sqrt` | **0.7653** | **0.5814** | 0.156 | 0.6948 | 0.4186 | 0.2286 | 164 (41 act) | 0.4896 | 0.2995 | `0.38` | 0.5616 |

> **Note on Natural Product Flag:** The `natural_product = 1` flag in ChEMBL is coarse and utilized strictly to stratify the ChEMBL internal evaluation across natural vs synthetic small molecules. It is not used as evidence about Bangladesh flora compounds.

### Per-Fold Internal Validation Breakdown

| Target | Threshold | Fold 1 AUROC / AUPRC | Fold 2 AUROC / AUPRC | Fold 3 AUROC / AUPRC | Fold 4 AUROC / AUPRC | Fold 5 AUROC / AUPRC | Mean AUROC | Mean AUPRC |
|---|---|---|---|---|---|---|---|---|
| **COX-2 (PTGS2)** | T=6 | 0.758 / 0.786 | 0.749 / 0.777 | N/A (dry run) | N/A (dry run) | N/A (dry run) | **0.7536** | **0.7815** |
| **Xanthine Oxidase (XDH)** | T=6 | 0.862 / 0.905 | 0.929 / 0.954 | N/A (dry run) | N/A (dry run) | N/A (dry run) | **0.8954** | **0.9296** |
| **MAO-A (CHRFAM7A/MAOA)** | T=6 | 0.740 / 0.567 | 0.791 / 0.596 | N/A (dry run) | N/A (dry run) | N/A (dry run) | **0.7653** | **0.5814** |

### Calibration Tables (10 Bins, Out-of-Fold Validation Predictions)

#### Calibration: `COX2_T6`

| Probability Bin | Bin Range | Sample Count | Positives | Mean Predicted Probability | Empirical Positive Rate |
|---|---|---|---|---|---|
| [0.0, 0.1) | [0.0, 0.1] | 109 | 4 | 0.0679 | 0.0367 |
| [0.1, 0.2) | [0.1, 0.2] | 305 | 49 | 0.1550 | 0.1607 |
| [0.2, 0.3) | [0.2, 0.3] | 414 | 123 | 0.2515 | 0.2971 |
| [0.3, 0.4) | [0.3, 0.4] | 463 | 217 | 0.3542 | 0.4687 |
| [0.4, 0.5) | [0.4, 0.5] | 625 | 319 | 0.4526 | 0.5104 |
| [0.5, 0.6) | [0.5, 0.6] | 566 | 338 | 0.5501 | 0.5972 |
| [0.6, 0.7) | [0.6, 0.7] | 554 | 371 | 0.6503 | 0.6697 |
| [0.7, 0.8) | [0.7, 0.8] | 569 | 455 | 0.7499 | 0.7996 |
| [0.8, 0.9) | [0.8, 0.9] | 386 | 323 | 0.8452 | 0.8368 |
| [0.9, 1.0] | [0.9, 1.0] | 131 | 120 | 0.9489 | 0.9160 |

#### Calibration: `XO_T6`

| Probability Bin | Bin Range | Sample Count | Positives | Mean Predicted Probability | Empirical Positive Rate |
|---|---|---|---|---|---|
| [0.0, 0.1) | [0.0, 0.1] | 27 | 3 | 0.0493 | 0.1111 |
| [0.1, 0.2) | [0.1, 0.2] | 61 | 5 | 0.1440 | 0.0820 |
| [0.2, 0.3) | [0.2, 0.3] | 85 | 15 | 0.2492 | 0.1765 |
| [0.3, 0.4) | [0.3, 0.4] | 62 | 31 | 0.3486 | 0.5000 |
| [0.4, 0.5) | [0.4, 0.5] | 45 | 21 | 0.4490 | 0.4667 |
| [0.5, 0.6) | [0.5, 0.6] | 43 | 36 | 0.5491 | 0.8372 |
| [0.6, 0.7) | [0.6, 0.7] | 39 | 27 | 0.6419 | 0.6923 |
| [0.7, 0.8) | [0.7, 0.8] | 35 | 29 | 0.7540 | 0.8286 |
| [0.8, 0.9) | [0.8, 0.9] | 57 | 55 | 0.8492 | 0.9649 |
| [0.9, 1.0] | [0.9, 1.0] | 157 | 150 | 0.9581 | 0.9554 |

#### Calibration: `MAOA_T6`

| Probability Bin | Bin Range | Sample Count | Positives | Mean Predicted Probability | Empirical Positive Rate |
|---|---|---|---|---|---|
| [0.0, 0.1) | [0.0, 0.1] | 581 | 53 | 0.0589 | 0.0912 |
| [0.1, 0.2) | [0.1, 0.2] | 587 | 64 | 0.1474 | 0.1090 |
| [0.2, 0.3) | [0.2, 0.3] | 527 | 98 | 0.2464 | 0.1860 |
| [0.3, 0.4) | [0.3, 0.4] | 438 | 112 | 0.3518 | 0.2557 |
| [0.4, 0.5) | [0.4, 0.5] | 314 | 130 | 0.4422 | 0.4140 |
| [0.5, 0.6) | [0.5, 0.6] | 145 | 71 | 0.5434 | 0.4897 |
| [0.6, 0.7) | [0.6, 0.7] | 135 | 75 | 0.6458 | 0.5556 |
| [0.7, 0.8) | [0.7, 0.8] | 64 | 43 | 0.7511 | 0.6719 |
| [0.8, 0.9) | [0.8, 0.9] | 71 | 53 | 0.8510 | 0.7465 |
| [0.9, 1.0] | [0.9, 1.0] | 52 | 49 | 0.9505 | 0.9423 |

---

## 3. External Flora Evaluation (One-Time Touch Post-Freeze)

### Summary of External Sets & Performance

| Target | Threshold | Flora Tested (Act/Inact) | Evaluation Protocol | External AUROC [95% CI] | External AUPRC [95% CI] | Spearman Rank rho (p-value) | In-Domain (NN >= 0.4) N (Act) | In-Domain Perf | Out-of-Domain (NN < 0.4) N (Act) | Out-of-Domain Perf |
|---|---|---|---|---|---|---|---|---|---|---|
| **COX-2 (PTGS2)** | T=6 | 23 (1/22) | Descriptive (Spearman Rank Correlation) | Descriptive only (no claim) N/A | Descriptive only (no claim) N/A | 0.3218 (1.34e-01) | 18 (0) | 0.1426 | 5 (1) | 0.8 |
| **Xanthine Oxidase (XDH)** | T=6 | 26 (5/21) | Quantitative (AUROC, AUPRC, 1000-resample Bootstrap CI) | 0.9619 [0.8636, 1.0000] | 0.81 [0.4167, 1.0000] | N/A (N/A) | 22 (4) | 0.9583 / 0.8042 | 4 (1) | 1.0 / 1.0 |
| **MAO-A (CHRFAM7A/MAOA)** | T=6 | 41 (12/29) | Quantitative (AUROC, AUPRC, 1000-resample Bootstrap CI) | 0.7011 [0.4947, 0.8819] | 0.5917 [0.3369, 0.8207] | N/A (N/A) | 33 (8) | 0.665 / 0.5351 | 8 (4) | 0.75 / 0.7708 |

> **Governance Protocol Verification:**
> - **Run (a) (As-Is):** Fully reported above.
> - **Run (b) (Excluding Reference Compounds):** Status: **Pending user review**. Column `is_reference_compound` in `data/processed/modeling/external_verification_sheet.csv` is currently unpopulated.

### COX Targets Detailed Predictions vs Measured Potency

#### Target: `COX2_T6` (All External Molecules Tested)

| Connectivity Layer | Measured Median pChEMBL | True Active (T) | Predicted Probability | NN Tanimoto to Training Pool | Domain Status (>= 0.4) |
|---|---|---|---|---|---|
| `FAKRSMQSSFJEIM` | 4.92 | 0 | 0.3600 | 0.3667 | OUT-OF-DOMAIN |
| `IBGBGRVKPALMCQ` | 4.71 | 0 | 0.0750 | 0.4167 | IN-DOMAIN |
| `IXELFRRANAOWSF` | 5.47 | 0 | 0.3125 | 0.1273 | OUT-OF-DOMAIN |
| `KTEXNACQROZXEV` | 6.10 | 1 | 0.4150 | 0.3973 | OUT-OF-DOMAIN |
| `KVVSCMOUFCNCGX` | 5.63 | 0 | 0.0123 | 1.0000 | IN-DOMAIN |
| `KZNIFHPLKGYRTM` | 5.10 | 0 | 0.1133 | 0.4167 | IN-DOMAIN |
| `LHPRYOJTASOZGJ` | 4.65 | 0 | 0.1250 | 0.4318 | IN-DOMAIN |
| `MBRLOUHOWLUMFF` | 4.09 | 0 | 0.0533 | 0.6939 | IN-DOMAIN |
| `MDKGKXOCJGEUJW` | 5.56 | 0 | 0.3117 | 0.5714 | IN-DOMAIN |
| `MIJYXULNPSFWEK` | 4.06 | 0 | 0.1567 | 0.7586 | IN-DOMAIN |
| `PCMORTLOPMLEFB` | 4.55 | 0 | 0.0864 | 0.4571 | IN-DOMAIN |
| `PFTAWBLQPZVEMU` | 4.03 | 0 | 0.0750 | 0.4561 | IN-DOMAIN |
| `PREBVFJICNPEKM` | 4.44 | 0 | 0.0550 | 0.6286 | IN-DOMAIN |
| `QBLQLKNOKUHRCH` | 4.33 | 0 | 0.1150 | 0.3750 | OUT-OF-DOMAIN |
| `REFJWTPEDVJJIY` | 4.54 | 0 | 0.1431 | 0.4167 | IN-DOMAIN |
| `RSYUFYQTACJFML` | 4.16 | 0 | 0.0767 | 0.5577 | IN-DOMAIN |
| `RTIXKCRFFJGDFG` | 4.59 | 0 | 0.0667 | 0.5333 | IN-DOMAIN |
| `SUTUBQHKZRNZRA` | 4.70 | 0 | 0.0783 | 0.5897 | IN-DOMAIN |
| `VFLDPWHFBUODDF` | 4.53 | 0 | 0.0350 | 0.8857 | IN-DOMAIN |
| `VLEUZFDZJKSGMX` | 5.65 | 0 | 0.3650 | 0.8889 | IN-DOMAIN |
| `WCGUUGGRBIKTOS` | 4.07 | 0 | 0.3183 | 0.5294 | IN-DOMAIN |
| `YNVJOQCPHWKWSO` | 4.10 | 0 | 0.1170 | 0.3077 | OUT-OF-DOMAIN |
| `YQUVCSBJEUQKSH` | 4.59 | 0 | 0.1650 | 0.4333 | IN-DOMAIN |

---

## 4. Applicability Domain & Flora Molecule Scoring

All 7,315 fingerprintable flora layers were scored with the frozen final models:

| Target | Threshold | Total Flora Scored | Internal Cutoff (Max F1) | Flora Above Cutoff (%) | Flora in Domain (NN >= 0.4) (%) | Flora Tolerant Domain (NN >= 0.3) (%) | Predictions CSV Path |
|---|---|---|---|---|---|---|---|
| **COX-2 (PTGS2)** | T=6 | 7,315 | `0.32` | Report CSV | Report CSV | Report CSV | [`data/processed/modeling/flora_predictions_cox2_T6.csv`](file:///data/processed/modeling/flora_predictions_cox2_T6.csv) |
| **Xanthine Oxidase (XDH)** | T=6 | 7,315 | `0.34` | Report CSV | Report CSV | Report CSV | [`data/processed/modeling/flora_predictions_xo_T6.csv`](file:///data/processed/modeling/flora_predictions_xo_T6.csv) |
| **MAO-A (CHRFAM7A/MAOA)** | T=6 | 7,315 | `0.38` | Report CSV | Report CSV | Report CSV | [`data/processed/modeling/flora_predictions_maoa_T6.csv`](file:///data/processed/modeling/flora_predictions_maoa_T6.csv) |

> **Strict Scope Constraint:** Predictions written to `data/processed/modeling/flora_predictions_*.csv` are stored solely for downstream use. No plant-level enrichment or aggregation has been executed in this stage.

---

## 5. Artifact & Integrity Ledger

- **Master MPBD SHA-256 (Start):** `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7`
- **Master MPBD SHA-256 (End):** `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` (**MATCH**)
- **Frozen Config SHA-256:** `ED3C1DC545EE6DEBE364DB93A6AD13E8A13932105F9E12D8533E27F5417B0FDB`
- **ChEMBL Database Mode:** Strictly read-only (`mode=ro`). Zero disk writes or schema mutations.
- **Generated Figures:**
  - [`figures/remaining_targets_roc_curves.png`](file:///f:/bmppd-thesis/figures/remaining_targets_roc_curves.png) (ROC curves per target, 300 dpi)
  - [`figures/remaining_targets_pr_curves.png`](file:///f:/bmppd-thesis/figures/remaining_targets_pr_curves.png) (PR curves per target, 300 dpi)
  - [`figures/remaining_targets_calibration_plots.png`](file:///f:/bmppd-thesis/figures/remaining_targets_calibration_plots.png) (10-bin calibration diagrams, 300 dpi)
  - [`figures/remaining_targets_cox_external_predicted_vs_measured.png`](file:///f:/bmppd-thesis/figures/remaining_targets_cox_external_predicted_vs_measured.png) (Scatter plot of COX predicted probability vs measured pChEMBL, 300 dpi)
  - [`figures/remaining_targets_flora_nn_similarity_histograms.png`](file:///f:/bmppd-thesis/figures/remaining_targets_flora_nn_similarity_histograms.png) (Flora vs ChEMBL training pool similarity distribution, 300 dpi)
