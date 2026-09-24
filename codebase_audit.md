# BMPPD Thesis — Comprehensive Codebase Audit & System State Report

**Audit Date**: 2026-09-24  
**Project**: Phytochemical Data Pipeline for Bangladeshi Medicinal Plants  
**Repository Root**: `F:\bmppd-thesis`  
**Current Pipeline Milestone**: **Stage 8A Completed** (MPBD Plant Detail-Page Scraping & Traditional-Use Data Extraction)

---

## 1. Executive Summary

This repository hosts a multi-stage bio-computational pipeline designed to systematically cross-reference medicinal plant enumerations from the **Medicinal Plants of Bangladesh (MPBD)** database with bioactive phytochemical compound records from the **Bioactive Medicinal Plants Phytochemical Database (BMPPD)**.

The pipeline adheres to strict research reproducibility standards:
1. **Defensive, polite web scraping**: Full `robots.txt` compliance, rate limiting (1.0s–1.5s delays), and SHA-256 local HTML disk caching.
2. **Dataset immutability**: The master MPBD plant index (916 records) is cryptographically frozen via SHA-256 (`0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7`).
3. **Deterministic query resolution**: Syntactic decomposition of botanical author authority strings allows MPBD botanical binomials to query BMPPD successfully without scientific ambiguity or parent-binomial fallback leakage.
4. **Zero-loss provenance tracking**: Every compound record in the consolidated dataset traces deterministically from `plant_index → source_query → bmpdd_query_name → source_page_url`.
5. **Zero-failure operational state**: All 916 MPBD plants have been queried against BMPPD and all 916 detail pages have been retrieved from MPBD with **0 fetch failures, 0 parse failures, and 0 failed plants remaining**.

---

## 2. Complete Repository File & Folder Inventory

```
F:\bmppd-thesis\
│
├── requirements.txt
├── codebase_audit.md
│
├── scrapers/
│   ├── mpbd_scraper.py
│   ├── mpbd_detail_scraper.py
│   ├── mpbd_normalizer.py
│   ├── mpbd_name_structure_analyzer.py
│   ├── sitemap_parser.py
│   ├── bmppd_scraper.py
│   ├── bmppd_query_compat_pilot.py
│   ├── bmppd_query_compat_20.py
│   ├── bmppd_query_dispatch_validation.py
│   ├── bmppd_query_resolver.py
│   ├── bmppd_bulk_scraper.py
│   └── cache/
│       ├── index.csv
│       ├── robots.txt
│       ├── mpbd/
│       │   ├── index.csv
│       │   ├── backfill_notes.csv
│       │   └── *.html (93 files)
│       ├── mpbd_details/
│       │   ├── index.csv
│       │   └── *.html (917 production cache files: 916 detail pages + pharmacology)
│       └── bmppd/
│           ├── index.csv
│           ├── robots.txt
│           └── *.html (916 production files + pilot files)

│
└── data/
    ├── raw/
    │   ├── mpbd/
    │   │   ├── mpbd_plant_index.csv
    │   │   ├── mpbd_dataset_manifest.json
    │   │   └── archive/
    │   │       ├── mpbd_plant_index_pilot.csv
    │   │       ├── mpbd_plant_index_pages1_5.csv
    │   │       ├── mpbd_plant_index_pages1_20.csv
    │   │       └── mpbd_plant_index_pages21_21.csv
    │   ├── mpbd_details/
    │   │   ├── mpbd_detail_url_map.csv
    │   │   ├── mpbd_disease_vocabulary.csv
    │   │   └── mpbd_plant_details_raw.csv
    │   └── bmppd/
    │       ├── bmppd_compounds_raw.csv
    │       ├── bmppd_failed_plants.csv
    │       ├── bmppd_pilot.csv
    │       └── bmppd_pilot_qc.csv
    │
    ├── processed/
    │   ├── mpbd/
    │   │   ├── mpbd_plant_index_normalized.csv
    │   │   ├── mpbd_botanical_reconciliation.csv
    │   │   ├── mpbd_family_normalization.csv
    │   │   ├── mpbd_reconciliation_manifest.json
    │   │   ├── mpbd_bmppd_query_map.csv
    │   │   └── bmppd_query_overrides.csv
    │   └── mpbd_details/
    │       └── mpbd_disease_terms_long.csv
    │
    ├── attrition/
    │   ├── mpbd_attrition.csv
    │   ├── mpbd_detail_attrition.csv
    │   └── bmppd_attrition.csv
    │
    └── quality/
        ├── mpbd_quality_report.md
        ├── mpbd_reconciliation_report.md
        ├── mpbd_detail_scrape_report.md
        ├── mpbd_query_candidate_analysis.csv
        ├── mpbd_query_candidate_analysis.md
        ├── mpbd_infraspecific_review.csv
        ├── bmppd_query_compatibility_pilot.csv
        ├── bmppd_query_compatibility_pilot.md
        ├── bmppd_query_compatibility_20.csv
        ├── bmppd_query_compatibility_20.md
        ├── bmppd_query_dispatch_validation.csv
        ├── bmppd_query_dispatch_validation.md
        ├── bmppd_query_resolution_policy.md
        ├── bmppd_scrape_summary.md
        ├── bmppd_stage6g_1_20_report.md
        ├── bmppd_full_scrape_failure_report.md
        ├── bmppd_full_scrape_report.md
        └── bmppd_plant_level_summary.csv
```

