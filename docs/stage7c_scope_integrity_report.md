# Stage 7C: Post-Stage-7B Scope Lock, Integrity Audit & Thesis-Design Reconciliation Report

**Authority:** `docs/thesis_design_note.md` (and logged amendments)  
**Audit Status:** **PASS (100% Verified — Read-Only Scope Lock Active)**  
**Execution Timestamp:** `2026-09-30T14:40:00Z` (Local Time: `2026-09-30T20:40:00+06:00`)  
**Lead Auditor:** Antigravity Agentic Pair-Programmer (on behalf of Nahid / Thesis Author)  

---

## 1. Executive Summary & Verification Verdict

An exhaustive, read-only scope lock and integrity audit was performed on the completed Stage 7B full evaluation artifacts before commencing downstream plant-level ethnobotanical enrichment analyses.

### Key Audit Findings:
1. **Master Dataset Immutability:** The raw MPBD master dataset (`data/raw/mpbd/mpbd_plant_index.csv`) remains bit-for-bit identical to its pre-modeling baseline (`0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7`).
2. **Frozen Model Configuration:** The Stage 7B frozen configuration (`data/processed/modeling/stage7b_config_frozen_FULL.json`) is intact (`ED5F00E529F0FE4D7CAE877DC53C88A589F5DF06C9EB6AFBB984DC33D9C81AB4`), confirming that all architectures, hyperparameters, seeds, and scaffold-split CV cutoffs were permanently frozen prior to touching external flora labels.
3. **Prediction Integrity:** All 8 flora prediction CSVs (`flora_predictions_{cox1,cox2,xo,maoa}_T{6,5}.csv`) contain exactly **7,315 scored connectivity layers**, zero duplicate molecules, zero missing values, and strict mathematical consistency with applicability domain thresholds.
4. **Proposal vs. Implementation Reconciliation (GNN Scope):** The thesis proposal originally mentioned exploring Graph Neural Networks alongside fingerprint classifiers. Section 7 of the authoritative study design note explicitly conditioned GNN training on *"only if time allows"*. Stage 7B established that Random Forest + 1-NN baselines fully answer the thesis research question. GNN is **formally not required** for downstream ethnobotanical testing.
5. **Downstream Safety Gate:** All 8 prediction files are verified as immutable inputs. Retraining, re-tuning, post-hoc threshold adjustment, or label editing are strictly blocked.

---

## 2. Repository State & Environment Ledger

- **Git Commit:** `b5ed7be` (*"feat: add stage 7b modeling pipeline, predictions, evaluation reports, and figures"*)
- **Working Tree:** Clean (all modeling artifacts tracked; read-only test suite added under `tests/`).
- **ChEMBL Database Access:** Verified strictly read-only (`mode=ro`). Zero disk writes or schema mutations occurred.
- **Runtime Environment:**
  - Python: `3.14.3`
  - Scikit-learn: `1.7.dev0`
  - RDKit: `2024.09.5`
  - Pandas: `2.2.3`
  - NumPy: `2.2.3`
  - SciPy: `1.15.2`
  - Matplotlib: `3.10.1`

---

## 3. Verified Master Artifact Hashes

All file hashes below were independently recomputed via SHA-256 and confirmed against the Stage 7B execution ledger:

| Artifact Description | File Path | Recorded Stage 7B SHA-256 | Audit Recomputed SHA-256 | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| **MPBD Master Index** | `data/raw/mpbd/mpbd_plant_index.csv` | `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` | `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` | **PASS (EXACT)** |
| **Stage 7B Frozen Config (Full)** | `data/processed/modeling/stage7b_config_frozen_FULL.json` | `ED5F00E529F0FE4D7CAE877DC53C88A589F5DF06C9EB6AFBB984DC33D9C81AB4` | `ED5F00E529F0FE4D7CAE877DC53C88A589F5DF06C9EB6AFBB984DC33D9C81AB4` | **PASS (EXACT)** |
| **Stage 7B Frozen Config (Canon)**| `data/processed/modeling/stage7b_config_frozen.json` | `ED5F00E529F0FE4D7CAE877DC53C88A589F5DF06C9EB6AFBB984DC33D9C81AB4` | `ED5F00E529F0FE4D7CAE877DC53C88A589F5DF06C9EB6AFBB984DC33D9C81AB4` | **PASS (EXACT)** |
| **Stage 7B Final Quality Report** | `data/quality/stage7b_model_report_FULL.md` | `C0E8FF812F26837F2B1E4D00EF84DB0747B4D2549850819A9ACA4BBB75A0B4A2` | `C0E8FF812F26837F2B1E4D00EF84DB0747B4D2549850819A9ACA4BBB75A0B4A2` | **PASS (EXACT)** |
| **Stage 7B Quality Report Sync** | `data/quality/stage7b_model_report.md` | `C0E8FF812F26837F2B1E4D00EF84DB0747B4D2549850819A9ACA4BBB75A0B4A2` | `C0E8FF812F26837F2B1E4D00EF84DB0747B4D2549850819A9ACA4BBB75A0B4A2` | **PASS (EXACT)** |
| **Thesis Design Note** | `docs/thesis_design_note.md` | `45E1CD5B2E1B70D36479CF92EF20692DED1A6029F06AD1430E32FB1BA8A78CAB` | `45E1CD5B2E1B70D36479CF92EF20692DED1A6029F06AD1430E32FB1BA8A78CAB` | **PASS (EXACT)** |

