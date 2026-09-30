# Stage 7B Final Model Training, Internal Validation & External Evaluation Report (Full Non-Dry-Run)
**Authority:** `docs/thesis_design_note.md` (and logged amendments)  
**Execution Timestamp:** 2026-09-30T14:06:41.457725+00:00 UTC  
**Master MPBD SHA-256 (Start & End):** `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` / `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` (**VERIFIED / UNCHANGED**)  
**Frozen Config SHA-256:** `ED5F00E529F0FE4D7CAE877DC53C88A589F5DF06C9EB6AFBB984DC33D9C81AB4`  

---

## 1. Executive Summary

- **Models Evaluated:** Strictly two model families: RandomForestClassifier (fixed 4-point grid: `n_estimators` in {300, 600}, `max_features` in {'sqrt', 0.1}, `class_weight='balanced'`, seed 42) and a 1-Nearest-Neighbour Tanimoto baseline. No other model family was trained.
- **Scaffold Split:** Bemis-Murcko scaffold grouped cross-validation (acyclic molecules grouped into `'acyclic'`). Grid point selected by mean validation AUPRC.
- **Pre-Evaluation Freeze:** Model architectures, chosen hyperparameters, probability cutoffs, training content hashes, and environment package versions were frozen and committed to `stage7b_config_frozen_FULL.json` before evaluating any external flora labels.
- **External Set Governance:** External flora molecules were filtered to those with $\ge 1$ HIGH-tier link in `plant_compound_links_confidence.csv`. COX-1 and COX-2 external evaluations are reported purely descriptively (Spearman rank correlation; no AUROC/AUPRC claimed). XO and MAO-A serve as the main quantitative external evaluations (AUROC, AUPRC, and 1,000-resample bootstrap 95% CIs).
- **Reference Compound Exclusions:** Run (a) executed as-is across all targets. Run (b) sensitivity analysis executed for targets with active reference artifacts: COX-1 (T=6 and T=5, excluding Suprofen and Trolox; N=29) and COX-2 (T=5, excluding Suprofen; N=22). Status: **COMPLETED**.
- **Base-Rate Framing Note on COX-2 ($T=5$):** The internal ChEMBL training pool for COX-2 at $T=5$ has an active base rate of 85.54% (3,598 actives / 4,206 molecules). The uncalibrated naive baseline AUPRC is ~0.855; thus, the observed validation AUPRC of 0.9410 represents an absolute gain of +0.086 (relative lift of $1.10\times$), consistent with its scaffold CV AUROC of 0.7571. Reviewers should interpret the high raw AUPRC primarily as an artifact of extreme class prevalence at $10\,\mu\text{M}$ rather than near-perfect discrimination.

---

## 2. Internal Cross-Validation Performance (ChEMBL Training Pool)

| Target | Threshold | Training N (Act/Inact) | Best RF Grid Point | Mean Val AUROC | Mean Val AUPRC | Mean Val Brier | 1-NN Val AUROC | 1-NN Val AUPRC | 1-NN Val Brier | ChEMBL NP N | ChEMBL NP AUROC | ChEMBL NP AUPRC | Opt Cutoff (Max F1) | Opt F1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **COX-1 (PTGS1)** | T=6 | 1458 (325/1133) | `n_est=600, max_feat=sqrt` | **0.7219** | **0.491** | 0.168 | 0.6517 | 0.3318 | 0.2407 | 94 (23 act) | 0.8099 | 0.6747 | `0.39` | 0.4928 |
| **COX-1 (PTGS1)** | T=5 | 1457 (839/618) | `n_est=600, max_feat=sqrt` | **0.7738** | **0.8134** | 0.1918 | 0.7032 | 0.7062 | 0.2891 | 88 (59 act) | 0.7551 | 0.886 | `0.34` | 0.7786 |
| **COX-2 (PTGS2)** | T=6 | 4122 (2319/1803) | `n_est=300, max_feat=0.1` | **0.7739** | **0.7957** | 0.1934 | 0.6854 | 0.6822 | 0.3112 | 148 (42 act) | 0.6723 | 0.5932 | `0.36` | 0.7755 |
| **COX-2 (PTGS2)** | T=5 | 4206 (3598/608) | `n_est=600, max_feat=sqrt` | **0.7571** | **0.941** | 0.1274 | 0.6532 | 0.8954 | 0.1762 | 152 (114 act) | 0.6391 | 0.8602 | `0.16` | 0.9251 |
| **Xanthine Oxidase (XDH)** | T=6 | 611 (372/239) | `n_est=600, max_feat=sqrt` | **0.9155** | **0.9449** | 0.1232 | 0.7703 | 0.7835 | 0.2206 | 40 (11 act) | 0.4953 | 0.4393 | `0.4` | 0.8686 |
| **Xanthine Oxidase (XDH)** | T=5 | 617 (486/131) | `n_est=600, max_feat=sqrt` | **0.8974** | **0.9716** | 0.1206 | 0.736 | 0.8772 | 0.1687 | 40 (20 act) | 0.51 | 0.5789 | `0.3` | 0.9049 |
| **MAO-A (CHRFAM7A/MAOA)** | T=6 | 2914 (748/2166) | `n_est=600, max_feat=sqrt` | **0.8218** | **0.6664** | 0.1376 | 0.7251 | 0.4577 | 0.2083 | 164 (41 act) | 0.5332 | 0.3142 | `0.41` | 0.6203 |
| **MAO-A (CHRFAM7A/MAOA)** | T=5 | 2922 (1722/1200) | `n_est=600, max_feat=sqrt` | **0.7899** | **0.8382** | 0.1846 | 0.7019 | 0.7151 | 0.2896 | 166 (92 act) | 0.5831 | 0.6541 | `0.38` | 0.7879 |

> **Note on Natural Product Flag:** The `natural_product = 1` flag in ChEMBL is coarse and utilized strictly to stratify the ChEMBL internal evaluation across natural vs synthetic small molecules. It is not used as evidence about Bangladesh flora compounds.

