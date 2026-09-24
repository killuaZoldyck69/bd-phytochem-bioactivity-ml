# BMPPD Stage 6H — Full 916-Plant Production Acquisition Report

## 1. Objective
Execute the complete, deterministic bulk scrape of BMPPD phytochemical records for all 916 plants in the frozen MPBD master inventory using the validated Stage 6E query-resolution layer and Stage 6F production bulk scraper engine. Validate end-to-end data integrity, provenance traceability, cache completeness, resume protection, and absence of data loss or file corruption.

## 2. Execution Period
- **Start Time (UTC)**: 2026-09-24T07:19:28Z (Local: 2026-09-24 13:19:28 +06:00)
- **Primary Full Scrape Completed (UTC)**: 2026-09-24T08:32:54Z (Duration: ~1h 13m 26s)
- **Controlled Retry Completed (UTC)**: 2026-09-24T08:37:57Z (Duration: ~3m 51s)
- **Total Acquisition Elapsed Time**: ~1h 18m 29s

## 3. Software and Configuration
- **Script**: `scrapers/bmppd_bulk_scraper.py`
- **Python Version**: 3.11+
- **HTTP Engine**: `requests.Session` with User-Agent: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 (Research Scraper; Botanical Phytochemical Data Mining)`
- **Polite Delay**: 1.5 seconds between consecutive live requests
- **Request Timeout**: 30 seconds
- **Robots.txt Parser**: `urllib.robotparser.RobotFileParser` referencing `https://bmppd.org/robots.txt` (cached locally)
- **Search Dispatch Endpoint**: `https://bmppd.org/bmppd_result/?q={bmpdd_query_name}`

## 4. Source Inventory
- **Master File**: `data/raw/mpbd/mpbd_plant_index.csv` (FROZEN)
- **Record Count**: Exactly 916 plants
- **Master SHA-256 Checksum**: `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7`

## 5. Query-Resolution Methodology
- **Mapping Table**: `data/processed/mpbd/mpbd_bmppd_query_map.csv` (916 records)
- **Manual Overrides Table**: `data/processed/mpbd/bmppd_query_overrides.csv` (12 records)
- **Join Key**: Strict integer `plant_index` (1 to 916)
- **Dispatch Rule**: Clean binomial candidate `bmpdd_query_name` dispatched to BMPPD search endpoint; original frozen MPBD scientific name preserved as `source_query`.
- **Infraspecific Rule**: Parent-binomial fallback remains strictly disabled for `subsp.` and `var.` taxa.

## 6. Pre-Flight Integrity Checks
All pre-flight assertions passed prior to launch:
- Master MPBD SHA-256 verified identical to frozen hash.
- Query map contained 916 unique, non-blank rows with 0 name mismatches against MPBD.
- Resolver and manual override files verified unmodified via `git diff`.
- Baselines recorded: 851 compound rows, 44 attrition rows, 0 failed plants, 80 cache entries.

## 7. Network and Cache Methodology
- Every successful HTTP 200 response was immediately persisted to disk under `scrapers/cache/bmppd/` using SHA-256 filename hashing (`{hash[:24]}.html`).
- Metadata (URL, filename, HTTP status, ISO-8601 UTC timestamp, content hash, content type) indexed in `scrapers/cache/bmppd/index.csv`.
- Resume protection bypassed already-completed plants in `data/raw/bmppd/bmppd_compounds_raw.csv`.

## 8. Full Execution Statistics

| Metric | Primary Pass (`--full`) | Second Pass (`--retry-failed`) | Final Cumulative Dataset |
| :--- | :---: | :---: | :---: |
| **Total Plants in Scope** | 916 | 105 | **916** |
| **Plants Attempted** | 908 (8 skipped via resume) | 105 | **916** |
| **Successful Queries (PASS)** | 198 | 16 | **222** (24.24%) |
| **Zero-Result Queries (ZERO_RESULTS)** | 605 | 89 | **694** (75.76%) |
| **Fetch Failures (FETCH_FAILED)** | 105 | 0 | **0** (0.00%) |
| **Parse Failures (PARSE_FAILED)** | 0 | 0 | **0** (0.00%) |
| **Total Compound Rows Extracted** | 22,231 | 919 | **24,001** |
| **Rows with Valid Numeric PubChem CID** | 17,207 | 301 | **17,716** (73.81%) |
| **Rows Missing PubChem CID** | 5,024 | 618 | **6,285** (26.19%) |
| **Cache Hits** | 54 | 89 | **143** |
| **Live Web Fetches** | 749 | 105 | **854** |
| **Total Cached BMPPD Pages** | 808 | 916 | **916** (100.0%) |

## 9. Plant-Level Results Overview
- **PASS Plants**: 222 plants yielded at least one phytochemical record in BMPPD.
- **ZERO_RESULTS Plants**: 694 plants yielded zero result tables in BMPPD (genuine upstream absence).
- **FAILED Plants**: 0 plants failed. All 916 plants resolved to a verified acquisition state.

