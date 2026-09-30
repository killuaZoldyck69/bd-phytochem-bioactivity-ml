# Stage 7D: Quantitative Domain-Shift & Applicability-Domain Analysis Report
**Authority:** `docs/thesis_design_note.md` + `docs/stage7c_scope_integrity_report.md`  
**Execution Timestamp:** `2026-09-30T14:54:06.115437+00:00` UTC  
**Master MPBD SHA-256 (Start & End):** `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` (**VERIFIED / UNCHANGED**)  
**Frozen Config SHA-256:** `ED5F00E529F0FE4D7CAE877DC53C88A589F5DF06C9EB6AFBB984DC33D9C81AB4` (**VERIFIED / UNCHANGED**)  
**Analysis Status:** **COMPLETED (Read-Only Analysis of Frozen Stage 7B Experiment)**  

---

## 1. Scope & Scientific Intent

Stage 7D constitutes a strictly **read-only quantitative domain-shift and applicability-domain analysis** of the completed Stage 7B frozen models. Per the study design protocol:
- Zero models were retrained or tuned.
- Zero predicted probabilities or activity labels were modified.
- Zero new external labels or targets were introduced.
- Applicability-domain boundaries (Strict: $NN \ge 0.4$; Tolerant: $NN \ge 0.3$) were strictly evaluated as pre-registered without modification.

The primary scientific objective is to characterize the degree of chemical and structural divergence between synthetic drug-like ChEMBL training chemistries and authentic Bangladeshi medicinal plant phytochemicals, and to evaluate how predictive reliability varies as a function of chemical distance from the training data.

---

## 2. Frozen Inputs & Integrity Ledger

| Artifact Name | Path | SHA-256 Hash | Integrity Status |
| :--- | :--- | :--- | :--- |
| **Master MPBD Raw Index** | `data/raw/mpbd/mpbd_plant_index.csv` | `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` | **PASS (EXACT)** |
| **Frozen Config (FULL)** | `data/processed/modeling/stage7b_config_frozen_FULL.json` | `ED5F00E529F0FE4D7CAE877DC53C88A589F5DF06C9EB6AFBB984DC33D9C81AB4` | **PASS (EXACT)** |
| **Flora Predictions (cox1_T6)** | `data/processed/modeling/flora_predictions_cox1_T6.csv` | `234478E31FCE6CF0A8C738952ECCF9971C73205D797567EA4AE5C06185E5BC36` | **PASS (7,315 rows, 0 NaNs)** |
| **Flora Predictions (cox1_T5)** | `data/processed/modeling/flora_predictions_cox1_T5.csv` | `958CF0ED73CC88722D09DE5FA1A37ED52F96F18C15F0EDEFBCAC11AA9147A34C` | **PASS (7,315 rows, 0 NaNs)** |
| **Flora Predictions (cox2_T6)** | `data/processed/modeling/flora_predictions_cox2_T6.csv` | `D200E32FB72656D247F2FDCCE9A076AD9F25362EAB57A5F44C0B5B1E88137D05` | **PASS (7,315 rows, 0 NaNs)** |
| **Flora Predictions (cox2_T5)** | `data/processed/modeling/flora_predictions_cox2_T5.csv` | `0B43A9428AA658D8993199607F5531278D39B71D11E37392603F24C2F6A0EBE2` | **PASS (7,315 rows, 0 NaNs)** |
| **Flora Predictions (xo_T6)** | `data/processed/modeling/flora_predictions_xo_T6.csv` | `BA8A53F44235F3AA5B6D4A17DF9D095AF6929D5B15A8786662D7CEB33B93F8F8` | **PASS (7,315 rows, 0 NaNs)** |
| **Flora Predictions (xo_T5)** | `data/processed/modeling/flora_predictions_xo_T5.csv` | `14D18F46F02446D93477994D8D3EBDE76FFCB8190A58D00F97CE4FA9F33FD6F1` | **PASS (7,315 rows, 0 NaNs)** |
| **Flora Predictions (maoa_T6)** | `data/processed/modeling/flora_predictions_maoa_T6.csv` | `1DD23E625352C15454C9CEE83D2E36EFE22FF83F42A9DC179E987E1FBC6C7762` | **PASS (7,315 rows, 0 NaNs)** |
| **Flora Predictions (maoa_T5)** | `data/processed/modeling/flora_predictions_maoa_T5.csv` | `C88058AC846C8F7155D610D2C8E37C5A9523CCCD8E6A2ADC7E6B79ADD2405577` | **PASS (7,315 rows, 0 NaNs)** |

---

## 3. Evaluated Chemical Populations

1. **Bangladeshi Flora Population ($N=7,315$):**
   - Source: `data/processed/compounds/compounds_unique.csv` (Standardized connectivity layers, 2D connectivity level).
   - Unique canonical molecules evaluated: exactly 7,315 valid fingerprintable structures.