### Per-Fold Internal Validation Breakdown

| Target | Threshold | Fold 1 AUROC / AUPRC | Fold 2 AUROC / AUPRC | Fold 3 AUROC / AUPRC | Fold 4 AUROC / AUPRC | Fold 5 AUROC / AUPRC | Mean AUROC | Mean AUPRC |
|---|---|---|---|---|---|---|---|---|
| **COX-1 (PTGS1)** | T=6 | 0.777 / 0.547 | 0.744 / 0.502 | 0.720 / 0.404 | 0.721 / 0.482 | 0.647 / 0.521 | **0.7219** | **0.491** |
| **COX-1 (PTGS1)** | T=5 | 0.789 / 0.820 | 0.795 / 0.831 | 0.782 / 0.808 | 0.782 / 0.835 | 0.720 / 0.772 | **0.7738** | **0.8134** |
| **COX-2 (PTGS2)** | T=6 | 0.815 / 0.813 | 0.736 / 0.779 | 0.779 / 0.796 | 0.760 / 0.788 | 0.779 / 0.802 | **0.7739** | **0.7957** |
| **COX-2 (PTGS2)** | T=5 | 0.716 / 0.927 | 0.787 / 0.952 | 0.771 / 0.942 | 0.766 / 0.945 | 0.746 / 0.939 | **0.7571** | **0.941** |
| **Xanthine Oxidase (XDH)** | T=6 | 0.884 / 0.936 | 0.915 / 0.947 | 0.931 / 0.943 | 0.942 / 0.960 | 0.906 / 0.937 | **0.9155** | **0.9449** |
| **Xanthine Oxidase (XDH)** | T=5 | 0.880 / 0.969 | 0.948 / 0.986 | 0.949 / 0.986 | 0.889 / 0.968 | 0.822 / 0.949 | **0.8974** | **0.9716** |
| **MAO-A (CHRFAM7A/MAOA)** | T=6 | 0.850 / 0.701 | 0.778 / 0.655 | 0.856 / 0.695 | 0.844 / 0.683 | 0.781 / 0.598 | **0.8218** | **0.6664** |
| **MAO-A (CHRFAM7A/MAOA)** | T=5 | 0.784 / 0.825 | 0.815 / 0.861 | 0.814 / 0.864 | 0.755 / 0.821 | 0.781 / 0.821 | **0.7899** | **0.8382** |

### Calibration Tables (10 Bins, Out-of-Fold Validation Predictions)

#### Calibration: `COX1_T6`

| Probability Bin | Bin Range | Sample Count | Positives | Mean Predicted Probability | Empirical Positive Rate |
|---|---|---|---|---|---|
| [0.0, 0.1) | [0.0, 0.1] | 150 | 13 | 0.0604 | 0.0867 |
| [0.1, 0.2) | [0.1, 0.2] | 276 | 30 | 0.1517 | 0.1087 |
| [0.2, 0.3) | [0.2, 0.3] | 294 | 38 | 0.2505 | 0.1293 |
| [0.3, 0.4) | [0.3, 0.4] | 250 | 47 | 0.3517 | 0.1880 |
| [0.4, 0.5) | [0.4, 0.5] | 200 | 61 | 0.4485 | 0.3050 |
| [0.5, 0.6) | [0.5, 0.6] | 112 | 41 | 0.5478 | 0.3661 |
| [0.6, 0.7) | [0.6, 0.7] | 78 | 32 | 0.6426 | 0.4103 |
| [0.7, 0.8) | [0.7, 0.8] | 51 | 26 | 0.7489 | 0.5098 |
| [0.8, 0.9) | [0.8, 0.9] | 27 | 20 | 0.8406 | 0.7407 |
| [0.9, 1.0] | [0.9, 1.0] | 20 | 17 | 0.9288 | 0.8500 |

#### Calibration: `COX1_T5`

| Probability Bin | Bin Range | Sample Count | Positives | Mean Predicted Probability | Empirical Positive Rate |
|---|---|---|---|---|---|
| [0.0, 0.1) | [0.0, 0.1] | 14 | 1 | 0.0705 | 0.0714 |
| [0.1, 0.2) | [0.1, 0.2] | 93 | 9 | 0.1562 | 0.0968 |
| [0.2, 0.3) | [0.2, 0.3] | 122 | 29 | 0.2499 | 0.2377 |
| [0.3, 0.4) | [0.3, 0.4] | 156 | 66 | 0.3569 | 0.4231 |
| [0.4, 0.5) | [0.4, 0.5] | 196 | 86 | 0.4525 | 0.4388 |
| [0.5, 0.6) | [0.5, 0.6] | 220 | 135 | 0.5517 | 0.6136 |
| [0.6, 0.7) | [0.6, 0.7] | 238 | 170 | 0.6507 | 0.7143 |
| [0.7, 0.8) | [0.7, 0.8] | 199 | 146 | 0.7503 | 0.7337 |
| [0.8, 0.9) | [0.8, 0.9] | 139 | 122 | 0.8489 | 0.8777 |
| [0.9, 1.0] | [0.9, 1.0] | 80 | 75 | 0.9454 | 0.9375 |

#### Calibration: `COX2_T6`

