# BMPPD Stage 6G — Controlled Bulk Expansion Report (Plants 1–20)

## 1. Objective
Execute a controlled, production-integrated bulk scrape of BMPPD phytochemical data for `plant_index` 1–20 using the deterministic query-resolution layer established in Stage 6E and production scraper engine integrated in Stage 6F. Verify end-to-end determinism, cache efficiency, resume protection, full provenance tracing, attrition logging, and immutability of the frozen MPBD master inventory.

## 2. Execution Date / Time
- **Timestamp (UTC)**: 2026-09-24T07:12:49Z / 2026-09-24T07:14:49Z
- **Local Time**: 2026-09-24 13:12:49 / 13:14:49 (+06:00)

## 3. Plant Range
- `plant_index`: 1–20 (20 plants in scope)

## 4. Pre-Run Integrity Checks
| Check | Requirement | Result | Status |
| :--- | :--- | :--- | :--- |
| **MPBD Master SHA-256** | `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` | `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` | **VERIFIED** |
| **Query Map Records** | Exactly 916 records | 916 records | **VERIFIED** |
| **Plants 1–20 Existence** | Unique `plant_index` 1 to 20 | Exactly 20 distinct records | **VERIFIED** |
| **Field Completeness (1–20)** | Non-empty `raw_mpbd_name`, `bmpdd_query_name`, valid status | 20/20 valid | **VERIFIED** |
| **Name Alignment (1–20)** | `raw_mpbd_name` == `scientific_name` in frozen index | 20/20 exact match | **VERIFIED** |
| **Resolver Source Code** | `scrapers/bmppd_query_resolver.py` unmodified | `git diff` clean (0 changes) | **VERIFIED** |
| **Initial Cache Index Count** | Baseline entries in `scrapers/cache/bmppd/index.csv` | 80 entries | **RECORDED** |
| **Initial Output Rows** | Baseline rows in `data/raw/bmppd/bmppd_compounds_raw.csv` | 601 rows (from Stage 6F plants 1–5) | **RECORDED** |
| **Initial Attrition Rows** | Baseline rows in `data/attrition/bmppd_attrition.csv` | 16 records | **RECORDED** |
| **Initial Failed Plants** | Baseline rows in `data/raw/bmppd/bmppd_failed_plants.csv` | 0 records | **RECORDED** |

## 5. Query-Resolution Verification (Plants 1–20)
All 20 records were evaluated via deterministic offline rules without botanical authority fallback:

| `plant_index` | `source_query` (Frozen MPBD Name) | `bmpdd_query_name` (Resolved Query) | `query_status` | `query_source` |
| :---: | :--- | :--- | :---: | :---: |
| 1 | *Piper betle* L. | *Piper betle* | READY | OFFLINE_RULE |
| 2 | *Piper cubeba* Vahl | *Piper cubeba* | READY | OFFLINE_RULE |
| 3 | *Berberis aristata* DC. | *Berberis aristata* | READY | OFFLINE_RULE |
| 4 | *Papaver somniferum* L. | *Papaver somniferum* | READY | OFFLINE_RULE |
| 5 | *Artocarpus heterophyllus* Lam. | *Artocarpus heterophyllus* | READY | OFFLINE_RULE |
| 6 | *Ficus racemosa* L. | *Ficus racemosa* | READY | OFFLINE_RULE |
| 7 | *Morus indica* L. | *Morus indica* | READY | OFFLINE_RULE |
| 8 | *Juglans regia* L. | *Juglans regia* | READY | OFFLINE_RULE |
| 9 | *Boerhavia diffusa* L. | *Boerhavia diffusa* | READY | OFFLINE_RULE |
| 10 | *Boerhavia repens* L. | *Boerhavia repens* | READY | OFFLINE_RULE |
| 11 | *Mirabilis jalapa* L. | *Mirabilis jalapa* | READY | OFFLINE_RULE |
| 12 | *Opuntia dellenii* (Ker Gawl.) Haw. | *Opuntia dellenii* | READY | OFFLINE_RULE |
| 13 | *Achyranthes aspera* L. | *Achyranthes aspera* | READY | OFFLINE_RULE |
| 14 | *Plumbago indica* L. | *Plumbago indica* | READY | OFFLINE_RULE |
| 15 | *Vateria indica* L. | *Vateria indica* | READY | OFFLINE_RULE |
| 16 | *Mesua ferrea* L. | *Mesua ferrea* | READY | OFFLINE_RULE |
| 17 | *Helicteres isora* L. | *Helicteres isora* | READY | OFFLINE_RULE |
| 18 | *Abelmoschus esculentus* (L.) Moench | *Abelmoschus esculentus* | READY | OFFLINE_RULE |
| 19 | *Gossypium arboreum* L. | *Gossypium arboreum* | READY | OFFLINE_RULE |
| 20 | *Viola odorata* L. | *Viola odorata* | READY | OFFLINE_RULE |