---

## 4. Flora Predictions Artifact Inventory & Integrity Audit

Each of the 8 prediction files corresponds to 7,315 standardized flora connectivity layers scored against the frozen final models.

| Prediction CSV Filename | Target Identifier | Threshold | Row Count | Unique Layers | Missing Values | In-Domain ($NN \ge 0.4$) | Tolerant ($NN \ge 0.3$) | Optimal F1 Cutoff | Flora Above Cutoff (%) | File SHA-256 Hash |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `flora_predictions_cox1_T6.csv` | COX-1 (`CHEMBL221`) | $T=6$ ($1\,\mu\text{M}$) | 7,315 | 7,315 | 0 | 671 (9.17%) | 2,133 (29.16%) | `0.39` | 51.47% | `234478E31FCE6CF0A8C738952ECCF9971C73205D797567EA4AE5C06185E5BC36` |
| `flora_predictions_cox1_T5.csv` | COX-1 (`CHEMBL221`) | $T=5$ ($10\,\mu\text{M}$) | 7,315 | 7,315 | 0 | 671 (9.17%) | 2,127 (29.08%) | `0.34` | 94.82% | `958CF0ED73CC88722D09DE5FA1A37ED52F96F18C15F0EDEFBCAC11AA9147A34C` |
| `flora_predictions_cox2_T6.csv` | COX-2 (`CHEMBL230`) | $T=6$ ($1\,\mu\text{M}$) | 7,315 | 7,315 | 0 | 917 (12.54%) | 2,625 (35.89%) | `0.36` | 13.82% | `D200E32FB72656D247F2FDCCE9A076AD9F25362EAB57A5F44C0B5B1E88137D05` |
| `flora_predictions_cox2_T5.csv` | COX-2 (`CHEMBL230`) | $T=5$ ($10\,\mu\text{M}$) | 7,315 | 7,315 | 0 | 918 (12.55%) | 2,625 (35.89%) | `0.16` | 99.43% | `0B43A9428AA658D8993199607F5531278D39B71D11E37392603F24C2F6A0EBE2` |
| `flora_predictions_xo_T6.csv` | XO (`CHEMBL1929`) | $T=6$ ($1\,\mu\text{M}$) | 7,315 | 7,315 | 0 | 564 (7.71%) | 1,540 (21.05%) | `0.40` | 4.01% | `BA8A53F44235F3AA5B6D4A17DF9D095AF6929D5B15A8786662D7CEB33B93F8F8` |
| `flora_predictions_xo_T5.csv` | XO (`CHEMBL1929`) | $T=5$ ($10\,\mu\text{M}$) | 7,315 | 7,315 | 0 | 564 (7.71%) | 1,540 (21.05%) | `0.30` | 66.51% | `14D18F46F02446D93477994D8D3EBDE76FFCB8190A58D00F97CE4FA9F33FD6F1` |
| `flora_predictions_maoa_T6.csv` | MAO-A (`CHEMBL1951`) | $T=6$ ($1\,\mu\text{M}$) | 7,315 | 7,315 | 0 | 809 (11.06%) | 2,079 (28.42%) | `0.41` | 6.70% | `1DD23E625352C15454C9CEE83D2E36EFE22FF83F42A9DC179E987E1FBC6C7762` |
| `flora_predictions_maoa_T5.csv` | MAO-A (`CHEMBL1951`) | $T=5$ ($10\,\mu\text{M}$) | 7,315 | 7,315 | 0 | 809 (11.06%) | 2,079 (28.42%) | `0.38` | 88.72% | `C88058AC846C8F7155D610D2C8E37C5A9523CCCD8E6A2ADC7E6B79ADD2405577` |

