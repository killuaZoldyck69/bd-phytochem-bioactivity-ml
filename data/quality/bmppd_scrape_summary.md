# BMPPD Stage 6 -- Bulk Scrape Summary

**Stage**: 6 -- Bulk BMPPD Phytochemical Scraping  
**Run Mode**: `retry-failed`  
**Plant Range**: `1-916`  
**Run Timestamp**: `2026-09-24T08:39:12.418930+00:00`  
**Report Generated**: `2026-09-24T08:39:13.202813+00:00`

---

## Run Statistics

| Metric | Value |
| :--- | :--- |
| **Plants attempted** | 89 |
| **Successful queries (>=1 result)** | 0 |
| **Zero-result queries** | 89 |
| **Fetch failures** | 0 |
| **Parse failures** | 0 |
| **Total compound rows extracted** | 0 |
| **Rows with valid PubChem CID** | 0 |
| **Rows missing CID** | 0 (0.00%) |
| **Cache hits** | 89 |
| **Live web fetches** | 0 |

---

## Output Files

- `data/raw/bmppd/bmppd_compounds_raw.csv` -- consolidated compound rows
- `data/attrition/bmppd_attrition.csv` -- per-plant audit log
- `data/raw/bmppd/bmppd_failed_plants.csv` -- plants that errored
- `scrapers/cache/bmppd/` -- cached HTML responses + index.csv