---

## 3. Detailed File Catalog & Purpose

### 3.1 Root Configuration
- **`requirements.txt`**: Minimal, lightweight dependencies (`requests>=2.32,<3`, `beautifulsoup4>=4.12,<5`). Uses standard library for everything else.
- **`codebase_audit.md`**: Architectural log and codebase audit documentation.

### 3.2 Scrapers & Pipeline Code (`scrapers/`)
- **`scrapers/mpbd_scraper.py`** (Stages 2–3):
  - Fetches and parses all 93 pagination pages of `https://mpbd.cu.ac.bd/plants.php`.
  - Implements SHA-256 URL hashing, local caching in `scrapers/cache/mpbd/`, provenance index tracking, rate limiting, and defensive robots checking.
- **`scrapers/mpbd_normalizer.py`** (Stage 4):
  - Layer A: Cleans whitespace, trims formatting, normalizes botanical families.
  - Layer B: Botanical reconciliation flagging orthographic variants, homotypic duplicates, and taxonomic synonyms across MPBD. Enforces raw master SHA-256 immutability before execution.
- **`scrapers/mpbd_name_structure_analyzer.py`** (Stage 6C):
  - Performs offline AST-style syntactic parsing of all 916 MPBD botanical scientific names. Categorizes names into 6 structural groups (simple binomials, parenthetical authorities, multi-author, infraspecific vars/subspecies, and complex review cases).
- **`scrapers/sitemap_parser.py`** (Stage 1):
  - XML sitemap discovery utility for BMPPD via `robots.txt` and recursive `<urlset>` extraction.
- **`scrapers/bmppd_scraper.py`** (Stage 1 Pilot):
  - Single-query prototype scraper for BMPPD (`Azadirachta indica`). Defines DOM table extraction logic, column header detection, PubChem CID extraction, and QC validation flags.
- **`scrapers/bmppd_query_compat_pilot.py`** (Stage 6B Pilot 1):
  - Comparative harness evaluating raw MPBD query strings vs. stripped binomial candidates across plants 1–5.
- **`scrapers/bmppd_query_compat_20.py`** (Stage 6B Pilot 2):
  - Evaluated query compatibility across plants 1–20 to establish query mismatch prevalence.
- **`scrapers/bmppd_query_dispatch_validation.py`** (Stage 6D):
  - Stratified live validation engine testing 52 representative plants across all syntactic categories to verify clean candidate safety without false positive collisions.
- **`scrapers/bmppd_query_resolver.py`** (Stage 6E):
  - The deterministic production query resolution engine. Reads the frozen MPBD master, applies syntactic stripping rules and the manual override table (`bmppd_query_overrides.csv`), and generates the master query map (`mpbd_bmppd_query_map.csv`).
- **`scrapers/bmppd_bulk_scraper.py`** (Stage 6F, 6G, 6H):
  - The full production bulk scraper for BMPPD.
  - Accepts `--plants START-END`, `--full`, `--cache-only`, `--retry-failed`.
  - Dispatches queries strictly using `bmpdd_query_name` from the query map while retaining the frozen MPBD name as `source_query`.
  - Directs raw HTML into `scrapers/cache/bmppd/`, logs query-level audit rows to `data/attrition/bmppd_attrition.csv`, extracts compound rows into `data/raw/bmppd/bmppd_compounds_raw.csv`, and manages `data/raw/bmppd/bmppd_failed_plants.csv`.

### 3.3 Raw Datasets (`data/raw/`)
- **`data/raw/mpbd/mpbd_plant_index.csv`** (FROZEN MASTER):
  - Exactly 916 records across 93 pages.
  - Columns: `page_number`, `plant_index`, `scientific_name`, `synonym`, `family`.
  - SHA-256: `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7`.
- **`data/raw/mpbd/mpbd_dataset_manifest.json`**:
  - Cryptographic verification manifest recording page count, plant count, generation timestamp, and SHA-256 hash.