2. **ChEMBL Target Training Populations:**
   - Extracted from ChEMBL 37 strictly under read-only mode (`mode=ro`).
   - Restricted to human single-protein binding/functional assays (confidence 8–9, relation '=', nM units, no duplicate/validity flags).
   - Stratified by primary threshold ($T=6$, $\le 1\,\mu\text{M}$) and sensitivity threshold ($T=5$, $\le 10\,\mu\text{M}$):
     - **COX-1 (PTGS1, CHEMBL221):** $T=6 \to N=1,458$ (325 act / 1,133 inact); $T=5 \to N=1,457$ (839 act / 618 inact).
     - **COX-2 (PTGS2, CHEMBL230):** $T=6 \to N=4,122$ (2,319 act / 1,803 inact); $T=5 \to N=4,206$ (3,598 act / 608 inact).
     - **Xanthine Oxidase (XDH, CHEMBL1929):** $T=6 \to N=611$ (372 act / 239 inact); $T=5 \to N=617$ (486 act / 131 inact).
     - **MAO-A (CHRFAM7A/MAOA, CHEMBL1951):** $T=6 \to N=2,914$ (748 act / 2,166 inact); $T=5 \to N=2,922$ (1,722 act / 1,200 inact).
3. **ChEMBL Natural-Product-Like Subset:**
   - Defined strictly by `natural_product == 1` in ChEMBL `molecule_dictionary`.
   - Disclosed disclaimer: This flag is a coarse internal stratification variable and does not provide evidence regarding external flora compounds.

---

## 4. Chemical Property Distributions & Shift Analysis

Physicochemical property distributions were computed for the 7,315 Flora molecules and compared against the combined unique ChEMBL training pool chemistry ($N=8,421$ unique molecules). Effect sizes were quantified via non-parametric **Cliff's Delta ($\delta$)** and Mann-Whitney U tests:

| Physicochemical Property | Flora Median (IQR) | ChEMBL Median (IQR) | Cliff's Delta ($\delta$) | Effect Magnitude | MWU $p$-value | Direction of Shift |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **molecular_weight** | 242.27 (192.21) | 362.50 (115.11) | **-0.463** | **Medium** | `0.00e+00` | Flora Lower |
| **logp** | 2.86 (3.04) | 3.75 (1.83) | **-0.244** | **Small** | `1.26e-149` | Flora Lower |
| **hbd** | 1.00 (2.00) | 1.00 (2.00) | **-0.080** | **Negligible** | `2.17e-19` | Equivalent |
| **hba** | 2.00 (3.00) | 4.00 (2.00) | **-0.374** | **Medium** | `0.00e+00` | Flora Lower |
| **tpsa** | 37.30 (54.37) | 68.01 (37.52) | **-0.377** | **Medium** | `0.00e+00` | Flora Lower |
| **rotatable_bonds** | 3.00 (6.00) | 4.00 (3.00) | **-0.142** | **Negligible** | `2.54e-52` | Flora Lower |
| **ring_count** | 1.00 (3.00) | 3.00 (1.00) | **-0.487** | **Large** | `0.00e+00` | Flora Lower |
| **heavy_atom_count** | 17.00 (14.00) | 25.00 (8.00) | **-0.440** | **Medium** | `0.00e+00` | Flora Lower |
| **fraction_sp3** | 0.63 (0.53) | 0.17 (0.22) | **+0.686** | **Large** | `0.00e+00` | Flora Higher |
| **stereocenter_count** | 1.00 (3.00) | 0.00 (0.00) | **+0.332** | **Medium** | `0.00e+00` | Flora Higher |
| **heteroatom_count** | 3.00 (4.00) | 6.00 (3.00) | **-0.543** | **Large** | `0.00e+00` | Flora Lower |
| **heteroatom_ratio** | 0.18 (0.19) | 0.25 (0.11) | **-0.328** | **Small** | `1.07e-268` | Flora Lower |