| Probability Bin | Bin Range | Sample Count | Positives | Mean Predicted Probability | Empirical Positive Rate |
|---|---|---|---|---|---|
| [0.0, 0.1) | [0.0, 0.1] | 202 | 20 | 0.0631 | 0.0990 |
| [0.1, 0.2) | [0.1, 0.2] | 362 | 53 | 0.1507 | 0.1464 |
| [0.2, 0.3) | [0.2, 0.3] | 449 | 149 | 0.2498 | 0.3318 |
| [0.3, 0.4) | [0.3, 0.4] | 428 | 174 | 0.3493 | 0.4065 |
| [0.4, 0.5) | [0.4, 0.5] | 474 | 274 | 0.4515 | 0.5781 |
| [0.5, 0.6) | [0.5, 0.6] | 485 | 299 | 0.5466 | 0.6165 |
| [0.6, 0.7) | [0.6, 0.7] | 443 | 310 | 0.6516 | 0.6998 |
| [0.7, 0.8) | [0.7, 0.8] | 442 | 338 | 0.7500 | 0.7647 |
| [0.8, 0.9) | [0.8, 0.9] | 497 | 400 | 0.8476 | 0.8048 |
| [0.9, 1.0] | [0.9, 1.0] | 340 | 302 | 0.9402 | 0.8882 |

#### Calibration: `COX2_T5`

| Probability Bin | Bin Range | Sample Count | Positives | Mean Predicted Probability | Empirical Positive Rate |
|---|---|---|---|---|---|
| [0.0, 0.1) | [0.0, 0.1] | 21 | 7 | 0.0601 | 0.3333 |
| [0.1, 0.2) | [0.1, 0.2] | 59 | 20 | 0.1486 | 0.3390 |
| [0.2, 0.3) | [0.2, 0.3] | 109 | 61 | 0.2622 | 0.5596 |
| [0.3, 0.4) | [0.3, 0.4] | 158 | 91 | 0.3508 | 0.5759 |
| [0.4, 0.5) | [0.4, 0.5] | 270 | 178 | 0.4504 | 0.6593 |
| [0.5, 0.6) | [0.5, 0.6] | 347 | 285 | 0.5543 | 0.8213 |
| [0.6, 0.7) | [0.6, 0.7] | 418 | 350 | 0.6541 | 0.8373 |
| [0.7, 0.8) | [0.7, 0.8] | 633 | 548 | 0.7548 | 0.8657 |
| [0.8, 0.9) | [0.8, 0.9] | 1172 | 1077 | 0.8530 | 0.9189 |
| [0.9, 1.0] | [0.9, 1.0] | 1019 | 981 | 0.9444 | 0.9627 |

#### Calibration: `XO_T6`

| Probability Bin | Bin Range | Sample Count | Positives | Mean Predicted Probability | Empirical Positive Rate |
|---|---|---|---|---|---|
| [0.0, 0.1) | [0.0, 0.1] | 58 | 1 | 0.0578 | 0.0172 |
| [0.1, 0.2) | [0.1, 0.2] | 66 | 11 | 0.1460 | 0.1667 |
| [0.2, 0.3) | [0.2, 0.3] | 70 | 20 | 0.2501 | 0.2857 |
| [0.3, 0.4) | [0.3, 0.4] | 43 | 16 | 0.3490 | 0.3721 |
| [0.4, 0.5) | [0.4, 0.5] | 39 | 23 | 0.4512 | 0.5897 |
| [0.5, 0.6) | [0.5, 0.6] | 42 | 31 | 0.5428 | 0.7381 |
| [0.6, 0.7) | [0.6, 0.7] | 33 | 28 | 0.6497 | 0.8485 |
| [0.7, 0.8) | [0.7, 0.8] | 49 | 38 | 0.7469 | 0.7755 |
| [0.8, 0.9) | [0.8, 0.9] | 72 | 67 | 0.8529 | 0.9306 |
| [0.9, 1.0] | [0.9, 1.0] | 139 | 137 | 0.9611 | 0.9856 |

#### Calibration: `XO_T5`

| Probability Bin | Bin Range | Sample Count | Positives | Mean Predicted Probability | Empirical Positive Rate |
|---|---|---|---|---|---|
| [0.0, 0.1) | [0.0, 0.1] | 19 | 4 | 0.0380 | 0.2105 |
| [0.1, 0.2) | [0.1, 0.2] | 19 | 6 | 0.1502 | 0.3158 |
| [0.2, 0.3) | [0.2, 0.3] | 35 | 10 | 0.2584 | 0.2857 |
| [0.3, 0.4) | [0.3, 0.4] | 54 | 30 | 0.3517 | 0.5556 |
| [0.4, 0.5) | [0.4, 0.5] | 52 | 28 | 0.4511 | 0.5385 |
| [0.5, 0.6) | [0.5, 0.6] | 45 | 29 | 0.5484 | 0.6444 |
| [0.6, 0.7) | [0.6, 0.7] | 43 | 37 | 0.6583 | 0.8605 |
| [0.7, 0.8) | [0.7, 0.8] | 99 | 95 | 0.7487 | 0.9596 |
| [0.8, 0.9) | [0.8, 0.9] | 50 | 47 | 0.8512 | 0.9400 |
| [0.9, 1.0] | [0.9, 1.0] | 201 | 200 | 0.9673 | 0.9950 |

#### Calibration: `MAOA_T6`

| Probability Bin | Bin Range | Sample Count | Positives | Mean Predicted Probability | Empirical Positive Rate |
|---|---|---|---|---|---|
| [0.0, 0.1) | [0.0, 0.1] | 611 | 34 | 0.0512 | 0.0556 |
| [0.1, 0.2) | [0.1, 0.2] | 548 | 48 | 0.1469 | 0.0876 |
| [0.2, 0.3) | [0.2, 0.3] | 573 | 108 | 0.2475 | 0.1885 |
| [0.3, 0.4) | [0.3, 0.4] | 368 | 76 | 0.3461 | 0.2065 |
| [0.4, 0.5) | [0.4, 0.5] | 251 | 91 | 0.4461 | 0.3625 |
| [0.5, 0.6) | [0.5, 0.6] | 164 | 77 | 0.5446 | 0.4695 |
| [0.6, 0.7) | [0.6, 0.7] | 95 | 62 | 0.6446 | 0.6526 |
| [0.7, 0.8) | [0.7, 0.8] | 88 | 70 | 0.7486 | 0.7955 |
| [0.8, 0.9) | [0.8, 0.9] | 96 | 73 | 0.8514 | 0.7604 |
| [0.9, 1.0] | [0.9, 1.0] | 120 | 109 | 0.9459 | 0.9083 |