- **`data/raw/mpbd/archive/`**:
  - Development stage baselines (`mpbd_plant_index_pilot.csv`, `mpbd_plant_index_pages1_5.csv`, `mpbd_plant_index_pages1_20.csv`, `mpbd_plant_index_pages21_21.csv`).
- **`data/raw/bmppd/bmppd_compounds_raw.csv`** (PRODUCTION COMPOUND DATASET):
  - **24,001 compound records** extracted from BMPPD across all 916 plants.
  - Columns: `plant_index`, `source_query`, `bmpdd_query_name`, `plant_name_extracted`, `common_name`, `compound_name`, `pubchem_cid`, `reference_link`, `source_page_url`, `scrape_timestamp`, `quality_flags`.
- **`data/raw/bmppd/bmppd_failed_plants.csv`**:
  - Tracks persistent scrape failures. Currently contains **0 failed plants** (header only).
- **`data/raw/bmppd/bmppd_pilot.csv` & `bmppd_pilot_qc.csv`**:
  - Stage 1 pilot artifacts from initial single-plant testing.

### 3.4 Processed Datasets (`data/processed/mpbd/`)
- **`data/processed/mpbd/mpbd_plant_index_normalized.csv`**:
  - 916 records with standardized whitespace, family reconciliation, and normalized strings.
- **`data/processed/mpbd/mpbd_botanical_reconciliation.csv`**:
  - 916 records with reconciliation categories (`UNIQUE_VALID`, `HOMOTYPIC_VARIANT`, `POTENTIAL_DUPLICATE`).
- **`data/processed/mpbd/mpbd_family_normalization.csv`**:
  - Audit of botanical family orthographic standardizations (e.g., Fabaceae / Leguminosae).
- **`data/processed/mpbd/mpbd_reconciliation_manifest.json`**:
  - Stage 4 normalization provenance and SHA-256 verification log.
- **`data/processed/mpbd/bmppd_query_overrides.csv`**:
  - 12 manually curated override mappings for complex hybrid/author strings that cannot be safely regex-parsed.
- **`data/processed/mpbd/mpbd_bmppd_query_map.csv`**:
  - Master deterministic dispatch table (916 rows) mapping each `plant_index` to its `source_scientific_name`, `cleaned_candidate`, `bmpdd_query_name`, `resolution_method`, `syntactic_category`, and `dispatch_action`.

### 3.5 Attrition & Audit Logs (`data/attrition/`)
- **`data/attrition/mpbd_attrition.csv`**:
  - Audit log for all 93 MPBD pagination requests (status code, parse counts, timestamp).
- **`data/attrition/bmppd_attrition.csv`**:
  - Cumulative audit trail for every BMPPD query dispatch (includes attempt indices, HTTP response codes, latency, extracted compound count, cache hit flags).

### 3.6 Quality Reports & Diagnostic Audits (`data/quality/`)
- **`bmppd_full_scrape_report.md`**: Comprehensive final audit report for Stage 6H covering all 916 plants, yield metrics, PubChem CID coverage, and top plant yields.
- **`bmppd_plant_level_summary.csv`**: Per-plant tabular summary (916 rows) detailing for every plant: `plant_index`, `source_query`, `bmpdd_query_name`, `status`, `row_count`, `valid_cid_count`, `missing_cid_count`, and `source_page_url`.
- **`bmppd_full_scrape_failure_report.md`**: Intermediate diagnostic report documenting the 105 transient upstream 503/timeout failures during Stage 6H's first pass and validating the retry strategy.
- **`bmppd_stage6g_1_20_report.md`**: Validation report for Stage 6G (plants 1–20).
- **`mpbd_query_candidate_analysis.csv` & `.md`**: Syntactic classification analysis of all 916 MPBD names.
- **`bmppd_query_dispatch_validation.csv` & `.md`**: 52-sample live validation results.
- **`mpbd_infraspecific_review.csv`**: Botanical analysis of all 10 infraspecific varieties/subspecies.
- **`bmppd_query_resolution_policy.md`**: Formal architectural specification of the Stage 6E query resolution policy.
- **`mpbd_quality_report.md` & `mpbd_reconciliation_report.md`**: Stage 3 and Stage 4 quality audit logs.

### 3.7 Local HTML Cache (`scrapers/cache/`)
- **`scrapers/cache/mpbd/`**: 93 cached raw HTML pages from `mpbd.cu.ac.bd` + `index.csv`.
- **`scrapers/cache/bmppd/`**: **916 cached raw HTML pages** from `bmppd.org` corresponding to all 916 resolved plant queries + cache `index.csv` + `robots.txt`.

---

## 4. Current Pipeline State & Metrics (Stage 6H Complete)

