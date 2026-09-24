# BMPPD Thesis — Comprehensive Codebase Audit & System State Report

**Audit Date**: 2026-09-24  
**Project**: Phytochemical Data Pipeline for Bangladeshi Medicinal Plants  
**Repository Root**: `F:\bmppd-thesis`  
**Current Pipeline Milestone**: **Stage 6H Completed** (Full 916-Plant BMPPD Bulk Scraping & Failure Resolution Complete)

---

## 1. Executive Summary

This repository hosts a multi-stage bio-computational pipeline designed to systematically cross-reference medicinal plant enumerations from the **Medicinal Plants of Bangladesh (MPBD)** database with bioactive phytochemical compound records from the **Bioactive Medicinal Plants Phytochemical Database (BMPPD)**.

The pipeline adheres to strict research reproducibility standards:
1. **Defensive, polite web scraping**: Full `robots.txt` compliance, rate limiting (1.0s–1.5s delays), and SHA-256 local HTML disk caching.
2. **Dataset immutability**: The master MPBD plant index (916 records) is cryptographically frozen via SHA-256 (`0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7`).
3. **Deterministic query resolution**: Syntactic decomposition of botanical author authority strings allows MPBD botanical binomials to query BMPPD successfully without scientific ambiguity or parent-binomial fallback leakage.
4. **Zero-loss provenance tracking**: Every compound record in the consolidated dataset traces deterministically from `plant_index → source_query → bmpdd_query_name → source_page_url`.
5. **Zero-failure operational state**: Following Stage 6H's initial pass and automated retry pass, all 916 MPBD plants have been queried against BMPPD with **0 fetch failures, 0 parse failures, and 0 failed plants remaining**.

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
    │   └── bmppd/
    │       ├── bmppd_compounds_raw.csv
    │       ├── bmppd_failed_plants.csv
    │       ├── bmppd_pilot.csv
    │       └── bmppd_pilot_qc.csv
    │
    ├── processed/
    │   └── mpbd/
    │       ├── mpbd_plant_index_normalized.csv
    │       ├── mpbd_botanical_reconciliation.csv
    │       ├── mpbd_family_normalization.csv
    │       ├── mpbd_reconciliation_manifest.json
    │       ├── mpbd_bmppd_query_map.csv
    │       └── bmppd_query_overrides.csv
    │
    ├── attrition/
    │   ├── mpbd_attrition.csv
    │   └── bmppd_attrition.csv
    │
    └── quality/
        ├── mpbd_quality_report.md
        ├── mpbd_reconciliation_report.md
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

## 5. Next Stages in the Thesis Pipeline

The data acquisition phase of the thesis (Stages 1 through 6) is complete. The project is prepared to transition to data cleaning, compound identity resolution, and analytical bioactivity screening:

| Stage | Focus | Planned Objectives |
| :--- | :--- | :--- |
| **Stage 7** | **PubChem CID Resolution & Chemical Normalization** | Query PubChem PUG-REST API for the 6,285 compounds with missing CIDs using standardized chemical names; resolve canonical SMILES, InChIKeys, and molecular structures. |
| **Stage 8** | **Taxonomic Harmonization & Cross-Database Join** | Integrate POWO (Plants of the World Online) or GBIF to reconcile the 26 MPBD duplicate/synonym groups; join normalized MPBD botanical metadata with normalized BMPPD phytochemical profiles. |
| **Stage 9** | **Bioactivity, Target Prediction & Network Analysis** | Annotate compounds against ChEMBL/BindingDB; evaluate therapeutic indications reported in MPBD against pharmacological targets of identified bioactive metabolites. |