#### Calibration: `MAOA_T5`

| Probability Bin | Bin Range | Sample Count | Positives | Mean Predicted Probability | Empirical Positive Rate |
|---|---|---|---|---|---|
| [0.0, 0.1) | [0.0, 0.1] | 83 | 5 | 0.0641 | 0.0602 |
| [0.1, 0.2) | [0.1, 0.2] | 244 | 51 | 0.1513 | 0.2090 |
| [0.2, 0.3) | [0.2, 0.3] | 237 | 70 | 0.2497 | 0.2954 |
| [0.3, 0.4) | [0.3, 0.4] | 275 | 105 | 0.3529 | 0.3818 |
| [0.4, 0.5) | [0.4, 0.5] | 386 | 203 | 0.4506 | 0.5259 |
| [0.5, 0.6) | [0.5, 0.6] | 415 | 226 | 0.5507 | 0.5446 |
| [0.6, 0.7) | [0.6, 0.7] | 383 | 282 | 0.6493 | 0.7363 |
| [0.7, 0.8) | [0.7, 0.8] | 319 | 247 | 0.7547 | 0.7743 |
| [0.8, 0.9) | [0.8, 0.9] | 323 | 294 | 0.8501 | 0.9102 |
| [0.9, 1.0] | [0.9, 1.0] | 257 | 239 | 0.9409 | 0.9300 |

---

## 3. External Flora Evaluation (One-Time Touch Post-Freeze)

### Summary of External Sets & Performance

| Target | Threshold | Flora Tested (Act/Inact) | Evaluation Protocol | External AUROC [95% CI] | External AUPRC [95% CI] | Spearman Rank rho (p-value) | In-Domain (NN >= 0.4) N (Act) | In-Domain Perf | Out-of-Domain (NN < 0.4) N (Act) | Out-of-Domain Perf |
|---|---|---|---|---|---|---|---|---|---|---|
| **COX-1 (PTGS1) [Run a - As-Is]** | T=6 | 31 (4/27) | Descriptive (Spearman Rank Correlation) | Descriptive only (no claim) N/A | Descriptive only (no claim) N/A | -0.0488 (7.94e-01) | 19 (3) | -0.2799 | 12 (1) | 0.3147 |
| **COX-1 (PTGS1) [Run b - Curated]** | T=6 | 29 (2/27) | Descriptive (Spearman Rank Correlation) | Descriptive only (no claim) N/A | Descriptive only (no claim) N/A | -0.1799 (3.50e-01) | 18 (2) | -0.476 | 11 (0) | 0.4909 |
| **COX-1 (PTGS1) [Run a - As-Is]** | T=5 | 31 (12/19) | Descriptive (Spearman Rank Correlation) | Descriptive only (no claim) N/A | Descriptive only (no claim) N/A | -0.1008 (5.89e-01) | 19 (8) | -0.1772 | 12 (4) | 0.021 |
| **COX-1 (PTGS1) [Run b - Curated]** | T=5 | 29 (10/19) | Descriptive (Spearman Rank Correlation) | Descriptive only (no claim) N/A | Descriptive only (no claim) N/A | -0.285 (1.34e-01) | 18 (7) | -0.3684 | 11 (3) | -0.0818 |
| **COX-2 (PTGS2)** | T=6 | 23 (1/22) | Descriptive (Spearman Rank Correlation) | Descriptive only (no claim) N/A | Descriptive only (no claim) N/A | 0.2765 (2.02e-01) | 18 (0) | 0.0444 | 5 (1) | 0.6 |
| **COX-2 (PTGS2) [Run a - As-Is]** | T=5 | 23 (6/17) | Descriptive (Spearman Rank Correlation) | Descriptive only (no claim) N/A | Descriptive only (no claim) N/A | 0.2926 (1.76e-01) | 18 (4) | 0.1797 | 5 (2) | 0.8 |
| **COX-2 (PTGS2) [Run b - Curated]** | T=5 | 22 (5/17) | Descriptive (Spearman Rank Correlation) | Descriptive only (no claim) N/A | Descriptive only (no claim) N/A | 0.248 (2.66e-01) | 17 (3) | 0.1091 | 5 (2) | 0.8 |
| **Xanthine Oxidase (XDH)** | T=6 | 26 (5/21) | Quantitative (AUROC, AUPRC, 1000-resample Bootstrap CI) | 0.9619 [0.8636, 1.0000] | 0.81 [0.4167, 1.0000] | N/A (N/A) | 22 (4) | 0.9583 / 0.8042 | 4 (1) | 1.0 / 1.0 |
| **Xanthine Oxidase (XDH)** | T=5 | 26 (15/11) | Quantitative (AUROC, AUPRC, 1000-resample Bootstrap CI) | 0.7515 [0.5475, 0.9273] | 0.8226 [0.6398, 0.9619] | N/A (N/A) | 22 (13) | 0.7949 / 0.8546 | 4 (2) | 0.5 / 0.5833 |
| **MAO-A (CHRFAM7A/MAOA)** | T=6 | 41 (12/29) | Quantitative (AUROC, AUPRC, 1000-resample Bootstrap CI) | 0.7011 [0.4947, 0.8819] | 0.5917 [0.3369, 0.8207] | N/A (N/A) | 33 (8) | 0.665 / 0.5351 | 8 (4) | 0.75 / 0.7708 |
| **MAO-A (CHRFAM7A/MAOA)** | T=5 | 41 (26/15) | Quantitative (AUROC, AUPRC, 1000-resample Bootstrap CI) | 0.4308 [0.2357, 0.6200] | 0.6522 [0.4636, 0.8238] | N/A (N/A) | 33 (19) | 0.3797 / 0.582 | 8 (7) | 0.7143 / 0.9617 |