### 4.1 Master Inventory Status
| Metric | Value | Notes |
| :--- | :--- | :--- |
| **Total MPBD Master Plants** | **916** | Frozen master inventory |
| **Plants Processed** | **916 / 916 (100.0%)** | All indices 1–916 dispatched |
| **Cached HTML Responses** | **916** | 100% locally archived in `scrapers/cache/bmppd/` |
| **Successful Plants with Compounds (PASS)** | **222 (24.24%)** | Returned $\ge 1$ compound row |
| **Zero-Result Plants (ZERO_RESULTS)** | **694 (75.76%)** | Valid botanical searches returning 0 compounds |
| **Failed Plants (FETCH_FAILED / PARSE_FAILED)**| **0 (0.00%)** | **Zero active failures** |
| **Total Compounds Extracted** | **24,001** | Total raw compound instances |
| **Unique Compound-Plant Rows** | **24,001** | 0 duplicates across the dataset |
| **Provenance Integrity** | **100.0%** | 0 mismatches across all 24,001 rows |

### 4.2 PubChem CID Coverage
| PubChem CID Classification | Count | Percentage |
| :--- | :--- | :--- |
| **Valid Numeric PubChem CID** | 17,716 | **73.81%** |
| **Missing / Null PubChem CID** | 6,285 | **26.19%** |
| *Total Compound Rows* | *24,001* | *100.0%* |

*(Note: All 6,285 rows with missing CIDs have been flagged with `missing_pubchem_cid` in `quality_flags` for Stage 7 cross-referencing).*

### 4.3 Top 10 Compound Yield Plants in Bangladesh Flora
1. **Citrus reticulata** (Plant 70): 708 compounds (708 valid CIDs)
2. **Hibiscus sabdariffa** (Plant 497): 656 compounds (656 valid CIDs)
3. **Citrus maxima** (Plant 687): 579 compounds (544 valid CIDs)
4. **Cyperus rotundus** (Plant 619): 578 compounds (578 valid CIDs)
5. **Mangifera indica** (Plant 407): 577 compounds (576 valid CIDs)
6. **Morus alba** (Plant 162): 542 compounds (541 valid CIDs)
7. **Cinnamomum camphora** (Plant 494): 523 compounds (523 valid CIDs)
8. **Allium cepa** (Plant 30): 480 compounds (478 valid CIDs)
9. **Camellia sinensis** (Plant 638): 455 compounds (455 valid CIDs)
10. **Aegle marmelos** (Plant 736): 442 compounds (442 valid CIDs)

---

## 5. Stage 7A: Chemical Structure Resolution, Standardization & ChEMBL Bioactivity Feasibility

**Execution Date**: 2026-09-24  
**Status**: **Stage 7A Completed** (Scripts 01, 02, and 03 fully executed, validated, and reconciled).

### 5.1 Pipeline Script 01: Chemical Structure Resolution (`pipeline/01_resolve_structures.py`)
- **Objective**: Resolve chemical structures (SMILES, InChI, InChIKey) for all 24,001 raw plant-compound rows via PubChem PUG-REST API.
- **Cache Architecture**: Complete local JSON disk caching (`data/cache/pubchem/cids/` and `data/cache/pubchem/names/`). Warm rerun yields **100% cache hit rate (0 network calls)** in <3 seconds.
- **Results**:
  - `CID-based`: 17,716 rows (73.81%)
  - `exact_match`: 4,789 rows (19.95%)
  - `multiple_matches`: 133 rows (0.55%)
  - `no_match`: 1,055 rows (4.40%)
  - `skipped_encoding_loss`: 295 rows (1.23%)
  - `skipped_nonspecific`: 13 rows (0.05%)
  - `fetch_error`: 0 rows (0.00%)
- **Outputs**:
  - `data/processed/compounds/compound_structures_resolved.csv`
  - `data/quality/no_match_high_frequency.csv`
  - `data/quality/stage7a_resolution_report.md`

### 5.2 Pipeline Script 02: Chemical Structure Standardization (`pipeline/02_standardize_structures.py`)
- **Objective**: Standardize chemical structures via RDKit (Largest fragment desalting -> Neutralization/uncharging -> Tautomer canonicalization -> Flat stereochemistry stripping).
- **Multiple-Match Rule**: Candidate sets evaluated at 14-char connectivity layer after desalting; 131 of 133 candidate sets accepted as flat structures (`stereo_resolved = False`).
- **Results**:
  - **Successfully Linked Rows**: **22,614 / 24,001 (94.22%)**
  - **Dropped / Unresolved Rows**: **1,387 / 24,001 (5.78%)**
  - **Exact Reconciliation**: `Linked (22,614) + Dropped (1,387) == 24,001` (0 orphan links; assertion passed).
  - **True Unique Molecule Inventory**: **7,317 unique 14-character connectivity layers** (6,770 stereo-resolved; 547 stereo-unresolved).
  - **Curated Drug-Like Organic Subset**: **7,228 molecules (98.8%)** (excluding inorganic, metals, mixtures, <5 heavy atoms, >100 heavy atoms).
  - **Botanical Coverage**: 222 / 222 plants (100.0%) retained at least one standardized molecule.
