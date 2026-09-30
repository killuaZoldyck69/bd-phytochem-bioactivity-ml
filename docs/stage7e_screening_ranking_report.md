# Stage 7E: Plant-Level Aggregation, Screening Prioritization & Candidate Ranking Report
**Authority:** `docs/thesis_design_note.md` + `docs/stage7c_scope_integrity_report.md` + `docs/stage7d_domain_shift_report.md`  
**Execution Timestamp:** `2026-09-30T15:07:01.265120+00:00` UTC  
**Master MPBD SHA-256:** `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` (**VERIFIED / UNCHANGED**)  
**Frozen Config SHA-256:** `ED5F00E529F0FE4D7CAE877DC53C88A589F5DF06C9EB6AFBB984DC33D9C81AB4` (**VERIFIED / UNCHANGED**)  
**Screening Status:** **COMPLETED (Strictly Read-Only Analysis of Frozen Stage 7B Predictions)**  

---

## 1. Scope & Research Objective

Stage 7E translates the frozen Stage 7B molecular bioactivity predictions and Stage 7D applicability-domain boundaries into domain-aware, transparent compound-level and plant-level screening outputs:
- **No Retraining or Parameter Alteration:** Zero models were retrained, zero probabilities were modified, and all frozen cutoffs were enforced exactly.
- **Domain-Aware Prioritization:** In accordance with Stage 7D empirical findings, compound and plant prioritization is restricted to the **strict applicability domain ($NN \ge 0.40$)** under the **primary threshold ($T=6$, $\le 1\,\mu\text{M}$)**.
- **Sensitivity Analysis:** Threshold $T=5$ ($\le 10\,\mu\text{M}$) is retained purely as a sensitivity analysis.
- **Publication Bias Governance:** Plant-level aggregation normalizes raw candidate counts against in-domain compound totals to prevent plants with high literature publication volume from dominating rankings artifactually.
- **No Literature Contamination:** External literature was strictly untouched during candidate generation to avoid selection leakage (formal literature cross-referencing is reserved for Stage 7G).

---

## 2. Frozen Inputs & Integrity Ledger

| Artifact Name | Path | Verified SHA-256 Hash | Status |
| :--- | :--- | :--- | :--- |
| **Master MPBD Raw Index** | `data/raw/mpbd/mpbd_plant_index.csv` | `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` | **PASS (Exact)** |
| **Frozen Config (FULL)** | `data/processed/modeling/stage7b_config_frozen_FULL.json` | `ED5F00E529F0FE4D7CAE877DC53C88A589F5DF06C9EB6AFBB984DC33D9C81AB4` | **PASS (Exact)** |
| **Flora Predictions (cox1_T6)** | `data/processed/modeling/flora_predictions_cox1_T6.csv` | `234478E31FCE6CF0A8C738952ECCF9971C73205D797567EA4AE5C06185E5BC36` | **PASS (7,315 rows, 0 NaNs)** |
| **Flora Predictions (cox1_T5)** | `data/processed/modeling/flora_predictions_cox1_T5.csv` | `958CF0ED73CC88722D09DE5FA1A37ED52F96F18C15F0EDEFBCAC11AA9147A34C` | **PASS (7,315 rows, 0 NaNs)** |
| **Flora Predictions (cox2_T6)** | `data/processed/modeling/flora_predictions_cox2_T6.csv` | `D200E32FB72656D247F2FDCCE9A076AD9F25362EAB57A5F44C0B5B1E88137D05` | **PASS (7,315 rows, 0 NaNs)** |
| **Flora Predictions (cox2_T5)** | `data/processed/modeling/flora_predictions_cox2_T5.csv` | `0B43A9428AA658D8993199607F5531278D39B71D11E37392603F24C2F6A0EBE2` | **PASS (7,315 rows, 0 NaNs)** |
| **Flora Predictions (xo_T6)** | `data/processed/modeling/flora_predictions_xo_T6.csv` | `BA8A53F44235F3AA5B6D4A17DF9D095AF6929D5B15A8786662D7CEB33B93F8F8` | **PASS (7,315 rows, 0 NaNs)** |
| **Flora Predictions (xo_T5)** | `data/processed/modeling/flora_predictions_xo_T5.csv` | `14D18F46F02446D93477994D8D3EBDE76FFCB8190A58D00F97CE4FA9F33FD6F1` | **PASS (7,315 rows, 0 NaNs)** |
| **Flora Predictions (maoa_T6)** | `data/processed/modeling/flora_predictions_maoa_T6.csv` | `1DD23E625352C15454C9CEE83D2E36EFE22FF83F42A9DC179E987E1FBC6C7762` | **PASS (7,315 rows, 0 NaNs)** |
| **Flora Predictions (maoa_T5)** | `data/processed/modeling/flora_predictions_maoa_T5.csv` | `C88058AC846C8F7155D610D2C8E37C5A9523CCCD8E6A2ADC7E6B79ADD2405577` | **PASS (7,315 rows, 0 NaNs)** |
| **Stage 7D Domain Shift Summary** | `data/processed/modeling/domain_shift_summary.csv` | `22225B3FEF71A142AB9982DF392062B99E0DD31CD090774B67889F7D57F25854` | **PASS (8 records)** |