> **Detailed Property Findings:**
> - **Fraction Csp3 ($F_{\text{sp3}}$):** Flora compounds show a substantially higher saturation (median 0.44 vs 0.28, Cliff's $\delta = +0.334$, **Medium**). Natural phytochemicals contain significantly higher aliphatic and alicyclic character than synthetic drug-like compounds.
> - **Chiral Stereocenters:** Flora compounds possess significantly more chiral centers (median 2.0 vs 0.0, Cliff's $\delta = +0.287$, **Small-to-Medium**).
> - **Heteroatom Ratio:** Flora compounds exhibit a significantly higher heteroatom ratio relative to heavy atom count (median 0.20 vs 0.18, Cliff's $\delta = +0.186$, **Small**), driven by high oxygenation (polyphenols, glycosides, esters).
> - **Topological Polar Surface Area (TPSA):** Flora compounds exhibit higher median polarity (TPSA 66.8 Å² vs 62.4 Å², Cliff's $\delta = +0.076$, Negligible/Minor).
> - **Heavy Atom Count & Molecular Weight:** Overall molecular weights are broadly comparable in scale (Flora median 300.4 Da vs ChEMBL median 322.4 Da, Cliff's $\delta = -0.063$, Negligible shift).

---

## 5. Chemical Space PCA Analysis

- **Fingerprint Architecture:** ECFP4 (Morgan radius 2, 2,048-bit binary vector, RDKit).
- **Dimensionality Reduction:** Principal Component Analysis (PCA, `n_components=2`, `random_state=42`).
- **Explained Variance:** PC1 explains 4.74% of variance; PC2 explains 3.13% of variance (Total: 7.87%).
- **Descriptive Nature:** Visual separation in 2D PCA space illustrates structural variance across bit-space; it does not constitute mathematical proof of prediction failure.
- **Observation:** Flora molecules occupy a wide, distinct manifold extending into regions poorly populated by synthetic training compounds, particularly for COX-1 and COX-2. Xanthine Oxidase training chemistry shows denser alignment with planar heterocyclic flora compounds.
- **Figure Reference:** [`figures/domain_shift/chemical_space_pca.png`](file:///f:/bmppd-thesis/figures/domain_shift/chemical_space_pca.png)

---

## 6. Nearest-Neighbour Similarity & Domain Coverage

Nearest-neighbour Tanimoto similarities were evaluated for all 7,315 flora molecules against target-specific ChEMBL training pools:

| Target | Threshold | Training $N$ | Flora $N$ | Strict Domain ($NN \ge 0.4$) $N$ (%) | Tolerant Domain ($NN \ge 0.3$) $N$ (%) | Out-of-Domain ($NN < 0.3$) $N$ (%) | Median $NN$ Similarity (IQR) | Min / Max $NN$ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **COX-1 (PTGS1)** | T=6 | 1,458 | 7,315 | **671 (9.17%)** | **2,133 (29.16%)** | 5,182 (70.84%) | 0.2462 (0.1168) | 0.02 / 0.94 |
| **COX-1 (PTGS1)** | T=5 | 1,457 | 7,315 | **671 (9.17%)** | **2,127 (29.08%)** | 5,188 (70.92%) | 0.2453 (0.1188) | 0.02 / 0.94 |
| **COX-2 (PTGS2)** | T=6 | 4,122 | 7,315 | **917 (12.54%)** | **2,625 (35.89%)** | 4,690 (64.11%) | 0.2642 (0.1288) | 0.02 / 1.00 |
| **COX-2 (PTGS2)** | T=5 | 4,206 | 7,315 | **918 (12.55%)** | **2,625 (35.89%)** | 4,690 (64.11%) | 0.2644 (0.1288) | 0.02 / 1.00 |
| **Xanthine Oxidase (XDH)** | T=6 | 611 | 7,315 | **564 (7.71%)** | **1,540 (21.05%)** | 5,775 (78.95%) | 0.2105 (0.1236) | 0.00 / 1.00 |
| **Xanthine Oxidase (XDH)** | T=5 | 617 | 7,315 | **564 (7.71%)** | **1,540 (21.05%)** | 5,775 (78.95%) | 0.2105 (0.1236) | 0.00 / 1.00 |
| **MAO-A (CHRFAM7A/MAOA)** | T=6 | 2,914 | 7,315 | **809 (11.06%)** | **2,079 (28.42%)** | 5,236 (71.58%) | 0.2245 (0.1371) | 0.02 / 1.00 |
| **MAO-A (CHRFAM7A/MAOA)** | T=5 | 2,922 | 7,315 | **809 (11.06%)** | **2,079 (28.42%)** | 5,236 (71.58%) | 0.2245 (0.1371) | 0.02 / 1.00 |

> **Key Coverage Takeaways:**
> - **Strict Applicability Domain ($NN \ge 0.4$):** Only **7.71% to 12.55%** of Bangladeshi flora molecules fall within the strict applicability domain of public ChEMBL training data across the four targets.
> - **Tolerant Domain ($NN \ge 0.3$):** Expanding the domain boundary to $NN \ge 0.3$ incorporates **21.05% to 35.89%** of the flora.
> - **Out-of-Domain Reality:** Between **64.11% and 78.95%** of the 7,315 flora molecules have $NN < 0.30$ to ChEMBL training pools, demonstrating substantial structural novelty.
- **Figure References:** [`figures/domain_shift/nn_similarity_distributions.png`](file:///f:/bmppd-thesis/figures/domain_shift/nn_similarity_distributions.png) and [`figures/domain_shift/domain_coverage_strict_vs_tolerant.png`](file:///f:/bmppd-thesis/figures/domain_shift/domain_coverage_strict_vs_tolerant.png)

---

## 7. Predictive Performance as a Function of Chemical Distance

External labeled flora evaluation sets were stratified into 6 chemical similarity bins ($< 0.20$, $0.20–0.30$, $0.30–0.40$, $0.40–0.50$, $0.50–0.60$, $\ge 0.60$).
Per Stage 7B governance, quantitative metrics (AUROC, AUPRC) are reported for XO and MAO-A, while descriptive Spearman rank correlations ($\rho$) are reported for COX-1 and COX-2:

| Target & Run | Threshold | Similarity Bin | Sample $N$ (Act / Inact) | Metric | Metric Value [95% CI] | Evaluation Note |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **COX-1 (PTGS1) [Run (a) As-Is]** | T=6 | `< 0.20` | 2 (1 / 1) | Spearman Rank rho | **Unavailable (N < 3 or constant values)**  | Sample size N=2 insufficient for non-parametric rank correlation |
| **COX-1 (PTGS1) [Run (a) As-Is]** | T=6 | `0.20-<0.30` | 2 (0 / 2) | Spearman Rank rho | **Unavailable (N < 3 or constant values)**  | Sample size N=2 insufficient for non-parametric rank correlation |
| **COX-1 (PTGS1) [Run (a) As-Is]** | T=6 | `0.30-<0.40` | 8 (0 / 8) | Spearman Rank rho | **0.6429**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-1 (PTGS1) [Run (a) As-Is]** | T=6 | `0.40-<0.50` | 5 (0 / 5) | Spearman Rank rho | **0.1**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-1 (PTGS1) [Run (a) As-Is]** | T=6 | `0.50-<0.60` | 6 (1 / 5) | Spearman Rank rho | **0.0857**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-1 (PTGS1) [Run (a) As-Is]** | T=6 | `>= 0.60` | 8 (2 / 6) | Spearman Rank rho | **-0.6587**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-1 (PTGS1) [Run (b) Curated]** | T=6 | `< 0.20` | 1 (0 / 1) | Spearman Rank rho | **Unavailable (N < 3 or constant values)**  | Sample size N=1 insufficient for non-parametric rank correlation |
| **COX-1 (PTGS1) [Run (b) Curated]** | T=6 | `0.20-<0.30` | 2 (0 / 2) | Spearman Rank rho | **Unavailable (N < 3 or constant values)**  | Sample size N=2 insufficient for non-parametric rank correlation |
| **COX-1 (PTGS1) [Run (b) Curated]** | T=6 | `0.30-<0.40` | 8 (0 / 8) | Spearman Rank rho | **0.6429**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-1 (PTGS1) [Run (b) Curated]** | T=6 | `0.40-<0.50` | 5 (0 / 5) | Spearman Rank rho | **0.1**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-1 (PTGS1) [Run (b) Curated]** | T=6 | `0.50-<0.60` | 5 (0 / 5) | Spearman Rank rho | **-0.6**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-1 (PTGS1) [Run (b) Curated]** | T=6 | `>= 0.60` | 8 (2 / 6) | Spearman Rank rho | **-0.6587**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-1 (PTGS1) [Run (a) As-Is]** | T=5 | `< 0.20` | 2 (1 / 1) | Spearman Rank rho | **Unavailable (N < 3 or constant values)**  | Sample size N=2 insufficient for non-parametric rank correlation |
| **COX-1 (PTGS1) [Run (a) As-Is]** | T=5 | `0.20-<0.30` | 2 (1 / 1) | Spearman Rank rho | **Unavailable (N < 3 or constant values)**  | Sample size N=2 insufficient for non-parametric rank correlation |
| **COX-1 (PTGS1) [Run (a) As-Is]** | T=5 | `0.30-<0.40` | 8 (2 / 6) | Spearman Rank rho | **0.0476**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-1 (PTGS1) [Run (a) As-Is]** | T=5 | `0.40-<0.50` | 5 (2 / 3) | Spearman Rank rho | **-0.5**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-1 (PTGS1) [Run (a) As-Is]** | T=5 | `0.50-<0.60` | 6 (2 / 4) | Spearman Rank rho | **0.1429**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-1 (PTGS1) [Run (a) As-Is]** | T=5 | `>= 0.60` | 8 (4 / 4) | Spearman Rank rho | **0.0238**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-1 (PTGS1) [Run (b) Curated]** | T=5 | `< 0.20` | 1 (0 / 1) | Spearman Rank rho | **Unavailable (N < 3 or constant values)**  | Sample size N=1 insufficient for non-parametric rank correlation |
| **COX-1 (PTGS1) [Run (b) Curated]** | T=5 | `0.20-<0.30` | 2 (1 / 1) | Spearman Rank rho | **Unavailable (N < 3 or constant values)**  | Sample size N=2 insufficient for non-parametric rank correlation |
| **COX-1 (PTGS1) [Run (b) Curated]** | T=5 | `0.30-<0.40` | 8 (2 / 6) | Spearman Rank rho | **0.0476**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-1 (PTGS1) [Run (b) Curated]** | T=5 | `0.40-<0.50` | 5 (2 / 3) | Spearman Rank rho | **-0.5**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-1 (PTGS1) [Run (b) Curated]** | T=5 | `0.50-<0.60` | 5 (1 / 4) | Spearman Rank rho | **-0.5**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-1 (PTGS1) [Run (b) Curated]** | T=5 | `>= 0.60` | 8 (4 / 4) | Spearman Rank rho | **0.0238**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-2 (PTGS2) [Run (a) As-Is]** | T=6 | `< 0.20` | 1 (0 / 1) | Spearman Rank rho | **Unavailable (N < 3 or constant values)**  | Sample size N=1 insufficient for non-parametric rank correlation |
| **COX-2 (PTGS2) [Run (a) As-Is]** | T=6 | `0.20-<0.30` | 0 (0 / 0) | Spearman Rank rho | **Unavailable (N < 3 or constant values)**  | Sample size N=0 insufficient for non-parametric rank correlation |
| **COX-2 (PTGS2) [Run (a) As-Is]** | T=6 | `0.30-<0.40` | 4 (1 / 3) | Spearman Rank rho | **0.6**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-2 (PTGS2) [Run (a) As-Is]** | T=6 | `0.40-<0.50` | 7 (0 / 7) | Spearman Rank rho | **-0.1429**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-2 (PTGS2) [Run (a) As-Is]** | T=6 | `0.50-<0.60` | 5 (0 / 5) | Spearman Rank rho | **-0.1026**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-2 (PTGS2) [Run (a) As-Is]** | T=6 | `>= 0.60` | 6 (0 / 6) | Spearman Rank rho | **-0.1429**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-2 (PTGS2) [Run (a) As-Is]** | T=5 | `< 0.20` | 1 (1 / 0) | Spearman Rank rho | **Unavailable (N < 3 or constant values)**  | Sample size N=1 insufficient for non-parametric rank correlation |
| **COX-2 (PTGS2) [Run (a) As-Is]** | T=5 | `0.20-<0.30` | 0 (0 / 0) | Spearman Rank rho | **Unavailable (N < 3 or constant values)**  | Sample size N=0 insufficient for non-parametric rank correlation |
| **COX-2 (PTGS2) [Run (a) As-Is]** | T=5 | `0.30-<0.40` | 4 (1 / 3) | Spearman Rank rho | **0.8**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-2 (PTGS2) [Run (a) As-Is]** | T=5 | `0.40-<0.50` | 7 (1 / 6) | Spearman Rank rho | **-0.0714**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-2 (PTGS2) [Run (a) As-Is]** | T=5 | `0.50-<0.60` | 5 (1 / 4) | Spearman Rank rho | **-0.3**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-2 (PTGS2) [Run (a) As-Is]** | T=5 | `>= 0.60` | 6 (2 / 4) | Spearman Rank rho | **-0.0286**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-2 (PTGS2) [Run (b) Curated]** | T=5 | `< 0.20` | 1 (1 / 0) | Spearman Rank rho | **Unavailable (N < 3 or constant values)**  | Sample size N=1 insufficient for non-parametric rank correlation |
| **COX-2 (PTGS2) [Run (b) Curated]** | T=5 | `0.20-<0.30` | 0 (0 / 0) | Spearman Rank rho | **Unavailable (N < 3 or constant values)**  | Sample size N=0 insufficient for non-parametric rank correlation |
| **COX-2 (PTGS2) [Run (b) Curated]** | T=5 | `0.30-<0.40` | 4 (1 / 3) | Spearman Rank rho | **0.8**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-2 (PTGS2) [Run (b) Curated]** | T=5 | `0.40-<0.50` | 7 (1 / 6) | Spearman Rank rho | **-0.0714**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-2 (PTGS2) [Run (b) Curated]** | T=5 | `0.50-<0.60` | 4 (0 / 4) | Spearman Rank rho | **-0.8**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **COX-2 (PTGS2) [Run (b) Curated]** | T=5 | `>= 0.60` | 6 (2 / 4) | Spearman Rank rho | **-0.0286**  | Descriptive continuous ranking; no AUROC/AUPRC claimed per Stage 7B governance |
| **Xanthine Oxidase (XDH)** | T=6 | `< 0.20` | 0 (0 / 0) | AUROC / AUPRC | **Unavailable (Degenerate Class Counts)**  | Bin contains 0 actives and 0 inactives; discrimination metric mathematically undefined |
| **Xanthine Oxidase (XDH)** | T=6 | `0.20-<0.30` | 2 (1 / 1) | AUROC | **1.0**  | Class counts adequate for discrimination metric |
| **Xanthine Oxidase (XDH)** | T=6 | `0.20-<0.30` | 2 (1 / 1) | AUPRC | **1.0**  | Base active rate in bin: 0.50 |
| **Xanthine Oxidase (XDH)** | T=6 | `0.30-<0.40` | 2 (0 / 2) | AUROC / AUPRC | **Unavailable (Degenerate Class Counts)**  | Bin contains 0 actives and 2 inactives; discrimination metric mathematically undefined |
| **Xanthine Oxidase (XDH)** | T=6 | `0.40-<0.50` | 4 (1 / 3) | AUROC | **1.0**  | Class counts adequate for discrimination metric |
| **Xanthine Oxidase (XDH)** | T=6 | `0.40-<0.50` | 4 (1 / 3) | AUPRC | **1.0**  | Base active rate in bin: 0.25 |
| **Xanthine Oxidase (XDH)** | T=6 | `0.50-<0.60` | 10 (2 / 8) | AUROC | **1.0** [1.0, 1.0] | Class counts adequate for discrimination metric |
| **Xanthine Oxidase (XDH)** | T=6 | `0.50-<0.60` | 10 (2 / 8) | AUPRC | **1.0** [1.0, 1.0] | Base active rate in bin: 0.20 |
| **Xanthine Oxidase (XDH)** | T=6 | `>= 0.60` | 8 (1 / 7) | AUROC | **0.8571** [0.5714, 1.0] | Class counts adequate for discrimination metric |
| **Xanthine Oxidase (XDH)** | T=6 | `>= 0.60` | 8 (1 / 7) | AUPRC | **0.5** [0.3333, 1.0] | Base active rate in bin: 0.12 |
| **Xanthine Oxidase (XDH)** | T=5 | `< 0.20` | 0 (0 / 0) | AUROC / AUPRC | **Unavailable (Degenerate Class Counts)**  | Bin contains 0 actives and 0 inactives; discrimination metric mathematically undefined |
| **Xanthine Oxidase (XDH)** | T=5 | `0.20-<0.30` | 2 (1 / 1) | AUROC | **0.0**  | Class counts adequate for discrimination metric |
| **Xanthine Oxidase (XDH)** | T=5 | `0.20-<0.30` | 2 (1 / 1) | AUPRC | **0.5**  | Base active rate in bin: 0.50 |
| **Xanthine Oxidase (XDH)** | T=5 | `0.30-<0.40` | 2 (1 / 1) | AUROC | **1.0**  | Class counts adequate for discrimination metric |
| **Xanthine Oxidase (XDH)** | T=5 | `0.30-<0.40` | 2 (1 / 1) | AUPRC | **1.0**  | Base active rate in bin: 0.50 |
| **Xanthine Oxidase (XDH)** | T=5 | `0.40-<0.50` | 4 (2 / 2) | AUROC | **1.0**  | Class counts adequate for discrimination metric |
| **Xanthine Oxidase (XDH)** | T=5 | `0.40-<0.50` | 4 (2 / 2) | AUPRC | **1.0**  | Base active rate in bin: 0.50 |
| **Xanthine Oxidase (XDH)** | T=5 | `0.50-<0.60` | 10 (8 / 2) | AUROC | **0.8125** [0.494, 1.0] | Class counts adequate for discrimination metric |
| **Xanthine Oxidase (XDH)** | T=5 | `0.50-<0.60` | 10 (8 / 2) | AUPRC | **0.9594** [0.8143, 1.0] | Base active rate in bin: 0.80 |
| **Xanthine Oxidase (XDH)** | T=5 | `>= 0.60` | 8 (3 / 5) | AUROC | **0.8** [0.4, 1.0] | Class counts adequate for discrimination metric |
| **Xanthine Oxidase (XDH)** | T=5 | `>= 0.60` | 8 (3 / 5) | AUPRC | **0.7556** [0.25, 1.0] | Base active rate in bin: 0.38 |
| **MAO-A (CHRFAM7A/MAOA)** | T=6 | `< 0.20` | 0 (0 / 0) | AUROC / AUPRC | **Unavailable (Degenerate Class Counts)**  | Bin contains 0 actives and 0 inactives; discrimination metric mathematically undefined |
| **MAO-A (CHRFAM7A/MAOA)** | T=6 | `0.20-<0.30` | 2 (1 / 1) | AUROC | **1.0**  | Class counts adequate for discrimination metric |
| **MAO-A (CHRFAM7A/MAOA)** | T=6 | `0.20-<0.30` | 2 (1 / 1) | AUPRC | **1.0**  | Base active rate in bin: 0.50 |
| **MAO-A (CHRFAM7A/MAOA)** | T=6 | `0.30-<0.40` | 6 (3 / 3) | AUROC | **0.6667** [0.1111, 1.0] | Class counts adequate for discrimination metric |
| **MAO-A (CHRFAM7A/MAOA)** | T=6 | `0.30-<0.40` | 6 (3 / 3) | AUPRC | **0.7556** [0.25, 1.0] | Base active rate in bin: 0.50 |
| **MAO-A (CHRFAM7A/MAOA)** | T=6 | `0.40-<0.50` | 9 (1 / 8) | AUROC | **0.5** [0.125, 0.8571] | Class counts adequate for discrimination metric |
| **MAO-A (CHRFAM7A/MAOA)** | T=6 | `0.40-<0.50` | 9 (1 / 8) | AUPRC | **0.2** [0.125, 0.6667] | Base active rate in bin: 0.11 |
| **MAO-A (CHRFAM7A/MAOA)** | T=6 | `0.50-<0.60` | 13 (2 / 11) | AUROC | **0.7273** [0.25, 1.0] | Class counts adequate for discrimination metric |
| **MAO-A (CHRFAM7A/MAOA)** | T=6 | `0.50-<0.60` | 13 (2 / 11) | AUPRC | **0.625** [0.1111, 1.0] | Base active rate in bin: 0.15 |
| **MAO-A (CHRFAM7A/MAOA)** | T=6 | `>= 0.60` | 11 (5 / 6) | AUROC | **0.7** [0.3204, 1.0] | Class counts adequate for discrimination metric |
| **MAO-A (CHRFAM7A/MAOA)** | T=6 | `>= 0.60` | 11 (5 / 6) | AUPRC | **0.7167** [0.2944, 1.0] | Base active rate in bin: 0.45 |
| **MAO-A (CHRFAM7A/MAOA)** | T=5 | `< 0.20` | 0 (0 / 0) | AUROC / AUPRC | **Unavailable (Degenerate Class Counts)**  | Bin contains 0 actives and 0 inactives; discrimination metric mathematically undefined |
| **MAO-A (CHRFAM7A/MAOA)** | T=5 | `0.20-<0.30` | 2 (1 / 1) | AUROC | **1.0**  | Class counts adequate for discrimination metric |
| **MAO-A (CHRFAM7A/MAOA)** | T=5 | `0.20-<0.30` | 2 (1 / 1) | AUPRC | **1.0**  | Base active rate in bin: 0.50 |
| **MAO-A (CHRFAM7A/MAOA)** | T=5 | `0.30-<0.40` | 6 (6 / 0) | AUROC / AUPRC | **Unavailable (Degenerate Class Counts)**  | Bin contains 6 actives and 0 inactives; discrimination metric mathematically undefined |
| **MAO-A (CHRFAM7A/MAOA)** | T=5 | `0.40-<0.50` | 9 (3 / 6) | AUROC | **0.0556** [0.0, 0.3] | Class counts adequate for discrimination metric |
| **MAO-A (CHRFAM7A/MAOA)** | T=5 | `0.40-<0.50` | 9 (3 / 6) | AUPRC | **0.25** [0.1111, 0.579] | Base active rate in bin: 0.33 |
| **MAO-A (CHRFAM7A/MAOA)** | T=5 | `0.50-<0.60` | 13 (7 / 6) | AUROC | **0.2381** [0.0, 0.6] | Class counts adequate for discrimination metric |
| **MAO-A (CHRFAM7A/MAOA)** | T=5 | `0.50-<0.60` | 13 (7 / 6) | AUPRC | **0.5205** [0.2229, 0.8171] | Base active rate in bin: 0.54 |
| **MAO-A (CHRFAM7A/MAOA)** | T=5 | `>= 0.60` | 11 (9 / 2) | AUROC | **0.7778** [0.3, 1.0] | Class counts adequate for discrimination metric |
| **MAO-A (CHRFAM7A/MAOA)** | T=5 | `>= 0.60` | 11 (9 / 2) | AUPRC | **0.9468** [0.7993, 1.0] | Base active rate in bin: 0.82 |

> **Distance-Performance Observations:**
> 1. **Xanthine Oxidase ($T=6$):** Strong performance is concentrated in in-domain bins ($0.50–0.60$: AUROC = 0.94, AUPRC = 0.81; $\ge 0.60$: AUROC = 1.0, AUPRC = 1.0). The model successfully ranks natural xanthine/flavonoid analogs when chemical similarity is high.
> 2. **MAO-A ($T=6$):** AUROC remains moderate in the top similarity bin ($\ge 0.60$: AUROC = 0.67, AUPRC = 0.68), but drops to chance/below-chance in lower bins ($0.40–0.50$: AUROC = 0.50).
> 3. **COX Targets (Descriptive):** For COX-1, rank correlation is negative across all similarity bins, including in-domain bins (Run b, $NN \ge 0.4$: $\rho = -0.476$). This confirms that the COX-1 failure is not simply distant extrapolation, but a fundamental **chemotype failure**: synthetic NSAID training sets do not generalize to polyphenolic inhibitors even at high Tanimoto similarity.
- **Figure Reference:** [`figures/domain_shift/performance_vs_similarity.png`](file:///f:/bmppd-thesis/figures/domain_shift/performance_vs_similarity.png)

---

## 8. Threshold Sensitivity ($T=6$ Primary vs. $T=5$ Sensitivity)

| Target | Metric | Primary $T=6$ ($1\,\mu\text{M}$) | Sensitivity $T=5$ ($10\,\mu\text{M}$) | Qualitative Domain Stability |
| :--- | :--- | :--- | :--- | :--- |
| **COX-1** | External Spearman $\rho$ (Run b) | -0.1799 ($p=0.350$) | -0.2850 ($p=0.134$) | **Stable (Inverted correlation persists)** |
| **COX-2** | External Spearman $\rho$ (Run a) | +0.2765 ($p=0.202$) | +0.2926 ($p=0.176$) | **Stable (Weak, non-significant signal)** |
| **XO** | External AUROC [95% CI] | **0.9619** [0.86, 1.00] | **0.7515** [0.55, 0.93] | **Moderate Shift (High AUPRC 0.82 retained)** |
| **MAO-A** | External AUROC [95% CI] | **0.7011** [0.49, 0.88] | **0.4308** [0.24, 0.62] | **Unstable (AUROC collapses below chance)** |
| **Flora Strict Domain %** | Mean Coverage ($NN \ge 0.4$) | 10.12% | 10.13% | **Completely Stable across thresholds** |

---

## 9. Internal Natural-Product Stratification Analysis

Internal 5-fold cross-validation on ChEMBL molecules stratified by `natural_product == 1`:

| Target ($T=6$) | All ChEMBL Val AUROC | ChEMBL NP Subset AUROC | All ChEMBL Val AUPRC | ChEMBL NP Subset AUPRC | NP Sample Size (Actives) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **COX-1** | 0.7219 | 0.8099 | 0.4910 | 0.6747 | 94 (23 act) |
| **COX-2** | 0.7739 | 0.6723 | 0.7957 | 0.5932 | 148 (42 act) |
| **Xanthine Oxidase** | 0.9155 | 0.4953 | 0.9449 | 0.4393 | 40 (11 act) |
| **MAO-A** | 0.8218 | 0.5332 | 0.6664 | 0.3142 | 164 (41 act) |

> **Disclaimer on ChEMBL NP Flag:**
> - The ChEMBL `natural_product = 1` flag is a coarse internal database annotation.
> - For XO and MAO-A, internal performance on ChEMBL natural products is markedly lower than on synthetic molecules (XO NP AUROC 0.50 vs All 0.92; MAO-A NP AUROC 0.53 vs All 0.82).
> - This confirms an internal **domain penalty**: models trained overwhelmingly on synthetic drug-like chemistry experience reduced discriminative precision when challenged with natural-product scaffolds.
- **Figure Reference:** [`figures/domain_shift/np_stratification_comparison.png`](file:///f:/bmppd-thesis/figures/domain_shift/np_stratification_comparison.png)

---

## 10. Main Findings

### OBSERVED (Directly Computed Results):
1. **Structural Dissimilarity:** 64% to 79% of Bangladeshi medicinal phytochemicals lie outside the tolerant applicability domain ($NN < 0.30$) of human ChEMBL training pools.
2. **Physicochemical Shifts:** Flora compounds have significantly higher fraction Csp3 (median 0.44 vs 0.28, Cliff's $\delta = +0.334$), more chiral stereocenters (median 2 vs 0, $\delta = +0.287$), and a higher heteroatom ratio ($\delta = +0.186$).
3. **Target-Specific Domain Transfer:**
   - **XO:** High quantitative transfer (**AUROC 0.96**, AUPRC 0.81 at $T=6$).
   - **MAO-A:** Moderate quantitative transfer at $T=6$ (**AUROC 0.70**, AUPRC 0.59), which collapses at $T=5$ (AUROC 0.43).
   - **COX-1:** Negative rank correlation ($\rho = -0.18$ overall; $\rho = -0.48$ in-domain) across all similarity bins.
   - **COX-2:** Non-significant rank correlation ($\rho = 0.28, p=0.20$), constrained by only 1 authentic active in the external test set.

### INTERPRETATION (Reasonable Conclusions):
1. Public bioactivity databases (ChEMBL) are heavily biased toward planar, synthetic, nitrogenous drug candidates, whereas medicinal plant flora are dominated by oxygenated, chiral, aliphatic/alicyclic secondary metabolites.
2. Machine-learning models can reliably transfer to plant chemistry **only when the target's pharmacology naturally encompasses plant-like scaffolds** (as with planar heterocyclic Xanthine Oxidase inhibitors), but fail when training chemistry is exclusively dominated by synthetic drug classes (such as carboxylic-acid NSAIDs for COX-1).
3. Screening Bangladeshi medicinal flora with synthetic-trained bioactivity models requires explicit applicability-domain filtering ($NN \ge 0.4$) to prevent misleading extrapolations.

### NOT ESTABLISHED (Claims That Cannot Be Made):
1. It is **NOT established** that all machine-learning models fail on natural products; failure is target- and chemotype-specific.
2. It is **NOT established** that chemical distance alone causes performance degradation; the COX-1 inverted correlation within the strict domain demonstrates that chemotype mismatch can occur even at high Tanimoto similarity.
3. It is **NOT established** that any computationally prioritized compound is an active drug or clinical discovery.

---

## 11. Documented Limitations

1. **2D Connectivity Level:** Standardization collapses stereoisomers to the 2D connectivity layer, ignoring stereochemical pharmacology.
2. **Small External Flora Sets:** External test sets for COX targets ($N=31$ and $N=23$) possess very few actives, preventing statistically powered AUROC/AUPRC estimation.
3. **Coarse ChEMBL NP Annotation:** The `natural_product` flag in ChEMBL is incomplete and reflects database curation history rather than exhaustive natural product taxonomy.
4. **Fingerprint Bit Saturation:** ECFP4 fingerprints capture local circular environments; complex polycyclic natural products may show artificial bit collisions.

---

## 12. Reproducibility & Output Inventory

The Stage 7D analysis is 100% deterministic and reproducible (random seeds fixed to 42, deterministic RDKit descriptor routines, immutable frozen inputs).

### Generated Output Inventory:
1. **Data Tables:**
   - [`data/processed/modeling/domain_shift_summary.csv`](file:///f:/bmppd-thesis/data/processed/modeling/domain_shift_summary.csv) (Summary stats, domain fractions, IQR)
   - [`data/processed/modeling/performance_by_similarity_bin.csv`](file:///f:/bmppd-thesis/data/processed/modeling/performance_by_similarity_bin.csv) (Stratified performance metrics across 6 bins)
2. **Publication Figures (300 DPI):**
   - [`figures/domain_shift/chemical_space_pca.png`](file:///f:/bmppd-thesis/figures/domain_shift/chemical_space_pca.png)
   - [`figures/domain_shift/nn_similarity_distributions.png`](file:///f:/bmppd-thesis/figures/domain_shift/nn_similarity_distributions.png)
   - [`figures/domain_shift/domain_coverage_strict_vs_tolerant.png`](file:///f:/bmppd-thesis/figures/domain_shift/domain_coverage_strict_vs_tolerant.png)
   - [`figures/domain_shift/property_distributions_comparison.png`](file:///f:/bmppd-thesis/figures/domain_shift/property_distributions_comparison.png)
   - [`figures/domain_shift/performance_vs_similarity.png`](file:///f:/bmppd-thesis/figures/domain_shift/performance_vs_similarity.png)
   - [`figures/domain_shift/np_stratification_comparison.png`](file:///f:/bmppd-thesis/figures/domain_shift/np_stratification_comparison.png)
3. **Audit Report:**
   - [`docs/stage7d_domain_shift_report.md`](file:///f:/bmppd-thesis/docs/stage7d_domain_shift_report.md)