- **Outputs**:
  - `data/processed/compounds/compounds_unique.csv`
  - `data/processed/compounds/plant_compound_links.csv`
  - `data/processed/compounds/compounds_dropped.csv`
  - `data/attrition/structure_standardization_attrition.csv`
  - `data/quality/stage7a_standardization_report.md`

### 5.3 Pipeline Script 03: ChEMBL Label Feasibility Check (`pipeline/03_chembl_label_coverage.py`)
- **Objective**: Cross-reference the 7,317 standardized Bangladeshi medicinal plant molecules against the ChEMBL 37 SQLite database in read-only mode to assess ML label feasibility.
- **Cache Architecture**: Pre-computed 14-character connectivity lookup table cached at `data/cache/chembl/chembl37_connectivity_lookup.csv` (2,897,819 structures loaded in 1.24s).
- **Results**:
  - **ChEMBL Structure Match Rate**: **3,263 / 7,317 molecules (44.59%)** match at connectivity level (**3,207 / 7,228 (44.37%)** in curated drug-like subset).
  - **Natural Product Validation**: 3,039 of matched molecules (93.1%) flagged as `natural_product = 1` in ChEMBL.
  - **Activity Records Extracted**: 389,846 raw activity records -> **38,352 USABLE binding/functional records** (`=`, `nM`, IC50/Ki/Kd/EC50) -> **11,504 STRICT records** (single-protein target, confidence 8–9, assay type B/F).
  - **Molecule-Level Label Coverage**:
    - Any activity record: 3,064 molecules (41.9%)
    - Usable activity record: 1,581 molecules (21.6%)
    - Strict activity record: 1,083 molecules (14.8%)
  - **Top Single Targets**: Carbonic anhydrase 12 (70 molecules), PTP1B (63 molecules), CA2 (62 molecules), CA9 (60 molecules), CA1 (58 molecules), CA7 (55 molecules), AKR1B1 (55 molecules), AChE (54 molecules). Single-target datasets have <200 molecules (high sparsity).
  - **Global Feasible ML Tasks (>= 1,000 labeled molecules)**:
    1. Active against ANY single protein target at pChEMBL >= 6 (Strict): **1,083 labeled molecules** (495 active, 588 inactive).
    2. Any usable activity record exists in ChEMBL: **3,263 labeled molecules** (1,581 active/functional, 1,682 untested/inactive).
  - **Botanical Coverage**: 215 of 222 medicinal plants (96.8%) have $\ge 1$ molecule with strict/usable bioactivity data.
- **Outputs**:
  - `data/processed/compounds/compound_chembl_match.csv`
  - `data/processed/compounds/compound_bioactivity_raw.csv`
  - `data/attrition/chembl_matching_attrition.csv`
  - `data/quality/label_feasibility_report.md`

### 5.4 Scraper & Pipeline Script: Stage 8A Traditional-Use Data Extraction (`scrapers/mpbd_detail_scraper.py`)
- **Objective**: Retrieve and systematically extract traditional medicinal uses, disease indications, vernacular nomenclature, and botanical details from the detail pages (`details.php?id=N`) of all 916 MPBD medicinal plants.
- **Cache Architecture**: Dedicated SHA-256 hashed HTML disk cache at `scrapers/cache/mpbd_details/` (917 production HTML files, tracking via `index.csv` ledger).
- **Execution & Politeness**:
  - `robots.txt` compliance: HTTP 404 (RFC 9309 compliant, unrestricted public access).
  - Rate limiting: 1.0s–1.5s randomized delays between live HTTP requests.
  - Frozen master MPBD SHA-256 integrity check verified at start and finish: `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7`.
- **Key Findings & Results**:
  - **Zero Fetch / Parse Failures**: 916 / 916 plants (100.0%) successfully retrieved and parsed.
  - **Site ID Alignment**: Detail site IDs span `4` to `925` (6 gaps: 92, 93, 199, 355, 582, 828, corresponding to 5 list-page duplicate entries + 1 omitted database ID). Zero duplicate site IDs in master alignment.
  - **Field Completeness**: 100.0% of all 916 plants (and 100.0% of the 222 compound plants) possess populated `disease_raw` and `uses_raw` fields.
  - **Botanical Consistency**: 0 botanical name mismatches (`name_mismatch`) and 0 family mismatches (`family_mismatch`).
  - **Upstream Data Anomalies Documented**:
    - Greek letter encoding loss confirmed upstream: literal `0x3F` (`?`) bytes in server HTTP responses (e.g. `?-cymene`).
    - Upstream MySQL `VARCHAR(255)` database schema truncation in `Chemical Constituents` (e.g. terminating at 255 chars).
    - `dictionary.php` returned HTTP 404; `pharmacology.php` contains a 47-page paginated glossary.
  - **Disease Term Extraction**: 6,512 total term instances extracted into long format (`term_raw`, `term_light`), yielding 1,526 distinct light terms.