> **Governance Protocol Verification:**
> - **Run (a) (As-Is):** Fully reported above for all targets.
> - **Run (b) (Excluding Reference Artifacts):** Evaluated for targets with active reference artifacts:
>   - **COX-1 (T=6 and T=5):** Excluded confirmed artifacts Suprofen (`MDKGKXOCJGEUJW`, synthetic NSAID / NIST spectral matching artifact) and Trolox (`GLEVLJDDWXEYCO`, synthetic antioxidant assay standard). Evaluation set: N=29 (T=6: 2 act/27 inact; T=5: 10 act/19 inact).
>   - **COX-2 (T=5):** Excluded confirmed artifact Suprofen (`MDKGKXOCJGEUJW`, median pChEMBL = 5.56 >= 5.0). Evaluation set: N=22 (5 authentic act/17 inact).
>   - **COX-2 (T=6):** No active reference artifacts present (Suprofen inactive at median pChEMBL 5.56 < 6.0; Trolox excluded a priori via Section 5 assay conflict rule).

### COX Targets Detailed Predictions vs Measured Potency

#### Target: `COX1_T6` (All External Molecules Tested)

| Connectivity Layer | Measured Median pChEMBL | True Active (T) | Predicted Probability | NN Tanimoto to Training Pool | Domain Status (>= 0.4) | Reference Artifact? |
|---|---|---|---|---|---|---|
| `DTOSIQBPPRVQHS` | 5.40 | 0 | 0.2350 | 0.6471 | IN-DOMAIN | No (Authentic) |
| `FAKRSMQSSFJEIM` | 4.77 | 0 | 0.4267 | 0.2182 | OUT-OF-DOMAIN | No (Authentic) |
| `GLEVLJDDWXEYCO` | 6.89 | 1 | 0.3233 | 0.1897 | OUT-OF-DOMAIN | **YES (EXCLUDED in Run b)** |
| `ILEDWLMCKZNDJK` | 4.24 | 0 | 0.2433 | 0.3947 | OUT-OF-DOMAIN | No (Authentic) |
| `ILRCGYURZSFMEG` | 4.14 | 0 | 0.2950 | 0.3676 | OUT-OF-DOMAIN | No (Authentic) |
| `LHPRYOJTASOZGJ` | 6.30 | 1 | 0.1567 | 0.6000 | IN-DOMAIN | No (Authentic) |
| `LUKBXSAWLPMMSZ` | 5.96 | 0 | 0.1017 | 0.7083 | IN-DOMAIN | No (Authentic) |
| `MDKGKXOCJGEUJW` | 6.25 | 1 | 0.8600 | 0.5714 | IN-DOMAIN | **YES (EXCLUDED in Run b)** |
| `OYHQOLUKZRVURQ` | 4.89 | 0 | 0.2767 | 0.5135 | IN-DOMAIN | No (Authentic) |
| `PANKHBYNKQNAHN` | 4.55 | 0 | 0.4517 | 0.1795 | OUT-OF-DOMAIN | No (Authentic) |
| `PCMORTLOPMLEFB` | 4.41 | 0 | 0.3917 | 0.5789 | IN-DOMAIN | No (Authentic) |
| `PDHAOJSHSJQANO` | 5.85 | 0 | 0.2467 | 0.4839 | IN-DOMAIN | No (Authentic) |
| `PFTAWBLQPZVEMU` | 4.26 | 0 | 0.1567 | 0.6226 | IN-DOMAIN | No (Authentic) |
| `QBLQLKNOKUHRCH` | 5.23 | 0 | 0.2800 | 0.4583 | IN-DOMAIN | No (Authentic) |
| `QJVXKWHHAMZTBY` | 4.44 | 0 | 0.3517 | 0.3699 | OUT-OF-DOMAIN | No (Authentic) |
| `QWCNQXNAFCBLLV` | 4.18 | 0 | 0.2933 | 0.6136 | IN-DOMAIN | No (Authentic) |
| `RAKJVIPCCGXHHS` | 4.19 | 0 | 0.2850 | 0.5909 | IN-DOMAIN | No (Authentic) |
| `RECUKUPTGUEGMW` | 5.40 | 0 | 0.4633 | 0.3103 | OUT-OF-DOMAIN | No (Authentic) |
| `RRAFCDWBNXTKKO` | 4.96 | 0 | 0.4100 | 0.3953 | OUT-OF-DOMAIN | No (Authentic) |
| `RSYUFYQTACJFML` | 5.01 | 0 | 0.1633 | 0.5849 | IN-DOMAIN | No (Authentic) |
| `SCCDQYPEOIRVGX` | 5.52 | 0 | 0.3900 | 0.3125 | OUT-OF-DOMAIN | No (Authentic) |
| `SFLMUHDGSQZDOW` | 4.12 | 0 | 0.4267 | 0.4028 | IN-DOMAIN | No (Authentic) |
| `SUTUBQHKZRNZRA` | 4.75 | 0 | 0.0883 | 0.5897 | IN-DOMAIN | No (Authentic) |
| `TZBJGXHYKVUXJN` | 4.10 | 0 | 0.3283 | 0.3478 | OUT-OF-DOMAIN | No (Authentic) |
| `UWQYBLOHTQWSQD` | 4.21 | 0 | 0.2583 | 0.6610 | IN-DOMAIN | No (Authentic) |
| `VFLDPWHFBUODDF` | 4.76 | 0 | 0.3317 | 0.6000 | IN-DOMAIN | No (Authentic) |
| `VLEUZFDZJKSGMX` | 6.16 | 1 | 0.1050 | 0.6897 | IN-DOMAIN | No (Authentic) |
| `XMOCLSLCDHWDHP` | 4.02 | 0 | 0.2050 | 0.4737 | IN-DOMAIN | No (Authentic) |
| `YKPUWZUDDOIDPM` | 5.62 | 0 | 0.3533 | 0.2969 | OUT-OF-DOMAIN | No (Authentic) |
| `YNVJOQCPHWKWSO` | 4.30 | 0 | 0.1967 | 0.4524 | IN-DOMAIN | No (Authentic) |
| `ZSYPIPFQOQGYHH` | 4.85 | 0 | 0.2467 | 0.3864 | OUT-OF-DOMAIN | No (Authentic) |

