# Quality Report: COX Go/No-Go Data Check (Design Note Section 9)
**ChEMBL Release:** ChEMBL_37 (Created: 2026-05-01 00:00:00.000000)  
**Database:** `F:/datasets/chembl_37/chembl_37_sqlite/chembl_37.db` (Opened Read-Only)  
**Date Generated:** 2026-09-25  
**Master MPBD SHA-256 (Start & End):** `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` (Verified Integrity)  
**Flora Molecules:** `data/processed/compounds/compounds_unique.csv` (7,317 unique layers; 5,629 ChEMBL molregnos covering 3,263 layers)  

---

## 1. Target Dictionary Verification

All targets verified against ChEMBL 37 `target_dictionary` as **Homo sapiens** and **SINGLE PROTEIN**:

| Role | Target | ChEMBL ID | Target ID (`tid`) | Preferred Name | Organism | Target Type |
|---|---|---|---|---|---|---|
| Primary | COX-1 | `CHEMBL221` | 96 | Prostaglandin G/H synthase 1 | Homo sapiens | SINGLE PROTEIN |
| Primary | COX-2 | `CHEMBL230` | 126 | Prostaglandin G/H synthase 2 | Homo sapiens | SINGLE PROTEIN |
| Exploratory | Xanthine Oxidase | `CHEMBL1929` | 149 | Xanthine dehydrogenase/oxidase | Homo sapiens | SINGLE PROTEIN |
| Exploratory | MAO-A | `CHEMBL1951` | 86 | Amine oxidase [flavin-containing] A | Homo sapiens | SINGLE PROTEIN |

> **Single-Protein Exhaustiveness Confirmation:** Checked all human single-protein targets in ChEMBL 37 matching `cyclooxygenase` or `prostaglandin g/h synthase`. Exactly two exist: COX-1 (`CHEMBL221`, tid 96) and COX-2 (`CHEMBL230`, tid 126). No human single-protein target was missed.

---

## 2. Record Funnel & Activity Labeling

Activities filtered strictly per Design Note Section 5 rules:
- `standard_relation = '='`, `standard_units = 'nM'`, `standard_type IN ('IC50', 'Ki', 'Kd', 'EC50')`
- `potential_duplicate = 0`, `data_validity_comment IS NULL`, `pchembl_value IS NOT NULL`
- Assays: `assay_type IN ('B', 'F')`, `confidence_score IN (8, 9)`, `assays.tid = target.tid`
- Leakage removal: 14-character InChIKey connectivity layer partitioning (flora external set vs training pool).
- Conflict definition: records span threshold `(min < T and max >= T) AND (max - min) > 1.0` log unit. Conflicts excluded.

### COX-1 (CHEMBL221, tid 96)

- **Raw Filtered Records:** 1,807
- **Distinct `molregno`s:** 1,569
- **Distinct Connectivity Layers:** 1,525 (Training Pool: 1,493, Flora: 32)

| Set | Threshold | Total Layers | Conflicts Excluded | Labeled Layers | Actives | Inactives | Active Fraction |
|---|---|---|---|---|---|---|---|
| **Training Pool** | T = 6 (Primary) | 1,493 | 35 | **1,458** | 325 | 1,133 | 22.3% |
| **Training Pool** | T = 5 (Sensitivity) | 1,493 | 36 | **1,457** | 839 | 618 | 57.6% |
| **Flora External Set** | T = 6 (Primary) | 32 | 0 | **32** | 4 | 28 | 12.5% |
| **Flora External Set** | T = 5 (Sensitivity) | 32 | 0 | **32** | 13 | 19 | 40.6% |

### COX-2 (CHEMBL230, tid 126)

- **Raw Filtered Records:** 5,142
- **Distinct `molregno`s:** 4,389
- **Distinct Connectivity Layers:** 4,273 (Training Pool: 4,248, Flora: 25)

| Set | Threshold | Total Layers | Conflicts Excluded | Labeled Layers | Actives | Inactives | Active Fraction |
|---|---|---|---|---|---|---|---|
| **Training Pool** | T = 6 (Primary) | 4,248 | 126 | **4,122** | 2,319 | 1,803 | 56.3% |
| **Training Pool** | T = 5 (Sensitivity) | 4,248 | 42 | **4,206** | 3,598 | 608 | 85.5% |
| **Flora External Set** | T = 6 (Primary) | 25 | 2 | **23** | 1 | 22 | 4.3% |
| **Flora External Set** | T = 5 (Sensitivity) | 25 | 2 | **23** | 6 | 17 | 26.1% |