### Integrity Verification Checks:
- **Identifier Uniqueness:** 7,315 unique `inchikey_connectivity` layers in every file. Zero collisions or duplicate rows.
- **Probability Validations:** Strict range $[0.0000, 1.0000]$ observed across all 58,520 prediction records.
- **Mathematical Consistency:** The boolean flag `in_domain_0.4` strictly equals `nn_similarity >= 0.4` across 100% of rows. The boolean flag `in_domain_0.3` strictly equals `nn_similarity >= 0.3` across 100% of rows.

---

## 5. Proposal-vs-Implementation Reconciliation (The GNN Question)

### Background:
In initial thesis proposals or outlines (e.g., `codebase_audit.md` Stage 10 description), candidate modeling approaches mentioned comparing classical fingerprint classifiers (Random Forest, XGBoost) and Graph Neural Networks (GNNs). However, Stage 7B was executed and frozen using strictly **RandomForestClassifier** and a **1-Nearest-Neighbour Tanimoto** baseline.

### Formal Audit Findings:
1. **Design Note Authority:** In `docs/thesis_design_note.md` Section 7 ("Models and evaluation"), the text explicitly specifies:
   > *- "Baseline: ECFP4 fingerprints with random forest or XGBoost. One additional model (a graph network or a second fingerprint family) only if time allows."*
   The inclusion of a GNN was pre-registered as a conditional, exploratory addition (*"only if time allows"*), **not** a mandatory core requirement.
2. **Core Hypothesis Alignment:** Section 2 of `docs/thesis_design_note.md` defines the central research question:
   > *"Can machine-learning models trained on public bioactivity data recover the traditional anti-inflammatory and analgesic uses of Bangladeshi medicinal plants?"*
   The thesis tests an **ethnobotanical information recovery hypothesis**, not a model-architecture benchmarking competition. The Random Forest models (supported by 1-NN baselines) establish rigorous baseline predictive distributions that directly feed the plant-level permutation test.
3. **Pre-Evaluation Freeze Lock:** In `data/processed/modeling/stage7b_config_frozen_FULL.json`, the configuration explicitly locked:
   `"model_family_restriction": "Strictly RandomForest and 1-NN Tanimoto baseline only; no other family permitted."`

### Formal Determinations:
- **Determination A:** The authoritative design note and Stage 7B frozen configuration formally narrowed the model scope to Random Forest and 1-NN Tanimoto.
- **Determination B:** **A GNN is NOT formally required.** The existing frozen RF models completely satisfy the research design.
- **Determination D:** We continue with the RF-based frozen pipeline for all downstream analyses.

### Isolated Contingency Recommendation (If GNN is Ever Requested by Committee):
If an external examiner or committee specifically mandates GNN evaluation, it must be executed as an **isolated sensitivity experiment** without disrupting the frozen Stage 7B baseline:
1. Featurize the 4 target ChEMBL pools and 7,315 flora molecules as molecular graph objects (PyTorch Geometric / DGL).
2. Train a standard Directed Message Passing Neural Network (D-MPNN) or Graph Convolutional Network (GCN) using the *exact identical 5 Bemis-Murcko scaffold folds*.
3. Freeze the GNN architecture and weights in a separate config (`stage7b_config_frozen_GNN.json`).
4. Evaluate on the external flora set under identical Stage 7B governance.
5. Re-run plant-level permutation testing on GNN predictions as a comparative secondary model.

---

## 6. Audit of Threshold Interpretation ($T=6$ vs. $T=5$)

- **$T=6$ (Primary Pre-Registered Analysis):**
  - Definition: Molecule median $\text{pChEMBL} \ge 6.0$, corresponding to an $\text{IC}_{50} / K_i / K_d / \text{EC}_{50} \le 1.0\,\mu\text{M}$ ($1,000\,\text{nM}$).
  - Scientific Meaning: Represents authentic, sub-micromolar pharmacological potency against human single-protein assays.
  - Role in Thesis: Serves as the primary bioactivity label for all hypothesis tests.
- **$T=5$ (Sensitivity Analysis):**
  - Definition: Molecule median $\text{pChEMBL} \ge 5.0$, corresponding to an $\text{IC}_{50} / K_i / K_d / \text{EC}_{50} \le 10.0\,\mu\text{M}$ ($10,000\,\text{nM}$).
  - Scientific Meaning: Tests whether expanding the activity threshold to weak/micromolar binders stabilizes or destabilizes the ethnobotanical signal.
  - Role in Thesis: Strictly a sensitivity control; does not override primary $T=6$ findings.
- **Conflict Rule:** As defined in Section 5 of the design note, molecule-target pairs whose ChEMBL assay records span both sides of the threshold by $>1.0$ log unit are excluded as ambiguous conflicts (`conflict_T6 = True` or `conflict_T5 = True`).

---