#### Target: `COX1_T5` (All External Molecules Tested)

| Connectivity Layer | Measured Median pChEMBL | True Active (T) | Predicted Probability | NN Tanimoto to Training Pool | Domain Status (>= 0.4) | Reference Artifact? |
|---|---|---|---|---|---|---|
| `DTOSIQBPPRVQHS` | 5.40 | 1 | 0.2067 | 0.6471 | IN-DOMAIN | No (Authentic) |
| `FAKRSMQSSFJEIM` | 4.77 | 0 | 0.4629 | 0.2182 | OUT-OF-DOMAIN | No (Authentic) |
| `GLEVLJDDWXEYCO` | 6.89 | 1 | 0.5250 | 0.1864 | OUT-OF-DOMAIN | **YES (EXCLUDED in Run b)** |
| `ILEDWLMCKZNDJK` | 4.24 | 0 | 0.2483 | 0.3947 | OUT-OF-DOMAIN | No (Authentic) |
| `ILRCGYURZSFMEG` | 4.14 | 0 | 0.6179 | 0.3676 | OUT-OF-DOMAIN | No (Authentic) |
| `LHPRYOJTASOZGJ` | 6.30 | 1 | 0.3967 | 0.6000 | IN-DOMAIN | No (Authentic) |
| `LUKBXSAWLPMMSZ` | 5.96 | 1 | 0.1733 | 0.7083 | IN-DOMAIN | No (Authentic) |
| `MDKGKXOCJGEUJW` | 6.25 | 1 | 0.8914 | 0.5714 | IN-DOMAIN | **YES (EXCLUDED in Run b)** |
| `OYHQOLUKZRVURQ` | 4.89 | 0 | 0.2772 | 0.5135 | IN-DOMAIN | No (Authentic) |
| `PANKHBYNKQNAHN` | 4.55 | 0 | 0.4156 | 0.1795 | OUT-OF-DOMAIN | No (Authentic) |
| `PCMORTLOPMLEFB` | 4.41 | 0 | 0.6267 | 0.5789 | IN-DOMAIN | No (Authentic) |
| `PDHAOJSHSJQANO` | 5.85 | 1 | 0.4100 | 0.4839 | IN-DOMAIN | No (Authentic) |
| `PFTAWBLQPZVEMU` | 4.26 | 0 | 0.3683 | 0.6226 | IN-DOMAIN | No (Authentic) |
| `QBLQLKNOKUHRCH` | 5.23 | 1 | 0.3942 | 0.4583 | IN-DOMAIN | No (Authentic) |
| `QJVXKWHHAMZTBY` | 4.44 | 0 | 0.6425 | 0.3699 | OUT-OF-DOMAIN | No (Authentic) |
| `QWCNQXNAFCBLLV` | 4.18 | 0 | 0.3111 | 0.6136 | IN-DOMAIN | No (Authentic) |
| `RAKJVIPCCGXHHS` | 4.19 | 0 | 0.5083 | 0.5909 | IN-DOMAIN | No (Authentic) |
| `RECUKUPTGUEGMW` | 5.40 | 1 | 0.6483 | 0.3103 | OUT-OF-DOMAIN | No (Authentic) |
| `RRAFCDWBNXTKKO` | 4.96 | 0 | 0.4287 | 0.3953 | OUT-OF-DOMAIN | No (Authentic) |
| `RSYUFYQTACJFML` | 5.01 | 1 | 0.4667 | 0.5849 | IN-DOMAIN | No (Authentic) |
| `SCCDQYPEOIRVGX` | 5.52 | 1 | 0.4953 | 0.3125 | OUT-OF-DOMAIN | No (Authentic) |
| `SFLMUHDGSQZDOW` | 4.12 | 0 | 0.7308 | 0.4028 | IN-DOMAIN | No (Authentic) |
| `SUTUBQHKZRNZRA` | 4.75 | 0 | 0.0867 | 0.5897 | IN-DOMAIN | No (Authentic) |
| `TZBJGXHYKVUXJN` | 4.10 | 0 | 0.5000 | 0.3478 | OUT-OF-DOMAIN | No (Authentic) |
| `UWQYBLOHTQWSQD` | 4.21 | 0 | 0.3583 | 0.6610 | IN-DOMAIN | No (Authentic) |
| `VFLDPWHFBUODDF` | 4.76 | 0 | 0.4233 | 0.6000 | IN-DOMAIN | No (Authentic) |
| `VLEUZFDZJKSGMX` | 6.16 | 1 | 0.3167 | 0.6897 | IN-DOMAIN | No (Authentic) |
| `XMOCLSLCDHWDHP` | 4.02 | 0 | 0.4775 | 0.4737 | IN-DOMAIN | No (Authentic) |
| `YKPUWZUDDOIDPM` | 5.62 | 1 | 0.4283 | 0.2969 | OUT-OF-DOMAIN | No (Authentic) |
| `YNVJOQCPHWKWSO` | 4.30 | 0 | 0.3600 | 0.4524 | IN-DOMAIN | No (Authentic) |
| `ZSYPIPFQOQGYHH` | 4.85 | 0 | 0.3250 | 0.3864 | OUT-OF-DOMAIN | No (Authentic) |

#### Target: `COX2_T6` (All External Molecules Tested)