### Xanthine Oxidase (CHEMBL1929, tid 149)

- **Raw Filtered Records:** 776
- **Distinct `molregno`s:** 658
- **Distinct Connectivity Layers:** 650 (Training Pool: 620, Flora: 30)

| Set | Threshold | Total Layers | Conflicts Excluded | Labeled Layers | Actives | Inactives | Active Fraction |
|---|---|---|---|---|---|---|---|
| **Training Pool** | T = 6 (Primary) | 620 | 9 | **611** | 372 | 239 | 60.9% |
| **Training Pool** | T = 5 (Sensitivity) | 620 | 3 | **617** | 486 | 131 | 78.8% |
| **Flora External Set** | T = 6 (Primary) | 30 | 3 | **27** | 5 | 22 | 18.5% |
| **Flora External Set** | T = 5 (Sensitivity) | 30 | 3 | **27** | 15 | 12 | 55.6% |

### MAO-A (CHEMBL1951, tid 86)

- **Raw Filtered Records:** 3,691
- **Distinct `molregno`s:** 3,121
- **Distinct Connectivity Layers:** 2,989 (Training Pool: 2,946, Flora: 43)

| Set | Threshold | Total Layers | Conflicts Excluded | Labeled Layers | Actives | Inactives | Active Fraction |
|---|---|---|---|---|---|---|---|
| **Training Pool** | T = 6 (Primary) | 2,946 | 32 | **2,914** | 748 | 2,166 | 25.7% |
| **Training Pool** | T = 5 (Sensitivity) | 2,946 | 24 | **2,922** | 1,722 | 1,200 | 58.9% |
| **Flora External Set** | T = 6 (Primary) | 43 | 1 | **42** | 12 | 30 | 28.6% |
| **Flora External Set** | T = 5 (Sensitivity) | 43 | 1 | **42** | 26 | 16 | 61.9% |

---

## 3. Additional Diagnostics

### (a) Publication Concentration in Training Pool

| Target | ChEMBL ID | Training Pool Records | Distinct `doc_id` | Top 5 Docs Records | Top 5 Docs Share (%) |
|---|---|---|---|---|---|
| COX-1 | `CHEMBL221` | 1,764 | 246 | 215 | 12.2% |
| COX-2 | `CHEMBL230` | 5,107 | 443 | 720 | 14.1% |
| Xanthine Oxidase | `CHEMBL1929` | 692 | 60 | 207 | 29.9% |
| MAO-A | `CHEMBL1951` | 3,619 | 366 | 385 | 10.6% |

### (b) Scaffold Diversity in Training Pool

Evaluated on representative structures from each training pool connectivity layer using Bemis-Murcko 2-core molecular framework analysis:

| Target | ChEMBL ID | Analyzed Layers | Distinct Scaffolds | Top 10 Scaffolds Share (%) | Acyclic Layers Count | Acyclic Share (%) |
|---|---|---|---|---|---|---|
| COX-1 | `CHEMBL221` | 1,493 | 443 | 25.1% (375) | 3 | 0.2% |
| COX-2 | `CHEMBL230` | 4,248 | 1,083 | 19.7% (836) | 7 | 0.2% |
| Xanthine Oxidase | `CHEMBL1929` | 620 | 240 | 26.8% (166) | 0 | 0.0% |
| MAO-A | `CHEMBL1951` | 2,946 | 917 | 17.1% (503) | 3 | 0.1% |

### (c) Filter Sensitivity Analysis (Information Only — Design Rules Unchanged)

Counts of training pool connectivity layers available if specific Section 5 filters are relaxed:

| Target | ChEMBL ID | Baseline (Section 5 Filters) | Without Confidence Filter (`conf IN (8,9)` dropped) | Without Assay Type Filter (`assay_type IN (B,F)` dropped) |
|---|---|---|---|---|
| COX-1 | `CHEMBL221` | 1,493 | 1,493 (+0) | 1,590 (+97) |
| COX-2 | `CHEMBL230` | 4,248 | 4,248 (+0) | 4,262 (+14) |
| Xanthine Oxidase | `CHEMBL1929` | 620 | 620 (+0) | 620 (+0) |
| MAO-A | `CHEMBL1951` | 2,946 | 2,946 (+0) | 3,018 (+72) |