## 6. Cache-Only Precheck
Command executed:
```bash
python scrapers/bmppd_bulk_scraper.py --plants 1-20 --cache-only
```
- **Plants in scope**: 20
- **Already cached**: 20 (100.0%)
- **Not yet cached**: 0 (0.0%)
- **Network requests made**: 0
- **Cache index count before / after**: 80 / 80 (unchanged)

## 7. Production Run Statistics (`--plants 1-20`)
Command executed:
```bash
python scrapers/bmppd_bulk_scraper.py --plants 1-20
```
- **Run Mode**: `plants 1-20`
- **Plants in scope**: 20
- **Skipped via resume protection**: 4 (plants 1, 2, 4, 5 previously completed in Stage 6F)
- **Plants evaluated**: 16 (plants 3, 6–20)
- **Successful queries (PASS)**: 4 (plants 9, 13, 14, 16)
- **Zero-result queries (ZERO_RESULTS)**: 12 (plants 3, 6, 7, 8, 10, 11, 12, 15, 17, 18, 19, 20)
- **Fetch failures (FETCH_FAILED)**: 0
- **Parse failures (PARSE_FAILED)**: 0
- **New compound rows extracted**: 250
- **Cumulative compound rows (Plants 1–20)**: 851
- **Cache hits**: 16 / 16 (100.0%)
- **Live web fetches**: 0

## 8. Per-Plant Extraction Table (Cumulative Plants 1–20)

| `plant_index` | `source_query` (Frozen MPBD Name) | `bmpdd_query_name` (Dispatched Query) | Cache Status | Parser Status | Extracted Rows | Rows With CID | Rows Missing CID |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **1** | *Piper betle* L. | *Piper betle* | HIT | PASS | 112 | 0 | 112 |
| **2** | *Piper cubeba* Vahl | *Piper cubeba* | HIT | PASS | 181 | 0 | 181 |
| **3** | *Berberis aristata* DC. | *Berberis aristata* | HIT | ZERO_RESULTS | 0 | 0 | 0 |
| **4** | *Papaver somniferum* L. | *Papaver somniferum* | HIT | PASS | 128 | 0 | 128 |
| **5** | *Artocarpus heterophyllus* Lam. | *Artocarpus heterophyllus* | HIT | PASS | 180 | 0 | 180 |
| **6** | *Ficus racemosa* L. | *Ficus racemosa* | HIT | ZERO_RESULTS | 0 | 0 | 0 |
| **7** | *Morus indica* L. | *Morus indica* | HIT | ZERO_RESULTS | 0 | 0 | 0 |
| **8** | *Juglans regia* L. | *Juglans regia* | HIT | ZERO_RESULTS | 0 | 0 | 0 |
| **9** | *Boerhavia diffusa* L. | *Boerhavia diffusa* | HIT | PASS | 57 | 53 | 4 |
| **10** | *Boerhavia repens* L. | *Boerhavia repens* | HIT | ZERO_RESULTS | 0 | 0 | 0 |
| **11** | *Mirabilis jalapa* L. | *Mirabilis jalapa* | HIT | ZERO_RESULTS | 0 | 0 | 0 |
| **12** | *Opuntia dellenii* (Ker Gawl.) Haw. | *Opuntia dellenii* | HIT | ZERO_RESULTS | 0 | 0 | 0 |
| **13** | *Achyranthes aspera* L. | *Achyranthes aspera* | HIT | PASS | 32 | 22 | 10 |
| **14** | *Plumbago indica* L. | *Plumbago indica* | HIT | PASS | 28 | 0 | 28 |
| **15** | *Vateria indica* L. | *Vateria indica* | HIT | ZERO_RESULTS | 0 | 0 | 0 |
| **16** | *Mesua ferrea* L. | *Mesua ferrea* | HIT | PASS | 133 | 133 | 0 |
| **17** | *Helicteres isora* L. | *Helicteres isora* | HIT | ZERO_RESULTS | 0 | 0 | 0 |
| **18** | *Abelmoschus esculentus* (L.) Moench | *Abelmoschus esculentus* | HIT | ZERO_RESULTS | 0 | 0 | 0 |
| **19** | *Gossypium arboreum* L. | *Gossypium arboreum* | HIT | ZERO_RESULTS | 0 | 0 | 0 |
| **20** | *Viola odorata* L. | *Viola odorata* | HIT | ZERO_RESULTS | 0 | 0 | 0 |
| **TOTAL** | — | — | — | **8 PASS / 12 ZERO** | **851** | **208** | **643** |

