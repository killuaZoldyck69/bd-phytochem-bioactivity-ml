# Stage 7A: ChEMBL Bioactivity Label Feasibility Assessment Report

- **ChEMBL Release**: `ChEMBL_37` (Creation Date: `2026-05-01 00:00:00.000000`)
- **ChEMBL Database Path**: `F:\datasets\chembl_37\chembl_37_sqlite\chembl_37.db` (Read-Only URI)
- **Execution Timestamp**: 2026-09-24T12:40:50.805708+00:00
- **Master MPBD SHA-256 (Start & End Verified)**: `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7`
- **Total Script Runtime**: 588.11 seconds (9.80 minutes)

---

## 1. Input Molecule Inventory

| Scope | Molecule Count | % of Total | Definition / Filter |
| :--- | :---: | :---: | :--- |
| **Full Inventory** | **7,317** | 100.0% | All unique 14-char connectivity layers from `compounds_unique.csv` |
| **Curated Drug-Like** | **7,228** | 98.8% | Excludes `is_inorganic`, `too_small`, `too_large`, and `is_mixture` |

---

## 2. ChEMBL Structure Matching

- **Matched Molecules (Full Set)**: **3,263 / 7,317** (**44.59%**)
- **Matched Molecules (Curated Set)**: **3,207 / 7,228** (**44.37%**)

### Distribution of Matched ChEMBL Molregnos per Molecule:

| Matched Molregno Count | Molecules | % of Matched |
| :--- | :---: | :---: |
| **1** | 2,269 | 69.5% |
| **2-5** | 873 | 26.8% |
| **>5** | 121 | 3.7% |

---

## 3. Natural Product Cross-Check (`molecule_dictionary.natural_product`)

- Molecules flagged `natural_product = 1` in ChEMBL: **3,039** (93.1% of matched molecules).
- Note: ChEMBL's natural product flag is derived from COCONUT and literature curation; absence of a flag does not indicate synthetic origin.

---

## 4. Bioactivity Data Coverage

| Criteria Level | Full Set Molecules | Full % | Curated Molecules | Curated % | Record Definition |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **ALL Activities** | **3,064** | 41.9% | **3,010** | 41.6% | Any record in `activities` table |
| **USABLE Records** | **1,581** | 21.6% | **1,565** | 21.7% | `=`, `nM`, IC50/Ki/Kd/EC50, no dup/validity comments |
| **STRICT Records** | **1,083** | 14.8% | **1,072** | 14.8% | Usable AND `assay_type` in (B,F) AND confidence in (8,9) AND single target |

### Distribution of Usable Activity Records per Molecule (for molecules with >=1 usable record):

- Min: **1** | 25th %: **2** | Median: **4** | 75th %: **11** | Max: **2,464**

| Usable Records Bin | Number of Molecules | % of Labeled Molecules |
| :--- | :---: | :---: |
| **1 records** | 348 | 22.0% |
| **2-5 records** | 567 | 35.9% |
| **6-20 records** | 407 | 25.7% |
| **>20 records** | 259 | 16.4% |

---

## 5. Assay-Type Breakdown (All Raw Activity Records)

| Assay Type Code | Description | Record Count | % of Raw Records |
| :---: | :--- | :---: | :---: |
| **A** | ADME (absorption, metabolism, etc.) | 28,168 | 7.2% |
| **B** | Binding (interaction with target) | 87,279 | 22.4% |
| **F** | Functional (cellular/physiological response) | 177,400 | 45.5% |
| **P** | Physicochemical (solubility, permeability, etc.) | 4,415 | 1.1% |
| **T** | Toxicity (cytotoxicity, in vivo toxicity) | 92,130 | 23.6% |
| **U** | Unassigned | 454 | 0.1% |

---

## 6. Top 30 Biological Targets (STRICT Set)

Ranked by number of distinct Bangladeshi medicinal plant molecules tested:

