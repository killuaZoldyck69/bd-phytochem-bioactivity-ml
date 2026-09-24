# Stage 7A: ChEMBL Bioactivity Label Feasibility Assessment Report

- **ChEMBL Release**: `ChEMBL_37` (Creation Date: `2026-05-01 00:00:00.000000`)
- **ChEMBL Database Path**: `F:\datasets\chembl_37\chembl_37_sqlite\chembl_37.db` (Read-Only URI)
- **Execution Timestamp**: 2026-09-24T12:30:51.446060+00:00
- **Master MPBD SHA-256 (Start & End Verified)**: `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7`
- **Total Script Runtime**: 29.20 seconds (0.49 minutes)

---

## 1. Input Molecule Inventory

| Scope | Molecule Count | % of Total | Definition / Filter |
| :--- | :---: | :---: | :--- |
| **Full Inventory** | **200** | 100.0% | All unique 14-char connectivity layers from `compounds_unique.csv` |
| **Curated Drug-Like** | **197** | 98.5% | Excludes `is_inorganic`, `too_small`, `too_large`, and `is_mixture` |

---

## 2. ChEMBL Structure Matching

- **Matched Molecules (Full Set)**: **82 / 200** (**41.00%**)
- **Matched Molecules (Curated Set)**: **81 / 197** (**41.12%**)

### Distribution of Matched ChEMBL Molregnos per Molecule:

| Matched Molregno Count | Molecules | % of Matched |
| :--- | :---: | :---: |
| **1** | 61 | 74.4% |
| **2-5** | 20 | 24.4% |
| **>5** | 1 | 1.2% |

---

## 3. Natural Product Cross-Check (`molecule_dictionary.natural_product`)

- Molecules flagged `natural_product = 1` in ChEMBL: **74** (90.2% of matched molecules).
- Note: ChEMBL's natural product flag is derived from COCONUT and literature curation; absence of a flag does not indicate synthetic origin.

---

## 4. Bioactivity Data Coverage

| Criteria Level | Full Set Molecules | Full % | Curated Molecules | Curated % | Record Definition |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **ALL Activities** | **75** | 37.5% | **74** | 37.6% | Any record in `activities` table |
| **USABLE Records** | **35** | 17.5% | **35** | 17.8% | `=`, `nM`, IC50/Ki/Kd/EC50, no dup/validity comments |
| **STRICT Records** | **21** | 10.5% | **21** | 10.7% | Usable AND `assay_type` in (B,F) AND confidence in (8,9) AND single target |

### Distribution of Usable Activity Records per Molecule (for molecules with >=1 usable record):

- Min: **1** | 25th %: **2** | Median: **4** | 75th %: **7** | Max: **155**

| Usable Records Bin | Number of Molecules | % of Labeled Molecules |
| :--- | :---: | :---: |
| **1 records** | 7 | 20.0% |
| **2-5 records** | 14 | 40.0% |
| **6-20 records** | 8 | 22.9% |
| **>20 records** | 6 | 17.1% |

---

## 5. Assay-Type Breakdown (All Raw Activity Records)

| Assay Type Code | Description | Record Count | % of Raw Records |
| :---: | :--- | :---: | :---: |
| **A** | ADME (absorption, metabolism, etc.) | 946 | 8.7% |
| **B** | Binding (interaction with target) | 2,131 | 19.6% |
| **F** | Functional (cellular/physiological response) | 2,534 | 23.3% |
| **P** | Physicochemical (solubility, permeability, etc.) | 190 | 1.7% |
| **T** | Toxicity (cytotoxicity, in vivo toxicity) | 5,091 | 46.7% |
| **U** | Unassigned | 5 | 0.0% |

---

## 6. Top 30 Biological Targets (STRICT Set)

Ranked by number of distinct Bangladeshi medicinal plant molecules tested:

| Rank | Target ChEMBL ID | Target Name | Target Type | Organism | Distinct Molecules Tested |
| :---: | :--- | :--- | :--- | :--- | :---: |
| 1 | `CHEMBL220` | Acetylcholinesterase | SINGLE PROTEIN | *Homo sapiens* | **3** |
| 2 | `CHEMBL234` | D(3) dopamine receptor | SINGLE PROTEIN | *Homo sapiens* | **3** |
| 3 | `CHEMBL5160` | Transient receptor potential cation channel subfamily A member 1 | SINGLE PROTEIN | *Rattus norvegicus* | **3** |
| 4 | `CHEMBL1916` | Alpha-2C adrenergic receptor | SINGLE PROTEIN | *Homo sapiens* | **2** |
| 5 | `CHEMBL1867` | Alpha-2A adrenergic receptor | SINGLE PROTEIN | *Homo sapiens* | **2** |
| 6 | `CHEMBL235` | Peroxisome proliferator-activated receptor gamma | SINGLE PROTEIN | *Homo sapiens* | **2** |
| 7 | `CHEMBL253` | Cannabinoid receptor 2 | SINGLE PROTEIN | *Homo sapiens* | **2** |
| 8 | `CHEMBL222` | Sodium-dependent noradrenaline transporter | SINGLE PROTEIN | *Homo sapiens* | **2** |
| 9 | `CHEMBL225` | 5-hydroxytryptamine receptor 2C | SINGLE PROTEIN | *Homo sapiens* | **2** |
| 10 | `CHEMBL218` | Cannabinoid receptor 1 | SINGLE PROTEIN | *Homo sapiens* | **2** |
| 11 | `CHEMBL224` | 5-hydroxytryptamine receptor 2A | SINGLE PROTEIN | *Homo sapiens* | **2** |
| 12 | `CHEMBL217` | D(2) dopamine receptor | SINGLE PROTEIN | *Homo sapiens* | **2** |
| 13 | `CHEMBL1075319` | Transient receptor potential cation channel subfamily M member 8 | SINGLE PROTEIN | *Homo sapiens* | **2** |
| 14 | `CHEMBL273` | 5-hydroxytryptamine receptor 1A | SINGLE PROTEIN | *Rattus norvegicus* | **2** |
| 15 | `CHEMBL4078` | Acetylcholinesterase | SINGLE PROTEIN | *Electrophorus electricus* | **2** |
| 16 | `CHEMBL4835` | L-lactate dehydrogenase A chain | SINGLE PROTEIN | *Homo sapiens* | **2** |
| 17 | `CHEMBL1951` | Amine oxidase [flavin-containing] A | SINGLE PROTEIN | *Homo sapiens* | **2** |
| 18 | `CHEMBL205` | Carbonic anhydrase 2 | SINGLE PROTEIN | *Homo sapiens* | **1** |
| 19 | `CHEMBL1942` | Alpha-2B adrenergic receptor | SINGLE PROTEIN | *Homo sapiens* | **1** |
| 20 | `CHEMBL1983` | 5-hydroxytryptamine receptor 1D | SINGLE PROTEIN | *Homo sapiens* | **1** |
| 21 | `CHEMBL1941` | Histamine H2 receptor | SINGLE PROTEIN | *Homo sapiens* | **1** |
| 22 | `CHEMBL1795174` | Mitogen-activated protein kinase 8 | SINGLE PROTEIN | *Mus musculus* | **1** |
| 23 | `CHEMBL1795125` | Carbonic anhydrase | SINGLE PROTEIN | *Dicentrarchus labrax* | **1** |
| 24 | `CHEMBL1821` | Muscarinic acetylcholine receptor M4 | SINGLE PROTEIN | *Homo sapiens* | **1** |
| 25 | `CHEMBL1808` | Angiotensin-converting enzyme | SINGLE PROTEIN | *Homo sapiens* | **1** |
| 26 | `CHEMBL1833` | 5-hydroxytryptamine receptor 2B | SINGLE PROTEIN | *Homo sapiens* | **1** |
| 27 | `CHEMBL2056` | D(1A) dopamine receptor | SINGLE PROTEIN | *Homo sapiens* | **1** |
| 28 | `CHEMBL210` | Beta-2 adrenergic receptor | SINGLE PROTEIN | *Homo sapiens* | **1** |
| 29 | `CHEMBL1973` | Tyrosinase | SINGLE PROTEIN | *Homo sapiens* | **1** |
| 30 | `CHEMBL2176772` | E3 ubiquitin-protein ligase TRIM33 | SINGLE PROTEIN | *Homo sapiens* | **1** |

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
| **Unclassified** | 135 |
| **Enzyme** | 6 |
| **Unclassified protein** | 2 |
| **Other cytosolic protein** | 1 |
| **Secreted protein** | 1 |

---

## 8. Target Bioactivity Distribution (Top 15 Targets, STRICT Set)

Aggregated by median pChEMBL per (molecule, target) pair:

| Target Name | Organism | Tested | Active (pChEMBL >= 6) | Inactive (< 6) | Conflicts (6) | Active (pChEMBL >= 5) | Inactive (< 5) | Conflicts (5) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Acetylcholinesterase** | *Homo sapiens* | 3 | **2** | 1 | 1 | **2** | 1 | 0 |
| **D(3) dopamine receptor** | *Homo sapiens* | 3 | **1** | 2 | 0 | **2** | 1 | 0 |
| **Transient receptor potential cation channel subfamily A member 1** | *Rattus norvegicus* | 3 | **2** | 1 | 0 | **2** | 1 | 0 |
| **Alpha-2C adrenergic receptor** | *Homo sapiens* | 2 | **1** | 1 | 0 | **2** | 0 | 0 |
| **Alpha-2A adrenergic receptor** | *Homo sapiens* | 2 | **1** | 1 | 0 | **2** | 0 | 0 |
| **Peroxisome proliferator-activated receptor gamma** | *Homo sapiens* | 2 | **1** | 1 | 1 | **2** | 0 | 1 |
| **Cannabinoid receptor 2** | *Homo sapiens* | 2 | **2** | 0 | 1 | **2** | 0 | 0 |
| **Sodium-dependent noradrenaline transporter** | *Homo sapiens* | 2 | **1** | 1 | 0 | **1** | 1 | 0 |
| **5-hydroxytryptamine receptor 2C** | *Homo sapiens* | 2 | **1** | 1 | 0 | **2** | 0 | 0 |
| **Cannabinoid receptor 1** | *Homo sapiens* | 2 | **2** | 0 | 1 | **2** | 0 | 0 |
| **5-hydroxytryptamine receptor 2A** | *Homo sapiens* | 2 | **1** | 1 | 1 | **2** | 0 | 0 |
| **D(2) dopamine receptor** | *Homo sapiens* | 2 | **1** | 1 | 0 | **2** | 0 | 0 |
| **Transient receptor potential cation channel subfamily M member 8** | *Homo sapiens* | 2 | **2** | 0 | 0 | **2** | 0 | 0 |
| **5-hydroxytryptamine receptor 1A** | *Rattus norvegicus* | 2 | **1** | 1 | 0 | **2** | 0 | 0 |
| **Acetylcholinesterase** | *Electrophorus electricus* | 2 | **0** | 2 | 0 | **0** | 2 | 0 |

---

## 9. Machine Learning Task Feasibility Summary

| Candidate Task | Total Labeled Molecules | Active Split | Inactive Split | Feasibility Threshold Flags |
| :--- | :---: | :---: | :---: | :--- |
| Target: `Acetylcholinesterase` | **3** | 2 (66.7%) | 1 | `< 200 (Low)` |
| Target: `D(3) dopamine receptor` | **3** | 1 (33.3%) | 2 | `< 200 (Low)` |
| Target: `Transient receptor potential cation channel subfamily A member 1` | **3** | 2 (66.7%) | 1 | `< 200 (Low)` |
| Target: `Alpha-2C adrenergic receptor` | **2** | 1 (50.0%) | 1 | `< 200 (Low)` |
| Target: `Alpha-2A adrenergic receptor` | **2** | 1 (50.0%) | 1 | `< 200 (Low)` |
| Target: `Peroxisome proliferator-activated receptor gamma` | **2** | 1 (50.0%) | 1 | `< 200 (Low)` |
| Target: `Cannabinoid receptor 2` | **2** | 2 (100.0%) | 0 | `< 200 (Low)` |
| Target: `Sodium-dependent noradrenaline transporter` | **2** | 1 (50.0%) | 1 | `< 200 (Low)` |
| Target: `5-hydroxytryptamine receptor 2C` | **2** | 1 (50.0%) | 1 | `< 200 (Low)` |
| Target: `Cannabinoid receptor 1` | **2** | 2 (100.0%) | 0 | `< 200 (Low)` |
| Target: `5-hydroxytryptamine receptor 2A` | **2** | 1 (50.0%) | 1 | `< 200 (Low)` |
| Target: `D(2) dopamine receptor` | **2** | 1 (50.0%) | 1 | `< 200 (Low)` |
| Target: `Transient receptor potential cation channel subfamily M member 8` | **2** | 2 (100.0%) | 0 | `< 200 (Low)` |
| Target: `5-hydroxytryptamine receptor 1A` | **2** | 1 (50.0%) | 1 | `< 200 (Low)` |
| Target: `Acetylcholinesterase` | **2** | 0 (0.0%) | 2 | `< 200 (Low)` |
| **Active against ANY target (pChEMBL >= 6, strict)** | **21** | 14 (66.7%) | 7 | `` |
| **Any usable activity record exists (ChEMBL-tested)** | **82** | 35 (42.7%) | 47 | `` |

---

## 10. Plant-Level Representation

- Total Medicinal Plants Evaluated: **222**
- Plants with >= 1 molecule having **USABLE** activity: **99** (44.6%)
- Plants with >= 1 molecule having **STRICT** activity: **81** (36.5%)

### Labeled Molecules per Plant Distribution:

- **Usable Activity**: Min: **1** | Median: **1** | Max: **5**
- **Strict Activity**: Min: **1** | Median: **1** | Max: **4**

---

## 11. Empirical Risks & Scientific Observations

1. **Label Sparsity**: While a notable fraction of molecules have bioactivity records in ChEMBL, data across specific individual protein targets drops significantly. Only a few top targets achieve >= 200 tested molecules.
2. **Severe Class Imbalance**: For single targets at pChEMBL >= 6, active vs inactive ratios exhibit strong skew depending on whether secondary pharmacology or primary screening was performed.
3. **Assay Heterogeneity**: Functional assays (cell-based, phenotypic) constitute a substantial volume alongside pure binding assays; strict single-protein target modeling requires filtering to assay types `B` and `F` with high confidence scores.