## 9. Attrition Audit
- Audit of [`data/attrition/bmppd_attrition.csv`](file:///F:/bmppd-thesis/data/attrition/bmppd_attrition.csv):
  - Total records in file: 32 (10 legacy test rows from initial raw query development, 6 from Stage 6F, 16 from Stage 6G).
  - All 16 Stage 6G records contain `run_timestamp = 2026-09-24T07:12:53.171492+00:00`.
  - For all PASS records: `rows_extracted > 0`.
  - For all ZERO_RESULTS records: `rows_extracted == 0`.
  - ZERO_RESULTS records are strictly classified as `ZERO_RESULTS`, never as `FETCH_FAILED` or `PARSE_FAILED`.
  - Provenance field `bmpdd_query_name` is present in all records.
  - `query_url` strictly matches `https://bmppd.org/bmppd_result/?q={bmpdd_query_name}`.

## 10. Failed-Plants Audit
- Audit of [`data/raw/bmppd/bmppd_failed_plants.csv`](file:///F:/bmppd-thesis/data/raw/bmppd/bmppd_failed_plants.csv):
  - Remaining failure records: **0**.
  - No fetch or parse failures occurred.
  - Zero-result queries are correctly excluded from the failure registry.

## 11. Raw-Data Provenance Audit
- Audit of [`data/raw/bmppd/bmppd_compounds_raw.csv`](file:///F:/bmppd-thesis/data/raw/bmppd/bmppd_compounds_raw.csv):
  - Exact column schema verified:
    `plant_index, source_query, bmpdd_query_name, plant_name, common_name, compound_name, pubchem_cid, reference_link, source_page_url, quality_flags, scrape_timestamp`
  - Total rows: **851** across 8 successful plants (1: 112, 2: 181, 4: 128, 5: 180, 9: 57, 13: 32, 14: 28, 16: 133).
  - Deduplication check: 851 total rows, 851 unique compound tuples. Zero duplicate rows within or across runs.
  - Provenance chain check: Checked all 851 rows against [`data/processed/mpbd/mpbd_bmppd_query_map.csv`](file:///F:/bmppd-thesis/data/processed/mpbd/mpbd_bmppd_query_map.csv); zero provenance mismatches.
  - Missing CIDs check: 643 missing CID rows, 100% flagged with `missing_pubchem_cid`. No artificial CID filling or chemical name alterations were performed.

## 12. CID Quality Statistics (Plants 1–20)
| Metric | Count | Percentage |
| :--- | :--- | :--- |
| **Total Extracted Compound Rows** | 851 | 100.00% |
| **Rows with Valid Numeric PubChem CID** | 208 | 24.44% |
| **Rows Missing PubChem CID** | 643 | 75.56% |

- *Note*: PubChem CID presence varies heavily by plant in BMPPD upstream data:
  - *Mesua ferrea* (Plant 16): 133/133 (100.0%) numeric CIDs.
  - *Boerhavia diffusa* (Plant 9): 53/57 (93.0%) numeric CIDs.
  - *Achyranthes aspera* (Plant 13): 22/32 (68.8%) numeric CIDs.
  - *Piper betle*, *Piper cubeba*, *Papaver somniferum*, *Artocarpus heterophyllus*, *Plumbago indica*: 0% numeric CIDs (BMPPD provides SMILES or `-` in `<td>CID: ...</td>`).

## 13. Cache Determinism Audit
- File: [`scrapers/cache/bmppd/index.csv`](file:///F:/bmppd-thesis/scrapers/cache/bmppd/index.csv)
- **Entries before Stage 6G**: 80
- **Entries after Stage 6G**: 80
- **New cache entries**: 0
- **Live HTTP requests**: 0
- Cached HTML files were reused without refetching or corruption.

## 14. Warm-Run / Resume Verification
1. Cache-only verification:
   ```bash
   python scrapers/bmppd_bulk_scraper.py --plants 1-20 --cache-only
   ```
   Confirmed all 20 plants cached; 0 network requests.
2. Warm production rerun:
   ```bash
   python scrapers/bmppd_bulk_scraper.py --plants 1-20
   ```
   - All 8 previously successful plants (1, 2, 4, 5, 9, 13, 14, 16) skipped via resume protection:
     `[SKIP (already completed)]`.
   - The 12 ZERO_RESULTS plants re-evaluated from cache with 0 network requests.
   - Total rows in `bmppd_compounds_raw.csv` remained exactly 851 (zero duplicate insertions).
   - Cache index remained at 80 entries.

## 15. Frozen MPBD Checksum Verification
- Master inventory file: [`data/raw/mpbd/mpbd_plant_index.csv`](file:///F:/bmppd-thesis/data/raw/mpbd/mpbd_plant_index.csv)
- Calculated SHA-256: `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7`
- Expected SHA-256: `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7`
- Checksum status: **VERIFIED MATCH**

## 16. Protected Files Audit
- `scrapers/bmppd_query_resolver.py`: **UNTOUCHED** (`git diff` clean)
- `data/processed/mpbd/mpbd_bmppd_query_map.csv`: **UNTOUCHED** (`git diff` clean)
- `data/processed/mpbd/bmppd_query_overrides.csv`: **UNTOUCHED** (`git diff` clean)

## 17. Anomalies
None. No stop conditions were met.

## 18. Final Status
**PASS — STAGE 6G COMPLETE**. The bulk scraping pipeline is verified, deterministic, and auditable across plants 1–20.