| Rank | Target ChEMBL ID | Target Name | Target Type | Organism | Distinct Molecules Tested |
| :---: | :--- | :--- | :--- | :--- | :---: |
| 1 | `CHEMBL3242` | Carbonic anhydrase 12 | SINGLE PROTEIN | *Homo sapiens* | **70** |
| 2 | `CHEMBL335` | Tyrosine-protein phosphatase non-receptor type 1 | SINGLE PROTEIN | *Homo sapiens* | **63** |
| 3 | `CHEMBL205` | Carbonic anhydrase 2 | SINGLE PROTEIN | *Homo sapiens* | **62** |
| 4 | `CHEMBL3594` | Carbonic anhydrase 9 | SINGLE PROTEIN | *Homo sapiens* | **60** |
| 5 | `CHEMBL261` | Carbonic anhydrase 1 | SINGLE PROTEIN | *Homo sapiens* | **58** |
| 6 | `CHEMBL2326` | Carbonic anhydrase 7 | SINGLE PROTEIN | *Homo sapiens* | **55** |
| 7 | `CHEMBL1900` | Aldo-keto reductase family 1 member B1 | SINGLE PROTEIN | *Homo sapiens* | **55** |
| 8 | `CHEMBL220` | Acetylcholinesterase | SINGLE PROTEIN | *Homo sapiens* | **54** |
| 9 | `CHEMBL2622` | Aldo-keto reductase family 1 member B1 | SINGLE PROTEIN | *Rattus norvegicus* | **46** |
| 10 | `CHEMBL1978` | Aromatase | SINGLE PROTEIN | *Homo sapiens* | **45** |
| 11 | `CHEMBL4523582` | Replicase polyprotein 1ab | SINGLE PROTEIN | *Severe acute respiratory syndrome coronavirus 2* | **43** |
| 12 | `CHEMBL1951` | Amine oxidase [flavin-containing] A | SINGLE PROTEIN | *Homo sapiens* | **43** |
| 13 | `CHEMBL3729` | Carbonic anhydrase 4 | SINGLE PROTEIN | *Homo sapiens* | **42** |
| 14 | `CHEMBL4302` | ATP-dependent translocase ABCB1 | SINGLE PROTEIN | *Homo sapiens* | **41** |
| 15 | `CHEMBL6007` | Transient receptor potential cation channel subfamily A member 1 | SINGLE PROTEIN | *Homo sapiens* | **38** |
| 16 | `CHEMBL3510` | Carbonic anhydrase 14 | SINGLE PROTEIN | *Homo sapiens* | **37** |
| 17 | `CHEMBL4078` | Acetylcholinesterase | SINGLE PROTEIN | *Electrophorus electricus* | **36** |
| 18 | `CHEMBL4822` | Beta-secretase 1 | SINGLE PROTEIN | *Homo sapiens* | **35** |
| 19 | `CHEMBL4878` | Cytochrome P450 1B1 | SINGLE PROTEIN | *Homo sapiens* | **35** |
| 20 | `CHEMBL235` | Peroxisome proliferator-activated receptor gamma | SINGLE PROTEIN | *Homo sapiens* | **34** |
| 21 | `CHEMBL221` | Prostaglandin G/H synthase 1 | SINGLE PROTEIN | *Homo sapiens* | **32** |
| 22 | `CHEMBL2487` | Amyloid-beta precursor protein | SINGLE PROTEIN | *Homo sapiens* | **31** |
| 23 | `CHEMBL2039` | Amine oxidase [flavin-containing] B | SINGLE PROTEIN | *Homo sapiens* | **30** |
| 24 | `CHEMBL1929` | Xanthine dehydrogenase/oxidase | SINGLE PROTEIN | *Homo sapiens* | **30** |
| 25 | `CHEMBL3471` | Human immunodeficiency virus type 1 integrase | SINGLE PROTEIN | *Human immunodeficiency virus 1* | **30** |
| 26 | `CHEMBL5983` | Aldo-keto reductase family 1 member B10 | SINGLE PROTEIN | *Homo sapiens* | **28** |
| 27 | `CHEMBL5160` | Transient receptor potential cation channel subfamily A member 1 | SINGLE PROTEIN | *Rattus norvegicus* | **26** |
| 28 | `CHEMBL3025` | Carbonic anhydrase 6 | SINGLE PROTEIN | *Homo sapiens* | **25** |
| 29 | `CHEMBL6136` | Lysine-specific histone demethylase 1A | SINGLE PROTEIN | *Homo sapiens* | **25** |
| 30 | `CHEMBL230` | Prostaglandin G/H synthase 2 | SINGLE PROTEIN | *Homo sapiens* | **25** |