- **Outputs**:
  - `data/raw/mpbd_details/mpbd_detail_url_map.csv` (916 rows)
  - `data/raw/mpbd_details/mpbd_disease_vocabulary.csv` (12 rows)
  - `data/raw/mpbd_details/mpbd_plant_details_raw.csv` (916 rows)
  - `data/processed/mpbd_details/mpbd_disease_terms_long.csv` (6,512 rows)
  - `data/attrition/mpbd_detail_attrition.csv` (936 rows)
  - `data/quality/mpbd_detail_scrape_report.md` (comprehensive audit report)

### 5.5 Pipeline Script 04: COX Go/No-Go Data Check (`pipeline/04_cox_data_check.py`)
- **Objective**: Conduct read-only activity counting and target validation across ChEMBL 37 for primary (COX-1, COX-2) and exploratory (Xanthine Oxidase, MAO-A) human single-protein targets after removing flora molecules, per `docs/thesis_design_note.md` Section 9.
- **Constraints & Compliance**:
  - ChEMBL 37 SQLite database opened strictly read-only (`mode=ro`).
  - Master MPBD SHA-256 integrity verified at start and end: `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7`.
  - No model training, no scaffold splitting, no changes to design note thresholds or rules.
- **Filtering & Labeling Rules Applied (Design Note Section 5)**:
  - `standard_relation = '='`, `standard_units = 'nM'`, `standard_type IN ('IC50', 'Ki', 'Kd', 'EC50')`.
  - `potential_duplicate = 0`, `data_validity_comment IS NULL`, `pchembl_value IS NOT NULL`.
  - Assays: `assay_type IN ('B', 'F')`, `confidence_score IN (8, 9)`, `assays.tid = target.tid`.
  - Aggregation: Median pChEMBL per 14-char InChIKey connectivity layer.
  - Conflict rule: `(min < T and max >= T) AND (max - min) > 1.0` log unit. Excluded from labeled set.
  - Partitioning: Training pool vs Flora external set by 14-char InChIKey connectivity layer.
- **Go/No-Go Findings (T=6 threshold: ~1,000 labeled layers)**:
  - **COX-1 (CHEMBL221, tid 96)**: 1,458 labeled training layers (325 active, 1,133 inactive, 22.3% active fraction, 35 conflicts excluded) -> **PASS**.
  - **COX-2 (CHEMBL230, tid 126)**: 4,122 labeled training layers (2,319 active, 1,803 inactive, 56.3% active fraction, 126 conflicts excluded) -> **PASS**.
  - **Xanthine Oxidase (CHEMBL1929, tid 149)**: 611 labeled training layers (372 active, 239 inactive, 60.9% active fraction, 9 conflicts excluded).
  - **MAO-A (CHEMBL1951, tid 86)**: 2,914 labeled training layers (748 active, 2,166 inactive, 25.7% active fraction, 32 conflicts excluded).
- **Outputs**:
  - `data/processed/modeling/cox_datacheck_labels_cox1.csv` (1,525 rows)
  - `data/processed/modeling/cox_datacheck_labels_cox2.csv` (4,273 rows)
  - `data/processed/modeling/cox_datacheck_labels_xo.csv` (650 rows)
  - `data/processed/modeling/cox_datacheck_labels_maoa.csv` (2,989 rows)
  - `data/quality/cox_data_check_report.md`
  - `data/attrition/cox_data_check_attrition.csv`

### 5.6 Stage 7A-1: Provenance Audit & Domain-Shift Diagnostics (`pipeline/05_provenance_and_domain_diagnostics.py`)
- **Objective**: Conduct rigorous provenance audit of 100 flora-labeled molecules across human COX-1, COX-2, XO, and MAO-A, evaluate chemical identity consistency across all 7,317 flora layers, and quantify domain shift between flora and ChEMBL training pools.
- **Constraints & Compliance**:
  - ChEMBL 37 opened strictly read-only (`mode=ro`).
  - Master MPBD SHA-256 integrity verified at start and end: `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7`.
  - Zero model training, zero network calls, zero data deletions.