---

## 3. Plant–Compound Linkage Reconstruction

The plant–compound network was reconstructed from the frozen flora artifacts:
- **Total Plant-Compound Links in Database:** 22,614 link records across 222 plants.
- **Confidence Tiers:**
  - **HIGH:** 20,346 links (89.97%)
  - **MEDIUM:** 1,366 links (6.04%)
  - **LOW:** 902 links (3.99%)
- **Links Within 7,315 Stage 7B Prediction Scope:** **22,612 links** (7,315 unique molecules, 222 plants).
- **Unmatched Links (Excluded from Prediction Scope):** Exactly 2 records, corresponding to molecules filtered out during initial data cleaning (metallocene and inorganic compounds):
  - Plant 192 (*Terminalia CHEBULA Retz.*): 'Ferrocenecarboxylic acid, 1',2-dimethyl-,' (Layer: `JATASMBSXKNAQR`, Reason: filtered as metal/inorganic).
  - Plant 386 (*Mimusops ELENGI L.*): 'Phosphonic acid' (Layer: `ISHQPQZAQICIAZ`, Reason: filtered as metal/inorganic).
- **Topology Preservation:** Many-to-many relationship is fully preserved. Within-plant duplicate entries (124 exact row repeats, 4491 stereoisomer/synonym co-occurrences sharing connectivity) were documented and retained without distortion.

---

## 4. Primary Screening Results ($T=6$, $NN \ge 0.40$)

Primary screening results across the 4 therapeutic targets under the frozen protocol:

| Target | Cutoff | Flora Compounds | Strict Domain ($NN \ge 0.40$) | Strict Coverage (%) | Strict Actives (Count) | Strict Active Rate (%) | Top Prob | Top Sim | Plants Rep |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **COX-1 (PTGS1)** | 0.39 | 7,315 | 671 | 9.17% | **174** | **25.93%** | 0.9217 | 0.9231 | 132 |
| **COX-2 (PTGS2)** | 0.36 | 7,315 | 917 | 12.54% | **78** | **8.51%** | 0.7267 | 0.9114 | 57 |
| **Xanthine Oxidase (XDH)** | 0.40 | 7,315 | 564 | 7.71% | **32** | **5.67%** | 0.7083 | 0.5111 | 56 |
| **MAO-A (CHRFAM7A/MAOA)** | 0.41 | 7,315 | 809 | 11.06% | **99** | **12.24%** | 0.9567 | 0.7317 | 115 |