| Connectivity Layer | Measured Median pChEMBL | True Active (T) | Predicted Probability | NN Tanimoto to Training Pool | Domain Status (>= 0.4) | Reference Artifact? |
|---|---|---|---|---|---|---|
| `FAKRSMQSSFJEIM` | 4.92 | 0 | 0.3800 | 0.3667 | OUT-OF-DOMAIN | No (Authentic) |
| `IBGBGRVKPALMCQ` | 4.71 | 0 | 0.0233 | 0.4167 | IN-DOMAIN | No (Authentic) |
| `IXELFRRANAOWSF` | 5.47 | 0 | 0.3394 | 0.1273 | OUT-OF-DOMAIN | No (Authentic) |
| `KTEXNACQROZXEV` | 6.10 | 1 | 0.3717 | 0.3973 | OUT-OF-DOMAIN | No (Authentic) |
| `KVVSCMOUFCNCGX` | 5.63 | 0 | 0.0100 | 1.0000 | IN-DOMAIN | No (Authentic) |
| `KZNIFHPLKGYRTM` | 5.10 | 0 | 0.0700 | 0.4167 | IN-DOMAIN | No (Authentic) |
| `LHPRYOJTASOZGJ` | 4.65 | 0 | 0.1500 | 0.4318 | IN-DOMAIN | No (Authentic) |
| `MBRLOUHOWLUMFF` | 4.09 | 0 | 0.0333 | 0.6939 | IN-DOMAIN | No (Authentic) |
| `MDKGKXOCJGEUJW` | 5.56 | 0 | 0.2433 | 0.5714 | IN-DOMAIN | **YES (EXCLUDED in Run b)** |
| `MIJYXULNPSFWEK` | 4.06 | 0 | 0.1167 | 0.7586 | IN-DOMAIN | No (Authentic) |
| `PCMORTLOPMLEFB` | 4.55 | 0 | 0.0243 | 0.4571 | IN-DOMAIN | No (Authentic) |
| `PFTAWBLQPZVEMU` | 4.03 | 0 | 0.0600 | 0.4561 | IN-DOMAIN | No (Authentic) |
| `PREBVFJICNPEKM` | 4.44 | 0 | 0.0233 | 0.6286 | IN-DOMAIN | No (Authentic) |
| `QBLQLKNOKUHRCH` | 4.33 | 0 | 0.0733 | 0.3750 | OUT-OF-DOMAIN | No (Authentic) |
| `REFJWTPEDVJJIY` | 4.54 | 0 | 0.1933 | 0.4167 | IN-DOMAIN | No (Authentic) |
| `RSYUFYQTACJFML` | 4.16 | 0 | 0.0667 | 0.5577 | IN-DOMAIN | No (Authentic) |
| `RTIXKCRFFJGDFG` | 4.59 | 0 | 0.0133 | 0.5333 | IN-DOMAIN | No (Authentic) |
| `SUTUBQHKZRNZRA` | 4.70 | 0 | 0.0367 | 0.5897 | IN-DOMAIN | No (Authentic) |
| `VFLDPWHFBUODDF` | 4.53 | 0 | 0.0167 | 0.8857 | IN-DOMAIN | No (Authentic) |
| `VLEUZFDZJKSGMX` | 5.65 | 0 | 0.3867 | 0.8889 | IN-DOMAIN | No (Authentic) |
| `WCGUUGGRBIKTOS` | 4.07 | 0 | 0.2433 | 0.5294 | IN-DOMAIN | No (Authentic) |
| `YNVJOQCPHWKWSO` | 4.10 | 0 | 0.1167 | 0.3077 | OUT-OF-DOMAIN | No (Authentic) |
| `YQUVCSBJEUQKSH` | 4.59 | 0 | 0.1967 | 0.4333 | IN-DOMAIN | No (Authentic) |

#### Target: `COX2_T5` (All External Molecules Tested)

| Connectivity Layer | Measured Median pChEMBL | True Active (T) | Predicted Probability | NN Tanimoto to Training Pool | Domain Status (>= 0.4) | Reference Artifact? |
|---|---|---|---|---|---|---|
| `FAKRSMQSSFJEIM` | 4.92 | 0 | 0.7367 | 0.3667 | OUT-OF-DOMAIN | No (Authentic) |
| `IBGBGRVKPALMCQ` | 4.71 | 0 | 0.1167 | 0.4167 | IN-DOMAIN | No (Authentic) |
| `IXELFRRANAOWSF` | 5.47 | 1 | 0.5769 | 0.1273 | OUT-OF-DOMAIN | No (Authentic) |
| `KTEXNACQROZXEV` | 6.10 | 1 | 0.7750 | 0.3973 | OUT-OF-DOMAIN | No (Authentic) |
| `KVVSCMOUFCNCGX` | 5.63 | 1 | 0.4573 | 1.0000 | IN-DOMAIN | No (Authentic) |
| `KZNIFHPLKGYRTM` | 5.10 | 1 | 0.4400 | 0.4167 | IN-DOMAIN | No (Authentic) |
| `LHPRYOJTASOZGJ` | 4.65 | 0 | 0.3517 | 0.4318 | IN-DOMAIN | No (Authentic) |
| `MBRLOUHOWLUMFF` | 4.09 | 0 | 0.0638 | 0.6939 | IN-DOMAIN | No (Authentic) |
| `MDKGKXOCJGEUJW` | 5.56 | 1 | 0.7253 | 0.5714 | IN-DOMAIN | **YES (EXCLUDED in Run b)** |
| `MIJYXULNPSFWEK` | 4.06 | 0 | 0.8300 | 0.7586 | IN-DOMAIN | No (Authentic) |
| `PCMORTLOPMLEFB` | 4.55 | 0 | 0.2491 | 0.4571 | IN-DOMAIN | No (Authentic) |
| `PFTAWBLQPZVEMU` | 4.03 | 0 | 0.2467 | 0.4561 | IN-DOMAIN | No (Authentic) |
| `PREBVFJICNPEKM` | 4.44 | 0 | 0.0925 | 0.6286 | IN-DOMAIN | No (Authentic) |
| `QBLQLKNOKUHRCH` | 4.33 | 0 | 0.3630 | 0.3750 | OUT-OF-DOMAIN | No (Authentic) |
| `REFJWTPEDVJJIY` | 4.54 | 0 | 0.4537 | 0.4167 | IN-DOMAIN | No (Authentic) |
| `RSYUFYQTACJFML` | 4.16 | 0 | 0.2498 | 0.5577 | IN-DOMAIN | No (Authentic) |
| `RTIXKCRFFJGDFG` | 4.59 | 0 | 0.3793 | 0.5333 | IN-DOMAIN | No (Authentic) |
| `SUTUBQHKZRNZRA` | 4.70 | 0 | 0.2303 | 0.5897 | IN-DOMAIN | No (Authentic) |
| `VFLDPWHFBUODDF` | 4.53 | 0 | 0.0450 | 0.8857 | IN-DOMAIN | No (Authentic) |
| `VLEUZFDZJKSGMX` | 5.65 | 1 | 0.6700 | 0.8889 | IN-DOMAIN | No (Authentic) |
| `WCGUUGGRBIKTOS` | 4.07 | 0 | 0.8050 | 0.5294 | IN-DOMAIN | No (Authentic) |
| `YNVJOQCPHWKWSO` | 4.10 | 0 | 0.4375 | 0.3077 | OUT-OF-DOMAIN | No (Authentic) |
| `YQUVCSBJEUQKSH` | 4.59 | 0 | 0.2403 | 0.4333 | IN-DOMAIN | No (Authentic) |