## 7. Audit of Applicability Domain Interpretation

- **Metric:** Nearest-Neighbour Tanimoto similarity computed over 2048-bit ECFP4 fingerprints against the target's ChEMBL training pool.
- **Strict Boundary ($NN \ge 0.4$):**
  - Established in cheminformatics as the threshold where Morgan fingerprints capture structural/scaffold analogy rather than spurious bit overlap.
  - Governs primary in-domain vs. out-of-domain performance splits.
- **Tolerant Boundary ($NN \ge 0.3$):**
  - Captures broader structural overlap (shared core rings or general pharmacophores).
- **Observed Flora Domain Coverage:**
  - Flora in strict domain ($NN \ge 0.4$): 7.7% to 12.6% across targets.
  - Flora in tolerant domain ($NN \ge 0.3$): 21.1% to 35.9% across targets.
  - Confirms the known limitation: Bangladeshi medicinal phytochemicals exhibit significant structural novelty relative to synthetic drug-like ChEMBL training sets.

---

## 8. Approved Downstream Inputs for Stage 8

The following files and parameters are **unconditionally approved** as inputs for the plant-level ethnobotanical recovery test:

1. **Frozen Flora Predictions:**
   - Primary: `data/processed/modeling/flora_predictions_cox1_T6.csv`
   - Primary: `data/processed/modeling/flora_predictions_cox2_T6.csv`
   - Exploratory / Negative Control: `data/processed/modeling/flora_predictions_xo_T6.csv`
   - Exploratory / Supportive: `data/processed/modeling/flora_predictions_maoa_T6.csv`
   - Sensitivity: All corresponding `*_T5.csv` files.
2. **Decision Cutoffs (Internal F1-Optimal):**
   - COX-1: $T=6 \to 0.39$; $T=5 \to 0.34$
   - COX-2: $T=6 \to 0.36$; $T=5 \to 0.16$
   - XO: $T=6 \to 0.40$; $T=5 \to 0.30$
   - MAO-A: $T=6 \to 0.41$; $T=5 \to 0.38$
3. **Linkage & Metadata:**
   - `data/processed/compounds/plant_compound_links_confidence.csv` (HIGH-tier plant-compound links)
   - `data/raw/mpbd/mpbd_plant_index.csv` (traditional indications text)

---

## 9. Blocked & Unsafe Operations (Integrity Guardrails)

The following actions are **strictly forbidden**:
- Retraining, re-fitting, or modifying Random Forest or 1-NN models.
- Re-tuning probability cutoffs to optimize plant-level enrichment scores (p-hacking / data snooping).
- Post-hoc modification of `is_reference_compound` labels.
- Re-running external test evaluations with alternative thresholds.
- Introducing new bioactivity targets without supervisor-approved amendments.

---

## 10. Automated Test Suite

A standalone integrity test suite was authored and verified:
- **Test File:** [`tests/test_stage7c_integrity.py`](file:///f:/bmppd-thesis/tests/test_stage7c_integrity.py)
- **Execution Command:** `python -m unittest tests/test_stage7c_integrity.py`
- **Result:** `Ran 4 tests in 0.097s — OK (PASS)`
- **Verifications Automated:**
  - `test_01_mpbd_master_hash`: Validates MPBD plant index SHA-256 against frozen baseline.
  - `test_02_frozen_config_hashes`: Validates FULL and canonical frozen config hashes.
  - `test_03_frozen_config_model_family_lock`: Validates two-model family restriction.
  - `test_04_prediction_files_integrity`: Validates 8 prediction files for row count (7,315), 0 duplicates, 0 NaNs, probability bounds, domain consistency, and exact SHA-256 hashes.

---

## 11. Exact Recommended Next Stage

### **Stage 8: Plant-Level Ethnobotanical Recovery Analysis**
Per Section 8 of `docs/thesis_design_note.md`:
1. **Disease Term Mapping:** Hand-map the top ~300 MPBD Disease terms into 6–10 validated medical categories (pain, inflammation, rheumatism, gout, nervous disorders, etc.), with inter-annotator agreement reported on at least 50 terms.
2. **Plant Scoring:** Compute plant bioactivity fractions (`share_predicted_active` above internal cutoff) and mean probabilities.
3. **Statistical Permutation Testing:** Execute non-parametric label-permutation test ($\ge 10,000$ shuffles).
4. **Control Analyses:** Compare against compound-count-matched plant cohorts and repeat with top 20 and top 50 widespread compounds removed (quercetin, $\beta$-sitosterol, palmitic acid controls).
5. **Multiple Testing Correction:** Apply Holm-Bonferroni correction across primary targets (COX-1 and COX-2).