- **Key Findings**:
  - **Provenance Review (100 Labeled Flora Layers)**: 32 layers flagged (`review_flag = True` for `natural_product = 0` OR `max_phase >= 1`).
    - Identified synthetic positive-control drug contamination from source literature into BMPPD: Trolox (antioxidant assay standard), Suprofen (synthetic NSAID control), and Captopril (synthetic ACE inhibitor control).
    - Pinpointed upstream CID typo in BMPPD for Plant 730 (*Ardisia solanacea*): labeled as `beta-Amyrin` but assigned CID 73171 (*coniferin glucoside derivative*), collapsing into coniferin layer `SFLMUHDGSQZDOW`.
  - **Identity Consistency (7,317 Layers)**: 1,796 layers have $\ge 2$ distinct names (830 in Group (i) stereo/case/trivial variants; 966 in Group (ii) discordant/different compound names).
  - **ChEMBL NP Status (3,263 Matched Flora Layers)**: 224 layers have `natural_product = 0` (strictly synthetic in ChEMBL), and 22 of those have `max_phase >= 1` (approved/investigational drugs).
  - **Domain Shift**:
    - Labeled flora nearest-neighbour Tanimoto similarities to training pools (median 0.457–0.555) are drastically lower than training pool leave-one-out self-similarity (median 0.745–0.785).
    - Only 7.7%–12.7% of all 7,317 flora molecules share an analogue with $NN \ge 0.4$ in the ChEMBL training pools.
- **Outputs**:
  - `data/processed/modeling/flora_provenance_review.csv` (100 rows)
  - `data/quality/provenance_and_domain_report.md`

### 5.7 Stage 7A-2: Link-Confidence Audit & In-Domain Power Check
- **Objective**: Conduct systematic name-versus-structure agreement audit for every plant-compound link (22,614 rows), classify link confidence into tiers (HIGH, MEDIUM, LOW), recalibrate labeled flora external sets after purging confirmed collisions, identify literature reference-compound candidates with clean DOIs, and execute an in-domain statistical power check across all 222 compound plants stratified by pain/inflammation indications.
- **Constraints & Compliance**:
  - `docs/thesis_design_note.md` adhered to as primary authority.
  - ChEMBL 37 opened strictly read-only (`mode=ro`).
  - Master MPBD SHA-256 verified at start and end: `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7`.
  - Zero model training, zero dataset modifications to `data/raw/` or existing processed files, zero paper claims made (none read).
- **Key Findings**:
  - **Part A (Link-Confidence Classification)**:
    - **HIGH (20,346 links, 89.97%)**: 15,258 CID synonym matches, 4,789 exact name lookups, 168 name/CID same connectivity, 131 name multi-matches same connectivity.
    - **MEDIUM (1,366 links, 6.04%)**: 1,336 PubChem unresolvable names (mostly misspellings or non-chemical strings), 30 ambiguous multi-matches.
    - **LOW (902 links, 3.99%)**: Confirmed upstream CID/name collisions resolving to different connectivity layers.
  - **Part B (Link Quality & Recalibration)**:
    - 17 of 222 plants lose >50% of links under HIGH-only filtering (e.g., Plant 21 *Benincasa hispida* and Plant 35 *Clitoria ternatea* due to massive upstream CID copy-paste errors).
    - Group (ii) audit of 966 discordant layers: 488 (50.5%) are ALL HIGH (valid chemical synonyms/isomers), 210 (21.7%) contain confirmed LOW collisions, 268 (27.7%) are MEDIUM.
    - Detailed layers: `IQPNAANSBPBGFQ` (Luteolin) has 34 HIGH links and 2 LOW links; `AEDDIBAIWPIIBD` (Mangiferin) has 4 HIGH and 1 LOW; `ZDWSNKPLZUXBPE` (3,5-di-tert-butylphenol) has 4 HIGH and 1 LOW.
    - Part C: 18 reference-compound candidate layers with clean DOIs.
    - Part D: Missing 2 of 7,317 flora layers explained (`JATASMBSXKNAQR` and `ISHQPQZAQICIAZ`).
- **Outputs**:
  - `data/processed/compounds/plant_compound_links_confidence.csv` (22,614 rows)
  - `data/quality/link_confidence_and_power_report.md`
  - `data/cache/pubchem/synonyms_batch_*.json` (142 files, 7,061 unique CIDs)
  - `data/cache/pubchem/names/name_*.json` (1,501 newly cached names)

### 5.8 Stage 7A-3: Corrections to the Link-Confidence Audit
- **Objective**: Implement methodological corrections from expert audit review: (1) Correct the external-set retention rule (drop LOW links, preserve molecules having $\ge 1$ HIGH link); (2) Generate primary literature verification sheet for manual inspection; (3) Reconcile duplicate plant query binomials into plant analysis units; (4) Perform molecular formula audit on LOW-tier links to separate isomer/representation differences from collisions; and (5) Recalibrate plant-level compound yield distributions without describing counts as statistical power.
- **Constraints & Compliance**:
  - `docs/thesis_design_note.md` adhered to as primary authority.
  - Master MPBD SHA-256 verified at start and end: `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7`.
  - Zero model training, zero dataset modifications to existing files, zero network calls, zero paper claims made (none read).