> *Note: As specified in Section 5 of the design note, these alternative filter counts are provided for diagnostic evaluation only and are NOT used in the study.*

### (d) Flora Molecules with Labeled Data in ChEMBL 37

#### COX-1 Flora Labeled Molecules (CHEMBL221)

| InChIKey Connectivity | Compound Name | Plants in MPBD | ChEMBL Records | Median pChEMBL | Conflict T=6 | Label T=6 | Common Flora (>=20 plants) |
|---|---|---|---|---|---|---|---|
| `OYHQOLUKZRVURQ` | (9E.12E)-9.12-Octadecadienoic Acid|(Z, Z)?9,12?Octadecadienoic acid|(Z,Z)-9,12-Octadecadienoic acid|1-Triacontanol|2,3,5-Trimethylpyrazine|24-Ethyllathosterol|4-Hydroxycinnamic acid|9, 12-Octadecadienoic acid (Z, Z)-, methyl ester|9,12-Octadecadienoic Acid|9,12-Octadecadienoic acid|9,12-Octadecadienoic acid (Z,Z)|9,12-Octadecadienoic acid (Z,Z)-|9,12-Octadecadienoic acid (z,z)-|9,12-octadecadienoic acid|9,12?Octadecadienoic acid (Z,Z)|9.12-Octadecadienoic acid|Arachidic acid|Cianidanol|Cis-9,cis-12-Octadecadienoic acid|Citric acid|Cycloartanol|D-Glucose|Entadamide B|Linoleic Acid|Linoleic acid|Linolenic acid|Lupeol|Luteolin|Mannitol|Nicotinic acid|Octadeca-9,12-dienoic acid|Oleic acid|Stigmasterol|beta-Sitosterol|cis,cis-Linoleic acid|cis-11-Eicosenoic acid|cis-9,12-Linoleic acid|delta7-Avenasterol|linoleic|linoleic acid | 91 | 1 | 4.89 | False | Inactive (0) | YES |
| `DTOSIQBPPRVQHS` | 9,12,15-Octadecatrienoic Acid|9,12,15-Octadecatrienoic acid|9,12,15-Octadecatrienoic acid (alpha.-Linolenic acid)|9,12,15-Octadecatrienoic acid, (Z,Z,Z)-|9,12,15-Octadecatrienoic acid, (z,z,z)-|9,12,15-octadecatrienoic acid,(z,z,z)-|9,12,15Octadecatrienoic acid|Ancistrocladine|Chlorogenic acid|Linolenic acid|Nonanoic acid|a-Linolenic acid|alpha-Linolenic acid|alpha-linolenic acid|linolenic acid | 47 | 1 | 5.40 | False | Inactive (0) | YES |
| `RRAFCDWBNXTKKO` | Eugenol|Eugenol/ Phenol, 4-allyl-2-methoxy|eugenol|phenylpropanoid | 43 | 1 | 4.96 | False | Inactive (0) | YES |
| `PFTAWBLQPZVEMU` | (+)-Catechin|(+)-catechin|(-)-Catechin|(-)-Epicatechin|(-)-epicatechin|(?)-Epicatechin|3-Methyl-2-buten-1-OL|Catechin|Catechin [ Recheck plz]|Catechin hydrate|Cianidanol|Epicatechin|catechin|epicatechin | 33 | 2 | 4.26 | False | Inactive (0) | YES |
| `RECUKUPTGUEGMW` | Carvacrol|Phenol, 2-methyl-5-(1-methylethyl)|carvacrol|p- Cymene | 32 | 1 | 5.40 | False | Inactive (0) | YES |
| `XMOCLSLCDHWDHP` | (+)-Gallocatechin|(+)-epigallocatechin|(-)-Epigallocatechin|Epigallocatechin|Gallocatechin|epigallocatechin|gallocatechin | 15 | 1 | 4.02 | False | Inactive (0) | no |
| `PCMORTLOPMLEFB` | Sinapic acid|Sinapinic acid|sinapic acid | 10 | 1 | 4.41 | False | Inactive (0) | no |
| `TZBJGXHYKVUXJN` | 4,5,7- Trihydroxy isoflavone|Genistein | 9 | 1 | 4.10 | False | Inactive (0) | no |
| `SCCDQYPEOIRVGX` | Acetyleugenol|Eugenyl acetate | 8 | 1 | 5.52 | False | Inactive (0) | no |
| `ILEDWLMCKZNDJK` | Esculetin|aesculetin|esculetin | 6 | 1 | 4.24 | False | Inactive (0) | no |
| `LUKBXSAWLPMMSZ` | Resveratrol | 4 | 5 | 5.96 | False | Inactive (0) | no |
| `VFLDPWHFBUODDF` | Curcumin|curcumin|diferuloylmethane | 4 | 4 | 4.76 | False | Inactive (0) | no |
| `QBLQLKNOKUHRCH` | Steppogenin|steppogenin | 3 | 1 | 5.23 | False | Inactive (0) | no |
| `QJVXKWHHAMZTBY` | Syringin|eleutheroside B | 3 | 1 | 4.44 | False | Inactive (0) | no |
| `LHPRYOJTASOZGJ` | moracin M | 2 | 1 | 6.30 | False | Active (1) | no |
| `YKPUWZUDDOIDPM` | Capsaicin | 2 | 2 | 5.62 | False | Inactive (0) | no |
| `ZSYPIPFQOQGYHH` | norartocarpetin | 2 | 1 | 4.85 | False | Inactive (0) | no |
| `PANKHBYNKQNAHN` | Crocetin|carotenoid aglycone (crocetin) | 2 | 1 | 4.55 | False | Inactive (0) | no |
| `QWCNQXNAFCBLLV` | Falcarindiol | 2 | 1 | 4.18 | False | Inactive (0) | no |
| `SFLMUHDGSQZDOW` | Coniferin|beta-Amyrin | 2 | 1 | 4.12 | False | Inactive (0) | no |
| `GLEVLJDDWXEYCO` | Trolox | 1 | 1 | 6.89 | False | Active (1) | no |
| `MDKGKXOCJGEUJW` | Suprofen | 1 | 1 | 6.25 | False | Active (1) | no |
| `VLEUZFDZJKSGMX` | Pterostilbene | 1 | 1 | 6.16 | False | Active (1) | no |
| `PDHAOJSHSJQANO` | Oxyresveratrol | 1 | 1 | 5.85 | False | Inactive (0) | no |
| `ITDYPNOEEHONAH` | Methyl-epigallocatechin | 1 | 2 | 5.20 | False | Inactive (0) | no |
| `RSYUFYQTACJFML` | Epiafzelechin | 1 | 2 | 5.01 | False | Inactive (0) | no |
| `FAKRSMQSSFJEIM` | captopril | 1 | 1 | 4.77 | False | Inactive (0) | no |
| `SUTUBQHKZRNZRA` | Eugenin | 1 | 1 | 4.75 | False | Inactive (0) | no |
| `YNVJOQCPHWKWSO` | Pallidol | 1 | 1 | 4.30 | False | Inactive (0) | no |
| `UWQYBLOHTQWSQD` | Mulberrin | 1 | 1 | 4.21 | False | Inactive (0) | no |
| `RAKJVIPCCGXHHS` | osthenol | 1 | 1 | 4.19 | False | Inactive (0) | no |
| `ILRCGYURZSFMEG` | Salidroside | 1 | 1 | 4.14 | False | Inactive (0) | no |