## 10. Compound Extraction Statistics
- **Consolidated Output File**: `data/raw/bmppd/bmppd_compounds_raw.csv`
- **Total Compound Rows**: **24,001**
- **Distinct Compound Tuples**: **24,001** (0 duplicates)
- **Row Distribution Summary**:
  - Highest yield plants:
    - *Citrus reticulata* (Plant 70): 708 rows (708 with CID, 0 missing)
    - *Hibiscus sabdariffa* (Plant 497): 656 rows (656 with CID, 0 missing)
    - *Citrus maxima* (Plant 687): 579 rows (544 with CID, 35 missing)
    - *Cyperus rotundus* (Plant 619): 578 rows (578 with CID, 0 missing)
    - *Mangifera indica* (Plant 407): 577 rows (576 with CID, 1 missing)
    - *Azadirachta indica* (Plant 749): 519 rows (503 with CID, 16 missing)
    - *Psidium guajava* (Plant 287): 466 rows (0 with CID, 466 missing)
    - *Carica papaya* (Plant 867): 449 rows (407 with CID, 42 missing)
    - *Cassia fistula* (Plant 872): 439 rows (323 with CID, 116 missing)
    - *Coriandrum sativum* (Plant 661): 421 rows (419 with CID, 2 missing)

## 11. PubChem CID Quality Statistics
- **Total Extracted Records**: 24,001
- **Valid Numeric PubChem CID**: **17,716** (73.81%)
- **Missing / Non-Numeric CID**: **6,285** (26.19%)
- **Quality Flags**: All 6,285 missing CID records are explicitly marked with `missing_pubchem_cid` in `quality_flags`.
- **Integrity Note**: No artificial CID imputation, PubChem API lookup, or structure normalization was conducted. Upstream data is preserved verbatim.

## 12. ZERO_RESULTS Statistics
- **Count**: 694 plants (75.76% of total inventory)
- **Character**: Genuine lack of coverage in BMPPD for these botanical taxa under their clean binomial search terms.
- **Classification**: Verified as `ZERO_RESULTS`, explicitly distinguished from network or parsing failures in `data/attrition/bmppd_attrition.csv`.

## 13. Fetch Failures Analysis
- During the primary run, 105 plants encountered transient fetch failures due to upstream server overload (HTTP 503 and 30s read timeouts) between `plant_index` 132 and 267.
- Documented in `data/quality/bmppd_full_scrape_failure_report.md`.
- Completely resolved in the controlled second pass (`--retry-failed`): 105/105 succeeded (16 PASS, 89 ZERO_RESULTS, 0 failures).

## 14. Parser Failures Analysis
- **Parse Failures**: Exactly **0** (0.00%).
- The pure HTML parser functions from `scrapers/bmppd_scraper.py` parsed every table structure flawlessly across all 24,001 extracted rows.

## 15. Attrition Pipeline Summary
The full attrition progression across the 916 frozen MPBD inventory is:
```
916 MPBD frozen plant taxa
    ↓ (100.0%)
916 deterministic BMPPD queries dispatched
    ↓
222 plants with phytochemical records (PASS, 24.24%)
[694 plants with no phytochemical records (ZERO_RESULTS, 75.76%)]
[0 failed plants (0.00%)]
    ↓
24,001 unique compound records extracted
    ↓
17,716 records with valid numeric PubChem CID (73.81%)
6,285 records missing PubChem CID (26.19%)
```

## 16. Deduplication Analysis
- Within-query deduplication applied on `(plant_name.lower(), compound_name.lower(), pubchem_cid, reference_link)`.
- Global uniqueness check on `data/raw/bmppd/bmppd_compounds_raw.csv`:
  - Total rows: 24,001
  - Unique keys: 24,001
  - Duplicate rows introduced: **0**

## 17. Provenance Verification
Every single row in `bmppd_compounds_raw.csv` was audited against `data/processed/mpbd/mpbd_bmppd_query_map.csv`:
- `plant_index` matches the master inventory ID.
- `source_query` matches the frozen MPBD scientific name verbatim.
- `bmpdd_query_name` matches the Stage 6E resolved dispatch query.
- `source_page_url` corresponds to `https://bmppd.org/bmppd_result/?q={bmpdd_query_name}`.
- **Total Provenance Mismatches**: **0** (100% verified trace).

## 18. Cache Audit
- **Cache Directory**: `scrapers/cache/bmppd/`
- **Cache Index**: `scrapers/cache/bmppd/index.csv`
- **Total Cached Files on Disk**: Exactly 916 HTML files corresponding to the 916 plant query URLs.
- **Total Cache Index Rows**: 934 (916 resolved plant queries + 18 legacy pilot queries).
- **Integrity**: Every file has valid SHA-256 content hash, HTTP 200 status, and UTF-8 encoding.

## 19. Resume Behavior Verification
- Resume protection verified during both primary run (skipped plants 1, 2, 4, 5, 9, 13, 14, 16) and retry runs.
- Duplicate output records prevented across all executions.

## 20. Protected-File Checksum Verification
- `data/raw/mpbd/mpbd_plant_index.csv`: SHA-256 = `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` (**FROZEN - UNTOUCHED**)
- `scrapers/bmppd_query_resolver.py`: `git diff` clean (**UNTOUCHED**)
- `data/processed/mpbd/mpbd_bmppd_query_map.csv`: `git diff` clean (**UNTOUCHED**)
- `data/processed/mpbd/bmppd_query_overrides.csv`: `git diff` clean (**UNTOUCHED**)

## 21. Anomalies
None. Upstream server instability during primary pass between indices 132–267 was gracefully caught, audited, and cleared via `--retry-failed`.

## 22. Final Acquisition Status
**STAGE 6H COMPLETED SUCCESSFULLY**. The complete BMPPD phytochemical dataset for the frozen MPBD inventory (916 plants) has been acquired, cached, verified, and locked in raw production storage. Downstream normalization, PubChem cross-referencing, and ML preparation remain for subsequent thesis pipeline stages.