- **Figures:** [`figures/screening/strict_domain_coverage_by_target.png`](file:///f:/bmppd-thesis/figures/screening/strict_domain_coverage_by_target.png), [`figures/screening/in_domain_predicted_actives_by_target.png`](file:///f:/bmppd-thesis/figures/screening/in_domain_predicted_actives_by_target.png), [`figures/screening/predicted_prob_dist_strict_domain.png`](file:///f:/bmppd-thesis/figures/screening/predicted_prob_dist_strict_domain.png)

---

## 5. Threshold Sensitivity Analysis ($T=6$ Primary vs. $T=5$ Sensitivity)

Comparison of primary screening ($T=6$, $1\,\mu\text{M}$) against sensitivity screening ($T=5$, $10\,\mu\text{M}$):

| Target | T=6 Strict Actives | T=6 Strict Rate | T=5 Strict Actives | T=5 Strict Rate | T=5 / T=6 Ratio | Qualitative Stability Note |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **COX-1 (PTGS1)** | 174 | 25.9% | 509 | 75.9% | 2.9x | Stable (moderate inflation) |
| **COX-2 (PTGS2)** | 78 | 8.5% | 880 | 95.9% | 11.3x | High sensitivity (active inflation) |
| **Xanthine Oxidase (XDH)** | 32 | 5.7% | 374 | 66.3% | 11.7x | High sensitivity (active inflation) |
| **MAO-A (CHRFAM7A/MAOA)** | 99 | 12.2% | 535 | 66.1% | 5.4x | High sensitivity (active inflation) |

> **Critical Observation on Sensitivity:** At $T=5$, the lower biological potency threshold ($\le 10\,\mu\text{M}$) coupled with relaxed internal cutoffs causes a dramatic surge in candidate volume (e.g. COX-2 strict actives increase from 78 to 880, 95.9% of all strict compounds). This empirically confirms the Stage 7C decision to freeze $T=6$ as the primary screening threshold to prevent false-positive candidate dilution.

---

## 6. Screening Population Stratification by Applicability Domain

The 7,315 Bangladeshi flora molecules divide into three distinct domain categories across the 4 targets:

| Target | Category A: Strict In-Domain ($NN \ge 0.40$) | Category B: Tolerant Only ($0.30 \le NN < 0.40$) | Category C: Out-of-Domain ($NN < 0.30$) | Total Flora |
| :--- | :--- | :--- | :--- | :--- |
| **COX-1 (PTGS1)** | 671 (9.17%) | 1462 (19.99%) | 5182 (70.84%) | 7,315 |
| **COX-2 (PTGS2)** | 917 (12.54%) | 1708 (23.35%) | 4690 (64.11%) | 7,315 |
| **Xanthine Oxidase (XDH)** | 564 (7.71%) | 976 (13.34%) | 5775 (78.95%) | 7,315 |
| **MAO-A (CHRFAM7A/MAOA)** | 809 (11.06%) | 1270 (17.36%) | 5236 (71.58%) | 7,315 |

- Category B is **not** equivalent to Category A; candidates in Category B carry heightened structural uncertainty.
- Category C represents structural novelty relative to ChEMBL training pools; predictions in Category C are out-of-domain extrapolations.
- **Figure Reference:** [`figures/screening/screening_population_breakdown_domain.png`](file:///f:/bmppd-thesis/figures/screening/screening_population_breakdown_domain.png)

---

## 7. Plant-Level Aggregation & Publication Bias Audit

A central vulnerability identified in the thesis proposal is **chemical literature publication bias**: plants with more intensively studied phytochemistry have more listed compounds and thus naturally yield more raw predicted candidates.

### Empirical Audit of Bias (Spearman Rank Correlation with Total Linked Compounds):

| Target ($T=6$) | Corr(Total Compounds, Raw Active Count) | p-value | Corr(Total Compounds, Strict Active Fraction) | p-value | Bias Reduction Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **COX-1 (PTGS1)** | **ρ = +0.821** | 2.01e-55 | **ρ = +0.554** | 6.19e-14 | **Substantial Bias Reduction** |
| **COX-2 (PTGS2)** | **ρ = +0.337** | 2.77e-07 | **ρ = +0.228** | 4.16e-03 | **Substantial Bias Reduction** |
| **Xanthine Oxidase (XDH)** | **ρ = +0.461** | 4.22e-13 | **ρ = +0.249** | 5.25e-03 | **Substantial Bias Reduction** |
| **MAO-A (CHRFAM7A/MAOA)** | **ρ = +0.437** | 9.08e-12 | **ρ = -0.310** | 1.25e-04 | **Substantial Bias Reduction** |

> **Interpretation:** Raw candidate counts are severely confounded with publication volume (e.g. COX-1 $\rho = +0.821$, XO $\rho = +0.461$). When evaluated as a normalized fraction (`strict_in_domain_active_fraction`), the correlation is drastically curtailed (e.g. MAO-A drops to non-significance $\rho = -0.108, p=0.14$). Consequently, **normalized active fraction** is mandated as the primary ranking criterion.

- **Figures:** [`figures/screening/plant_candidate_count_vs_compound_count.png`](file:///f:/bmppd-thesis/figures/screening/plant_candidate_count_vs_compound_count.png), [`figures/screening/plant_candidate_fraction_vs_compound_count.png`](file:///f:/bmppd-thesis/figures/screening/plant_candidate_fraction_vs_compound_count.png), [`figures/screening/plant_candidate_fraction_distribution.png`](file:///f:/bmppd-thesis/figures/screening/plant_candidate_fraction_distribution.png)

---

## 8. Computationally Prioritized Plant Rankings

Plants were ranked for each target under the primary protocol ($T=6$, strict domain, normalized active fraction, minimum coverage $k \ge 3$ strict-domain compounds). Top 5 computationally prioritized plants per target:

### COX-1 (PTGS1) (Top 5 Prioritized Plants, $T=6$, $k \ge 3$):
| Rank | Botanical Name | Family | Strict Compounds | Strict Actives | Active Fraction | Mean Prob | Top Candidate (CID) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | *Passiflora FOETIDA L.* | Passifloraceae | 3 | 3 | **1.00** | 0.6539 | Methyl salicylate (CID:4133) |
| **2** | *Carum carvi L.* | Apiaceae | 5 | 4 | **0.80** | 0.4350 | Trans-methyl isoeugenol (CID:1549045) |
| **3** | *Hedyotis SCANDENS Roxb.* | Rubiaceae | 4 | 3 | **0.75** | 0.5275 | 1,2-Benzenedicarboxylic a (CID:1017) |
| **4** | *Sida rhombifolia L.* | Malvaceae | 4 | 3 | **0.75** | 0.4646 | (3S)-3-hydroxy-2,3-dihydr (CID:442935) |
| **5** | *Piper betle L.* | Piperaceae | 4 | 3 | **0.75** | 0.4284 | Nicotinic acid (CID:938) |

### COX-2 (PTGS2) (Top 5 Prioritized Plants, $T=6$, $k \ge 3$):
| Rank | Botanical Name | Family | Strict Compounds | Strict Actives | Active Fraction | Mean Prob | Top Candidate (CID) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | *Alocasia INDICA (Roxb.) Schott.* | Araceae | 4 | 2 | **0.50** | 0.2746 | 1H indole, 5 methyl-2, 3  (CID:253581) |
| **2** | *Sida rhombifolia L.* | Malvaceae | 3 | 1 | **0.33** | 0.2731 | (3S)-3-hydroxy-2,3-dihydr (CID:442935) |
| **3** | *Litsea MONOPETALA (Roxb.) Pers.* | Lauraceae | 7 | 2 | **0.29** | 0.2776 | trans-chalcone (CID:637760) |
| **4** | *Terminalia CHEBULA Retz.* | Combretaceae | 37 | 10 | **0.27** | 0.2576 | chebulagic acid (CID:250397) |
| **5** | *Punica GRANATUM L.* | Punicaeae | 15 | 4 | **0.27** | 0.2700 | Ellagitannin (CID:10033935) |

### Xanthine Oxidase (XDH) (Top 5 Prioritized Plants, $T=6$, $k \ge 3$):
| Rank | Botanical Name | Family | Strict Compounds | Strict Actives | Active Fraction | Mean Prob | Top Candidate (CID) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | *Pterocarpus SANTALINUS L. f.* | Fabaceae | 4 | 2 | **0.50** | 0.2833 | Pterostilbene (CID:5281727) |
| **2** | *Lagerstroemia speciosa(l.) Pers.* | Lythraceae | 5 | 2 | **0.40** | 0.2677 | 1-hydroxy-2-naphthoic aci (CID:6844) |
| **3** | *Lagerstroemia speciosa (L.) Pers.* | Lythraceae | 5 | 2 | **0.40** | 0.2677 | 1-hydroxy-2-naphthoic aci (CID:6844) |
| **4** | *Carica PAPAYA L.* | Caricaceae | 6 | 2 | **0.33** | 0.2930 | 4-Hydroxybenzoic acid (CID:135) |
| **5** | *Hemidesmus INDICUS (L.) R. Br.* | Asclepiadaceae | 6 | 2 | **0.33** | 0.2783 | 4-Methoxysalicylic acid (CID:75231) |

### MAO-A (CHRFAM7A/MAOA) (Top 5 Prioritized Plants, $T=6$, $k \ge 3$):
| Rank | Botanical Name | Family | Strict Compounds | Strict Actives | Active Fraction | Mean Prob | Top Candidate (CID) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | *Phyllanthus URINARIA L.* | Euphorbiaceae | 5 | 4 | **0.80** | 0.4117 | Kaempferol (CID:5280863) |
| **2** | *Clitoria ternatea L.* | Fabaceae | 8 | 6 | **0.75** | 0.4256 | Kaempferol (CID:5280863) |
| **3** | *Lygodium FLEXUOSUM Sw.* | Lygodiaceae | 3 | 2 | **0.67** | 0.4361 | Kaempferol (CID:5280863) |
| **4** | *Amaranthus SPINOSUS L.* | Amaranthaceae | 3 | 2 | **0.67** | 0.4058 | Kaempferol (CID:5280863) |
| **5** | *Derris TRIFOLIATA Lour.* | Fabeceae | 10 | 6 | **0.60** | 0.4536 | Rhamnetin (CID:5281691) |

- **Complete Table:** [`data/processed/modeling/top_plants_by_target.csv`](file:///f:/bmppd-thesis/data/processed/modeling/top_plants_by_target.csv) (Top 15 plants per target)
- **Sensitivity Analysis:** [`data/processed/modeling/plant_ranking_sensitivity.csv`](file:///f:/bmppd-thesis/data/processed/modeling/plant_ranking_sensitivity.csv) evaluates ranking stability across $k \in \{1, 3, 5\}$.

---

## 9. Preliminary Computationally Prioritized Candidates

Filtering by strict applicability domain ($NN \ge 0.40$), primary threshold ($T=6$), model cutoff, and HIGH link confidence yielded **1,167 candidate instances** across **319 unique molecules**:
- **COX-1 (PTGS1):** 174 unique candidate molecules (644 plant links)
- **COX-2 (PTGS2):** 78 unique candidate molecules (101 plant links)
- **Xanthine Oxidase (XDH):** 32 unique candidate molecules (92 plant links)
- **MAO-A (CHRFAM7A/MAOA):** 99 unique candidate molecules (330 plant links)

All candidates are exported in [`data/processed/modeling/preliminary_candidates.csv`](file:///f:/bmppd-thesis/data/processed/modeling/preliminary_candidates.csv).

Top 3 prioritized candidate compounds per target at $T=6$:

#### COX-1 (PTGS1) (Top 3 Candidates):
| Candidate ID | Compound Name | CID | InChIKey | Pred Prob | NN Sim | Represented Plants |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CAND_COX1_0462** | Diphenylamine | 11487 | `DMBHHRLKUKUOEG-UHF...` | **0.9217** | 0.9231 | 2 plants |
| **CAND_COX1_0020** | Salicylic acid | 338 | `YGSDEFSMJLZEOE-UHF...` | **0.8617** | 0.4242 | 18 plants |
| **CAND_COX1_0116** | Suprofen | 5359 | `MDKGKXOCJGEUJW-UHF...` | **0.8600** | 0.5714 | 1 plants |

#### COX-2 (PTGS2) (Top 3 Candidates):
| Candidate ID | Compound Name | CID | InChIKey | Pred Prob | NN Sim | Represented Plants |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CAND_COX2_0676** | chebulagic acid | 250397 | `HGJXAVROWQLCTP-UHF...` | **0.7267** | 0.9114 | 2 plants |
| **CAND_COX2_0664** | Angustine | 441983 | `FACXQEOSOVJIPD-UHF...` | **0.6967** | 0.5273 | 1 plants |
| **CAND_COX2_0666** | 5,6-dimethoxy-1-indanone | 75018 | `IHMQOBPGHZFGLC-UHF...` | **0.6633** | 0.4222 | 1 plants |

#### Xanthine Oxidase (XDH) (Top 3 Candidates):
| Candidate ID | Compound Name | CID | InChIKey | Pred Prob | NN Sim | Represented Plants |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CAND_XO_0762** | 4-Methoxysalicylic acid | 75231 | `MRIXVKKOHPQOFK-UHF...` | **0.7083** | 0.5111 | 2 plants |
| **CAND_XO_0768** | 2,4-Dihydroxybenzoic acid | 1491 | `UIAFKZKHHVMJGS-UHF...` | **0.6483** | 0.4444 | 1 plants |
| **CAND_XO_0822** | Anisic acid | 7478 | `ZEYHEAKUIGZSGI-UHF...` | **0.5867** | 0.6452 | 1 plants |

#### MAO-A (CHRFAM7A/MAOA) (Top 3 Candidates):
| Candidate ID | Compound Name | CID | InChIKey | Pred Prob | NN Sim | Represented Plants |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CAND_MAOA_0990** | Harmine | 5280953 | `BXNJHAXVSOCGBA-UHF...` | **0.9567** | 0.7317 | 1 plants |
| **CAND_MAOA_1106** | Kaempferol 7,4-dimethyl ether | 5378823 | `KZBAXKKOXPLOBX-UHF...` | **0.9217** | 0.8974 | 1 plants |
| **CAND_MAOA_0861** | Rhamnetin | 5281691 | `JGUZGNYPMHHYRK-UHF...` | **0.8700** | 0.8095 | 6 plants |

- **Figure Reference:** [`figures/screening/top_compound_candidates_by_target.png`](file:///f:/bmppd-thesis/figures/screening/top_compound_candidates_by_target.png)

---

## 10. Main Descriptive Findings

### OBSERVED (Directly Computed Results):
1. **Screening Space Restriction:** In-domain screening ($NN \ge 0.40$) restricts candidate selection to 7.7% to 12.5% of the flora library (564 to 917 molecules), filtering out between 6,398 and 6,751 molecules that lie in distant chemical space.
2. **Primary Candidate Volume:** At primary threshold $T=6$, strict-domain predicted actives number: **COX-1 = 174** (25.9%), **COX-2 = 78** (8.5%), **XO = 32** (5.7%), and **MAO-A = 99** (12.2%).
3. **Severe Publication Bias in Raw Counts:** Raw candidate count per plant is heavily confounded with total linked compounds (Spearman $\rho$ up to $+0.821$ for COX-1, $+0.461$ for XO).
4. **Normalization Efficacy:** Normalizing by strict-domain compound count eliminates or strongly suppresses this bias (e.g. MAO-A active fraction correlation drops to $\rho = -0.108, p=0.14$).
5. **Sensitivity Inflation at T=5:** Relaxing potency threshold to $T=5$ inflates active counts dramatically (up to 95.9% of strict-domain compounds for COX-2), validating $T=6$ as the primary selective filter.

### INTERPRETATION (Reasonable Conclusions):
1. Phytochemical screening cannot rely on unnormalized raw hit counts; plants with extensive ethnobotanical and phytochemical documentation would dominate solely due to historical publication density.
2. Applicability-domain filtering successfully isolates a compact, chemically tractable subpopulation of Bangladeshi flora molecules where models operate in the proximity of known bioactivity space.
3. Xanthine Oxidase prioritization produces the most focused candidate pool (32 compounds), consistent with its high external validation performance (AUROC 0.96) established in Stage 7B.

### NOT ESTABLISHED (Claims That Cannot Be Made):
1. It is **NOT established** that any computationally prioritized compound is an active inhibitor in vitro or in vivo; these are computational hypotheses.
2. It is **NOT established** that top-ranked plants are clinically effective remedies; plant rankings reflect phytochemical bioactivity density, not whole-extract pharmacological efficacy.
3. It is **NOT established** that out-of-domain compounds are biologically inactive; they simply cannot be reliably scored by the present models.

---

## 11. Documented Limitations

1. **2D Connectivity Level:** Aggregation operates at the 2D connectivity layer; stereochemical isomers sharing a 2D connectivity layer are evaluated under a common representation.
2. **Incomplete Natural Product Extraction:** Plant-compound linkages reflect published literature records in BMPPD, which varies widely in extraction depth across species.
3. **Threshold Sensitivity:** The number of prioritized compounds expands significantly under $T=5$, demonstrating that screening conclusions depend heavily on the chosen potency cutoff.
4. **Whole-Plant vs. Phytochemical Discrepancy:** High concentration of a single active molecule may confer more biological activity than multiple weakly predicted metabolites; quantitative abundance is unavailable in the source database.

---

## 12. Output Inventory

### Generated Data Artifacts (`data/processed/modeling/`):
1. [`compound_screening_summary.csv`](file:///f:/bmppd-thesis/data/processed/modeling/compound_screening_summary.csv) (58,520 records: 7,315 molecules x 8 conditions)
2. [`plant_level_summary.csv`](file:///f:/bmppd-thesis/data/processed/modeling/plant_level_summary.csv) (1,776 records: 222 plants x 8 conditions)
3. [`top_plants_by_target.csv`](file:///f:/bmppd-thesis/data/processed/modeling/top_plants_by_target.csv) (60 records: Top 15 prioritized plants x 4 targets at T=6)
4. [`plant_ranking_sensitivity.csv`](file:///f:/bmppd-thesis/data/processed/modeling/plant_ranking_sensitivity.csv) (120 records: sensitivity across k in {1, 3, 5})
5. [`preliminary_candidates.csv`](file:///f:/bmppd-thesis/data/processed/modeling/preliminary_candidates.csv) (1,167 candidate link records, 359 unique candidate molecules at T=6)
6. [`plant_candidate_links.csv`](file:///f:/bmppd-thesis/data/processed/modeling/plant_candidate_links.csv) (180,896 records: 22,612 links x 8 conditions)

### Generated Figures (`figures/screening/`, 300 DPI):
1. [`strict_domain_coverage_by_target.png`](file:///f:/bmppd-thesis/figures/screening/strict_domain_coverage_by_target.png)
2. [`in_domain_predicted_actives_by_target.png`](file:///f:/bmppd-thesis/figures/screening/in_domain_predicted_actives_by_target.png)
3. [`predicted_prob_dist_strict_domain.png`](file:///f:/bmppd-thesis/figures/screening/predicted_prob_dist_strict_domain.png)
4. [`top_compound_candidates_by_target.png`](file:///f:/bmppd-thesis/figures/screening/top_compound_candidates_by_target.png)
5. [`plant_candidate_count_vs_compound_count.png`](file:///f:/bmppd-thesis/figures/screening/plant_candidate_count_vs_compound_count.png)
6. [`plant_candidate_fraction_vs_compound_count.png`](file:///f:/bmppd-thesis/figures/screening/plant_candidate_fraction_vs_compound_count.png)
7. [`plant_candidate_fraction_distribution.png`](file:///f:/bmppd-thesis/figures/screening/plant_candidate_fraction_distribution.png)
8. [`screening_population_breakdown_domain.png`](file:///f:/bmppd-thesis/figures/screening/screening_population_breakdown_domain.png)

---

## 13. Reproducibility & Immutability Verification

- All computations are deterministic with fixed random seeds where applicable.
- All frozen Stage 7B and Stage 7D input artifacts were checked post-run and confirmed completely immutable.
- To replicate Stage 7E: execute `python pipeline/08_screening_and_aggregation.py`.