- **Key Findings**:
  - **1. External Set Rule Correction**:
    - Only 3 of 100 labeled flora layers have zero HIGH links across all plants: `ITDYPNOEEHONAH` (1 MED, 0 HIGH, 0 LOW), `SHPPXMGVUDNKLV` (2 LOW, 0 HIGH), and `IBRKLUSXDYATLG` (1 MED, 0 HIGH).
    - Preserved 97 authentic phytochemicals previously dropped in whole-layer purging (luteolin, rutin, hyperoside, catechin, linoleic acid).
    - Recalibrated sets: COX-1 (31 layers: 4 act / 27 inact at T=6; 12 act / 19 inact at T=5); COX-2 (25 layers: 1 act / 22 inact / 2 conflict at T=6; 6 act / 17 inact / 2 conflict at T=5); XO (29 layers: 5 act / 21 inact / 3 conflict at T=6; 15 act / 11 inact / 3 conflict at T=5); MAO-A (42 layers: 12 act / 29 inact / 1 conflict at T=6; 26 act / 15 inact / 1 conflict at T=5).
    - **Trolox & Suprofen Diagnostic Insight**: The link-tier method tests name-vs-CID consistency within the database. It cannot detect literature positive-control contamination (e.g., Trolox or Suprofen) when the paper extractor entered the control drug's name alongside its correct PubChem CID (tier HIGH by construction).
  - **2. Verification Sheet**:
    - Compiled `external_verification_sheet.csv` (519 rows across 84 qualifying layers) with clean DOIs/PMIDs/ISBNs and blank manual review columns (`verified_in_source`, `is_reference_compound`, `notes`).
  - **3. Duplicate Plants & Plant Analysis Units**:
    - Identified 14 duplicate query groups covering 29 plant indices (all with 100% identical compound sets from identical BMPPD query dispatches, but divergent `disease_raw` texts from MPBD).
    - Formulated 207 plant analysis units across the 222 compound plants.
    - Only 16 analysis units lose >50% of links under HIGH-only (AU_021 *Benincasa hispida* was previously double-counted under plants 21 and 765).
  - **4. Molecular Formula Tier Audit**:
    - Formula comparison separates constitutional/stereochemical isomers from true database collisions.
    - Demonstrated that petunidin, peonidin, pelargonidin, curzerene, seychellene, and casuarinin share formulas/skeletons with their CID records, having been flagged due to counter-ion representation or standardization limitations.
  - **5. Plant-Level In-Domain Yield Recalibration**:
    - Computed in-domain compound counts across 207 analysis units (115 pain units, 55.6% vs 92 other units, 44.4%).
    - For COX-1 at $NN \ge 0.4$ under HIGH links: 64 of 115 pain units (55.7%) vs 47 of 92 other units (51.1%) have $\ge 5$ in-domain compounds (a modest 4.6 percentage point difference). Correctly framed as compound yield and chemical space coverage rather than statistical power.
- **Outputs**:
  - `data/processed/modeling/plant_analysis_units.csv` (916 rows)
  - `data/processed/modeling/external_verification_sheet.csv` (519 rows)
  - `data/processed/modeling/tier_sample_audit.csv` (100 rows, random seed 42)
  - `data/quality/stage7a3_corrections_report.md`

---

## 6. Next Stages in the Thesis Pipeline

Following completion of Stage 8A, traditional-use data acquisition is complete across all 916 Bangladeshi medicinal plants. The project is prepared for disease taxonomy mapping, cross-database integration, and downstream modeling:

| Stage | Focus | Planned Objectives |
| :--- | :--- | :--- |
| **Stage 8B** | **Disease Taxonomy Harmonization & Ontology Mapping** | Define standard therapeutic categories (e.g., analgesia, anti-inflammatory, antimicrobial, metabolic) and map the 1,526 distinct disease terms with user validation. |
| **Stage 9** | **Molecular Representation & Feature Engineering** | Compute Morgan / ECFP fingerprints, RDKit 2D physicochemical descriptors, and graph neural representations for the 7,317 unique molecules. |
| **Stage 10** | **Machine Learning Bioactivity Modeling & Ethnobotanical Validation** | Train and evaluate benchmark classifiers (Random Forest, XGBoost, GNNs) on feasible target tasks identified in Stage 7A, and correlate predicted bioactivities with traditional medicinal indications. |