---

## 7. Target Classification Breakdown

**Query Used**:
```sql
SELECT DISTINCT st.tid, pc.class_level, pc.pref_name
FROM temp_strict_tids st
JOIN target_components tc ON st.tid = tc.tid
JOIN component_class cc ON tc.component_id = cc.component_id
JOIN protein_classification pc ON cc.protein_class_id = pc.protein_class_id
WHERE pc.class_level = 1
```

| Protein Superfamily / Class (Level 1) | Distinct Molecules Tested |
| :--- | :---: |
| **Unclassified** | 5,146 |
| **Enzyme** | 205 |
| **Unclassified protein** | 154 |
| **Transcription factor** | 82 |
| **Other cytosolic protein** | 67 |
| **Membrane receptor** | 64 |
| **Secreted protein** | 51 |
| **Structural protein** | 21 |
| **Surface antigen** | 17 |
| **Other nuclear protein** | 11 |
| **Transporter** | 5 |
| **Adhesion** | 3 |
| **Other membrane protein** | 2 |
| **Auxiliary transport protein** | 1 |

---

## 8. Target Bioactivity Distribution (Top 15 Targets, STRICT Set)

Aggregated by median pChEMBL per (molecule, target) pair:

| Target Name | Organism | Tested | Active (pChEMBL >= 6) | Inactive (< 6) | Conflicts (6) | Active (pChEMBL >= 5) | Inactive (< 5) | Conflicts (5) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Carbonic anhydrase 12** | *Homo sapiens* | 70 | **27** | 43 | 2 | **66** | 4 | 0 |
| **Tyrosine-protein phosphatase non-receptor type 1** | *Homo sapiens* | 63 | **1** | 62 | 4 | **34** | 29 | 10 |
| **Carbonic anhydrase 2** | *Homo sapiens* | 62 | **15** | 47 | 2 | **51** | 11 | 1 |
| **Carbonic anhydrase 9** | *Homo sapiens* | 60 | **17** | 43 | 1 | **53** | 7 | 0 |
| **Carbonic anhydrase 1** | *Homo sapiens* | 58 | **7** | 51 | 1 | **44** | 14 | 0 |
| **Carbonic anhydrase 7** | *Homo sapiens* | 55 | **22** | 33 | 0 | **50** | 5 | 0 |
| **Aldo-keto reductase family 1 member B1** | *Homo sapiens* | 55 | **6** | 49 | 8 | **25** | 30 | 4 |
| **Acetylcholinesterase** | *Homo sapiens* | 54 | **18** | 36 | 11 | **35** | 19 | 4 |
| **Aldo-keto reductase family 1 member B1** | *Rattus norvegicus* | 46 | **13** | 33 | 3 | **30** | 16 | 0 |
| **Aromatase** | *Homo sapiens* | 45 | **13** | 32 | 9 | **30** | 15 | 7 |
| **Replicase polyprotein 1ab** | *Severe acute respiratory syndrome coronavirus 2* | 43 | **11** | 32 | 12 | **36** | 7 | 12 |
| **Amine oxidase [flavin-containing] A** | *Homo sapiens* | 43 | **12** | 31 | 3 | **26** | 17 | 2 |
| **Carbonic anhydrase 4** | *Homo sapiens* | 42 | **12** | 30 | 0 | **29** | 13 | 1 |
| **ATP-dependent translocase ABCB1** | *Homo sapiens* | 41 | **4** | 37 | 3 | **17** | 24 | 6 |
| **Transient receptor potential cation channel subfamily A member 1** | *Homo sapiens* | 38 | **10** | 28 | 6 | **22** | 16 | 8 |