#### COX-2 Flora Labeled Molecules (CHEMBL230)

| InChIKey Connectivity | Compound Name | Plants in MPBD | ChEMBL Records | Median pChEMBL | Conflict T=6 | Label T=6 | Common Flora (>=20 plants) |
|---|---|---|---|---|---|---|---|
| `REFJWTPEDVJJIY` | Quercetin|Quercitin|quercetin | 66 | 1 | 4.54 | False | Inactive (0) | YES |
| `PFTAWBLQPZVEMU` | (+)-Catechin|(+)-catechin|(-)-Catechin|(-)-Epicatechin|(-)-epicatechin|(?)-Epicatechin|3-Methyl-2-buten-1-OL|Catechin|Catechin [ Recheck plz]|Catechin hydrate|Cianidanol|Epicatechin|catechin|epicatechin | 33 | 1 | 4.03 | False | Inactive (0) | YES |
| `MIJYXULNPSFWEK` | 3-Epioleanolic acid|OLEANOLIC ACID|Olean-12-en-28-oic acid, 3,21-dihydroxy-, (3beta,21beta)-|Oleanolic acid|oleanic acid|oleanolic acid|trans-2-Icosenoic acid | 31 | 1 | 4.06 | False | Inactive (0) | YES |
| `KZNIFHPLKGYRTM` | Apigenin|apigenin | 29 | 1 | 5.10 | False | Inactive (0) | YES |
| `WCGUUGGRBIKTOS` | Ursolic acid|ursolic acid | 17 | 1 | 4.07 | False | Inactive (0) | no |
| `YQUVCSBJEUQKSH` | 3,4-Dihydroxy Benzoic Acid|3,4-Dihydroxybenzoic acid|3,4-Dihydroxybenzoic acid (Protocatechuic acid)|3,4-dihydroxybenzoic acid|Protocatechuic acid|protocatechuic acid | 16 | 1 | 4.59 | False | Inactive (0) | no |
| `PCMORTLOPMLEFB` | Sinapic acid|Sinapinic acid|sinapic acid | 10 | 1 | 4.55 | False | Inactive (0) | no |
| `LUKBXSAWLPMMSZ` | Resveratrol | 4 | 7 | 5.30 | True | Conflict | no |
| `VFLDPWHFBUODDF` | Curcumin|curcumin|diferuloylmethane | 4 | 2 | 4.53 | False | Inactive (0) | no |
| `MBRLOUHOWLUMFF` | Osthol|Osthole|osthol|osthole | 4 | 1 | 4.09 | False | Inactive (0) | no |
| `IBGBGRVKPALMCQ` | Protocatechualdehyde|Protocatechuic aldehyde|protocatecuic aldehyde | 3 | 1 | 4.71 | False | Inactive (0) | no |
| `PREBVFJICNPEKM` | Bisdemethoxycurcumin|bisdemethoxycurcumin|bisdemothxycurcumin|di-p-coumaroylmethane | 3 | 1 | 4.44 | False | Inactive (0) | no |
| `QBLQLKNOKUHRCH` | Steppogenin|steppogenin | 3 | 1 | 4.33 | False | Inactive (0) | no |
| `LHPRYOJTASOZGJ` | moracin M | 2 | 1 | 4.65 | False | Inactive (0) | no |
| `RTIXKCRFFJGDFG` | Chrysin | 2 | 1 | 4.59 | False | Inactive (0) | no |
| `KTEXNACQROZXEV` | Parthenolide | 1 | 1 | 6.10 | False | Active (1) | no |
| `GLEVLJDDWXEYCO` | Trolox | 1 | 2 | 5.85 | True | Conflict | no |
| `VLEUZFDZJKSGMX` | Pterostilbene | 1 | 2 | 5.65 | False | Inactive (0) | no |
| `KVVSCMOUFCNCGX` | 5-Pentadecylresorcinol | 1 | 1 | 5.63 | False | Inactive (0) | no |
| `MDKGKXOCJGEUJW` | Suprofen | 1 | 1 | 5.56 | False | Inactive (0) | no |
| `IXELFRRANAOWSF` | E-Ajoene|Z-Ajoene | 1 | 1 | 5.47 | False | Inactive (0) | no |
| `FAKRSMQSSFJEIM` | captopril | 1 | 1 | 4.92 | False | Inactive (0) | no |
| `SUTUBQHKZRNZRA` | Eugenin | 1 | 1 | 4.70 | False | Inactive (0) | no |
| `RSYUFYQTACJFML` | Epiafzelechin | 1 | 1 | 4.16 | False | Inactive (0) | no |
| `YNVJOQCPHWKWSO` | Pallidol | 1 | 1 | 4.10 | False | Inactive (0) | no |

---

## 4. Go/No-Go Decision Table (Design Note Section 9)

Evaluation against the Section 9 threshold of **~1,000 labeled training molecules** at **T = 6**:

| Target | ChEMBL ID | Threshold Criterion | Training Pool Labeled Layers (T=6) | Actives (T=6) | Active Fraction (T=6) | Status |
|---|---|---|---|---|---|---|
| **COX-1** | `CHEMBL221` | >= 1,000 labeled layers | 1,458 | 325 | 22.3% | **PASS** |
| **COX-2** | `CHEMBL230` | >= 1,000 labeled layers | 4,122 | 2,319 | 56.3% | **PASS** |
