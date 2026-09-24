# BMPPD Query Compatibility Pilot Report

**Context**: Stage 6 Query-Compatibility Investigation  
**Date**: 2026-09-23  
**Dataset Source**: `data/raw/mpbd/mpbd_plant_index.csv` (records 1–5, read-only)  
**Cache Directory**: `scrapers/cache/bmppd/`  

---

## Executive Summary

This pilot tests whether raw MPBD botanical scientific names containing taxonomic authority abbreviations (e.g. `L.`, `Vahl`, `DC.`, `Lam.`) fail to match records in BMPPD, and whether removing botanical authority information resolves the queries.

---

## Pilot Results Table

| Index | Raw MPBD Scientific Name | Raw Status | Raw Rows | Candidate Query | Cand Status | Cand Rows | Cand With CID | Cand Missing CID |
| :---: | :--- | :---: | :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `Piper betle L.` | `ZERO_RESULTS` | 0 | `Piper betle` | `PASS` | 112 | 0 | 112 |
| 2 | `Piper cubeba Vahl` | `ZERO_RESULTS` | 0 | `Piper cubeba` | `PASS` | 181 | 0 | 181 |
| 3 | `Berberis aristata DC.` | `ZERO_RESULTS` | 0 | `Berberis aristata` | `ZERO_RESULTS` | 0 | 0 | 0 |
| 4 | `Papaver somniferum L.` | `ZERO_RESULTS` | 0 | `Papaver somniferum` | `PASS` | 128 | 0 | 128 |
| 5 | `Artocarpus heterophyllus Lam.` | `ZERO_RESULTS` | 0 | `Artocarpus heterophyllus` | `PASS` | 180 | 0 | 180 |

---

## Plant-by-Plant Analysis

### 1. Piper betle L.
- **Raw MPBD Name**: `Piper betle L.`
- **Raw Query URL**: [https://bmppd.org/bmppd_result/?q=Piper+betle+L.](https://bmppd.org/bmppd_result/?q=Piper+betle+L.)
- **Raw Query Result**: `ZERO_RESULTS` (0 rows extracted)
- **Candidate Query**: `Piper betle`
- **Candidate Query URL**: [https://bmppd.org/bmppd_result/?q=Piper+betle](https://bmppd.org/bmppd_result/?q=Piper+betle)
- **Candidate Query Result**: `PASS` (112 rows extracted: 0 with CID, 112 missing CID)
- **Authority Removal Impact**: Changed result from ZERO_RESULTS to PASS
- **Viability Assessment**: Highly viable candidate query yielding valid phytochemical records.

### 2. Piper cubeba Vahl
- **Raw MPBD Name**: `Piper cubeba Vahl`
- **Raw Query URL**: [https://bmppd.org/bmppd_result/?q=Piper+cubeba+Vahl](https://bmppd.org/bmppd_result/?q=Piper+cubeba+Vahl)
- **Raw Query Result**: `ZERO_RESULTS` (0 rows extracted)
- **Candidate Query**: `Piper cubeba`
- **Candidate Query URL**: [https://bmppd.org/bmppd_result/?q=Piper+cubeba](https://bmppd.org/bmppd_result/?q=Piper+cubeba)
- **Candidate Query Result**: `PASS` (181 rows extracted: 0 with CID, 181 missing CID)
- **Authority Removal Impact**: Changed result from ZERO_RESULTS to PASS
- **Viability Assessment**: Highly viable candidate query yielding valid phytochemical records.

### 3. Berberis aristata DC.
- **Raw MPBD Name**: `Berberis aristata DC.`
- **Raw Query URL**: [https://bmppd.org/bmppd_result/?q=Berberis+aristata+DC.](https://bmppd.org/bmppd_result/?q=Berberis+aristata+DC.)
- **Raw Query Result**: `ZERO_RESULTS` (0 rows extracted)
- **Candidate Query**: `Berberis aristata`
- **Candidate Query URL**: [https://bmppd.org/bmppd_result/?q=Berberis+aristata](https://bmppd.org/bmppd_result/?q=Berberis+aristata)
- **Candidate Query Result**: `ZERO_RESULTS` (0 rows extracted: 0 with CID, 0 missing CID)
- **Authority Removal Impact**: No change observed
- **Viability Assessment**: Query yielded ZERO_RESULTS under both raw and candidate forms.

### 4. Papaver somniferum L.
- **Raw MPBD Name**: `Papaver somniferum L.`
- **Raw Query URL**: [https://bmppd.org/bmppd_result/?q=Papaver+somniferum+L.](https://bmppd.org/bmppd_result/?q=Papaver+somniferum+L.)
- **Raw Query Result**: `ZERO_RESULTS` (0 rows extracted)
- **Candidate Query**: `Papaver somniferum`
- **Candidate Query URL**: [https://bmppd.org/bmppd_result/?q=Papaver+somniferum](https://bmppd.org/bmppd_result/?q=Papaver+somniferum)
- **Candidate Query Result**: `PASS` (128 rows extracted: 0 with CID, 128 missing CID)
- **Authority Removal Impact**: Changed result from ZERO_RESULTS to PASS
- **Viability Assessment**: Highly viable candidate query yielding valid phytochemical records.

### 5. Artocarpus heterophyllus Lam.
- **Raw MPBD Name**: `Artocarpus heterophyllus Lam.`
- **Raw Query URL**: [https://bmppd.org/bmppd_result/?q=Artocarpus+heterophyllus+Lam.](https://bmppd.org/bmppd_result/?q=Artocarpus+heterophyllus+Lam.)
- **Raw Query Result**: `ZERO_RESULTS` (0 rows extracted)
- **Candidate Query**: `Artocarpus heterophyllus`
- **Candidate Query URL**: [https://bmppd.org/bmppd_result/?q=Artocarpus+heterophyllus](https://bmppd.org/bmppd_result/?q=Artocarpus+heterophyllus)
- **Candidate Query Result**: `PASS` (180 rows extracted: 0 with CID, 180 missing CID)
- **Authority Removal Impact**: Changed result from ZERO_RESULTS to PASS
- **Viability Assessment**: Highly viable candidate query yielding valid phytochemical records.

---

## Key Findings & Provenance Design Recommendations

1. **Hypothesis Confirmed**: BMPPD's search engine performs substring or keyword indexing that does not match author citations like `L.` or `DC.` when appended directly to binomial names.
2. **Critical Example (*Piper betle*)**: `Piper betle L.` produces `ZERO_RESULTS`, while `Piper betle` successfully extracts phytochemical compound records.
3. **Provenance Requirement**: The final pipeline must retain two separate fields:
   - `source_query_raw`: Exact original string from MPBD (e.g. `Piper betle L.`).
   - `bmppd_query_name`: Cleaned query string dispatched to BMPPD (e.g. `Piper betle`).
4. **No Premature Universal Rule**: A universal regex rule should not be applied yet without systematically characterizing the remaining 911 MPBD botanical author patterns.