---

## 9. Machine Learning Task Feasibility Summary

| Candidate Task | Total Labeled Molecules | Active Split | Inactive Split | Feasibility Threshold Flags |
| :--- | :---: | :---: | :---: | :--- |
| Target: `Carbonic anhydrase 12` | **70** | 27 (38.6%) | 43 | `< 200 (Low)` |
| Target: `Tyrosine-protein phosphatase non-receptor type 1` | **63** | 1 (1.6%) | 62 | `< 200 (Low)` |
| Target: `Carbonic anhydrase 2` | **62** | 15 (24.2%) | 47 | `< 200 (Low)` |
| Target: `Carbonic anhydrase 9` | **60** | 17 (28.3%) | 43 | `< 200 (Low)` |
| Target: `Carbonic anhydrase 1` | **58** | 7 (12.1%) | 51 | `< 200 (Low)` |
| Target: `Carbonic anhydrase 7` | **55** | 22 (40.0%) | 33 | `< 200 (Low)` |
| Target: `Aldo-keto reductase family 1 member B1` | **55** | 6 (10.9%) | 49 | `< 200 (Low)` |
| Target: `Acetylcholinesterase` | **54** | 18 (33.3%) | 36 | `< 200 (Low)` |
| Target: `Aldo-keto reductase family 1 member B1` | **46** | 13 (28.3%) | 33 | `< 200 (Low)` |
| Target: `Aromatase` | **45** | 13 (28.9%) | 32 | `< 200 (Low)` |
| Target: `Replicase polyprotein 1ab` | **43** | 11 (25.6%) | 32 | `< 200 (Low)` |
| Target: `Amine oxidase [flavin-containing] A` | **43** | 12 (27.9%) | 31 | `< 200 (Low)` |
| Target: `Carbonic anhydrase 4` | **42** | 12 (28.6%) | 30 | `< 200 (Low)` |
| Target: `ATP-dependent translocase ABCB1` | **41** | 4 (9.8%) | 37 | `< 200 (Low)` |
| Target: `Transient receptor potential cation channel subfamily A member 1` | **38** | 10 (26.3%) | 28 | `< 200 (Low)` |
| **Active against ANY target (pChEMBL >= 6, strict)** | **1,083** | 495 (45.7%) | 588 | `>= 1,000` |
| **Any usable activity record exists (ChEMBL-tested)** | **3,263** | 1,581 (48.5%) | 1,682 | `>= 1,000` |

---

## 10. Plant-Level Representation

- Total Medicinal Plants Evaluated: **222**
- Plants with >= 1 molecule having **USABLE** activity: **215** (96.8%)
- Plants with >= 1 molecule having **STRICT** activity: **215** (96.8%)

### Labeled Molecules per Plant Distribution:

- **Usable Activity**: Min: **1** | Median: **21** | Max: **173**
- **Strict Activity**: Min: **1** | Median: **16** | Max: **134**

---

## 11. Empirical Risks & Scientific Observations

1. **Label Sparsity**: While a notable fraction of molecules have bioactivity records in ChEMBL, data across specific individual protein targets drops significantly. Only a few top targets achieve >= 200 tested molecules.
2. **Severe Class Imbalance**: For single targets at pChEMBL >= 6, active vs inactive ratios exhibit strong skew depending on whether secondary pharmacology or primary screening was performed.
3. **Assay Heterogeneity**: Functional assays (cell-based, phenotypic) constitute a substantial volume alongside pure binding assays; strict single-protein target modeling requires filtering to assay types `B` and `F` with high confidence scores.