---

## 4. Applicability Domain & Flora Molecule Scoring

All 7,315 fingerprintable flora layers were scored with the frozen final models:

| Target | Threshold | Total Flora Scored | Internal Cutoff (Max F1) | Flora Above Cutoff (%) | Flora in Domain (NN >= 0.4) (%) | Flora Tolerant Domain (NN >= 0.3) (%) | Predictions CSV Path |
|---|---|---|---|---|---|---|---|
| **COX-1 (PTGS1)** | T=6 | 7,315 | `0.39` | 51.47% | 9.17% | 29.16% | [`data/processed/modeling/flora_predictions_cox1_T6.csv`](file:///data/processed/modeling/flora_predictions_cox1_T6.csv) |
| **COX-1 (PTGS1)** | T=5 | 7,315 | `0.34` | 94.82% | 9.17% | 29.08% | [`data/processed/modeling/flora_predictions_cox1_T5.csv`](file:///data/processed/modeling/flora_predictions_cox1_T5.csv) |
| **COX-2 (PTGS2)** | T=6 | 7,315 | `0.36` | 13.82% | 12.54% | 35.89% | [`data/processed/modeling/flora_predictions_cox2_T6.csv`](file:///data/processed/modeling/flora_predictions_cox2_T6.csv) |
| **COX-2 (PTGS2)** | T=5 | 7,315 | `0.16` | 99.43% | 12.55% | 35.89% | [`data/processed/modeling/flora_predictions_cox2_T5.csv`](file:///data/processed/modeling/flora_predictions_cox2_T5.csv) |
| **Xanthine Oxidase (XDH)** | T=6 | 7,315 | `0.40` | 4.01% | 7.71% | 21.05% | [`data/processed/modeling/flora_predictions_xo_T6.csv`](file:///data/processed/modeling/flora_predictions_xo_T6.csv) |
| **Xanthine Oxidase (XDH)** | T=5 | 7,315 | `0.30` | 66.51% | 7.71% | 21.05% | [`data/processed/modeling/flora_predictions_xo_T5.csv`](file:///data/processed/modeling/flora_predictions_xo_T5.csv) |
| **MAO-A (CHRFAM7A/MAOA)** | T=6 | 7,315 | `0.41` | 6.70% | 11.06% | 28.42% | [`data/processed/modeling/flora_predictions_maoa_T6.csv`](file:///data/processed/modeling/flora_predictions_maoa_T6.csv) |
| **MAO-A (CHRFAM7A/MAOA)** | T=5 | 7,315 | `0.38` | 88.72% | 11.06% | 28.42% | [`data/processed/modeling/flora_predictions_maoa_T5.csv`](file:///data/processed/modeling/flora_predictions_maoa_T5.csv) |

> **Strict Scope Constraint:** Predictions written to `data/processed/modeling/flora_predictions_*.csv` are stored solely for downstream use. No plant-level enrichment or aggregation has been executed in this stage.

---

## 5. Artifact & Integrity Ledger

- **Master MPBD SHA-256 (Start):** `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7`
- **Master MPBD SHA-256 (End):** `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` (**MATCH**)
- **Frozen Config SHA-256:** `ED5F00E529F0FE4D7CAE877DC53C88A589F5DF06C9EB6AFBB984DC33D9C81AB4`
- **ChEMBL Database Mode:** Strictly read-only (`mode=ro`). Zero disk writes or schema mutations.
- **Generated Figures:**
  - [`figures/roc_curves.png`](file:///f:/bmppd-thesis/figures/roc_curves.png) (ROC curves per target, 300 dpi)
  - [`figures/pr_curves.png`](file:///f:/bmppd-thesis/figures/pr_curves.png) (PR curves per target, 300 dpi)
  - [`figures/calibration_plots.png`](file:///f:/bmppd-thesis/figures/calibration_plots.png) (10-bin calibration diagrams, 300 dpi)
  - [`figures/cox_external_predicted_vs_measured.png`](file:///f:/bmppd-thesis/figures/cox_external_predicted_vs_measured.png) (Scatter plot of COX predicted probability vs measured pChEMBL, 300 dpi)
  - [`figures/flora_nn_similarity_histograms.png`](file:///f:/bmppd-thesis/figures/flora_nn_similarity_histograms.png) (Flora vs ChEMBL training pool similarity distribution, 300 dpi)
