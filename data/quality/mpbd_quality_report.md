# MPBD Dataset Quality & Reproducibility Audit Report

**Dataset**: Medicinal Plants of Bangladesh (MPBD) Enumeration Index  
**Version**: `v1.0.0` (Frozen Raw Dataset)  
**File**: `data/raw/mpbd/mpbd_plant_index.csv`  
**Audit Date**: `2026-09-22T22:35:00+06:00`  
**Evaluation Mode**: Full Offline Quality Validation (0 network requests)

---

## 1. Dataset Overview

The MPBD dataset contains the comprehensive enumeration of medicinal plant records published by the Medicinal Plants of Bangladesh portal (`https://mpbd.cu.ac.bd/plants.php`). The raw collection was conducted via polite, rate-limited sequential HTTP requests backed by an RFC-compliant caching and provenance system.

| Metric | Value |
| :--- | :--- |
| **Total Pages Detected & Scraped** | 93 |
| **Total Raw Rows Extracted** | 921 |
| **Exact Duplicates Removed** | 5 |
| **Final Unique Records** | 916 |
| **Cached HTML Files on Disk** | 93 |
| **Audit Status** | **PASS** (100% Reconciled) |
| **Final CSV SHA-256** | `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` |

---

## 2. Schema Validation

The dataset adheres strictly to the 5-column target schema.

| Column Name | Inferred Type | Expected Format | Null Count | Empty String | Whitespace-Only | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `scientific_name` | String (Text) | Binomial + Authority | 0 | 0 | 0 | **PASS** |
| `synonym` | String (Text) | Space-delimited synonyms | 0 | 8 | 0 | **PASS** |
| `family` | String (Text) | Botanical family name | 0 | 0 | 0 | **PASS** |
| `source_page_url` | String (URI) | Canonical MPBD URL | 0 | 0 | 0 | **PASS** |
| `scrape_timestamp` | String (ISO-8601) | UTC timestamp | 0 | 0 | 0 | **PASS** |

- Total row count matches expected: 916 records (+ 1 header line = 917 lines).
- Data fields are free of corrupting delimiter collisions, missing columns, or trailing delimiters.

---

## 3. Missing-Value Analysis

- **`scientific_name`**: 0 missing values (100% complete).
- **`family`**: 0 missing values (100% complete).
- **`source_page_url`**: 0 missing values (100% valid canonical URLs).
- **`scrape_timestamp`**: 0 missing values (100% ISO-8601 UTC).
- **`synonym`**: 
  - 821 records (89.6%) contain explicit textual synonyms.
  - 87 records (9.5%) contain a literal hyphen (`-`) indicating no recorded synonym in the source database.
  - 8 records (0.9%) contain an empty string (`""`) where the synonym cell in the HTML table was blank.
  - Neither empty strings nor hyphens represent data corruption; they reflect MPBD's underlying missingness.

---

## 4. Scientific Name Quality Analysis

Quality checks performed on `scientific_name`:

| Quality Check | Finding | Status / Action |
| :--- | :--- | :--- |
| Leading / Trailing Whitespace | 0 records | **PASS** (Normalized cleanly during parsing) |
| Collapsed Internal Whitespace | 0 records with `\s{2,}` | **PASS** |
| HTML Entities / Escaped Text | 0 records with `&...;` | **PASS** |
| Unexpected Characters | 0 records | **PASS** |
| ALL-CAPS Entire Name | 1 record (`ANETHUM SOWA ROXB. EX FLEM.`) | Upstream artifact in MPBD source |
| ALL-CAPS Specific Epithets | 694 records | Upstream artifact in MPBD source (e.g. `Centella ASIATICA`) |
| Case-Insensitive Name Duplicates | 26 groups | Upstream redundancy in MPBD source (documented below) |

### Important Taxonomic Finding: Upstream MPBD Capitalization & Redundancy
Under normalized case-folding (`lowercase(collapse_whitespace(name))`), 26 binomial names appear more than once with differing case conventions. Examples include:
- `Ficus racemosa L.` (Page 1) vs. `Ficus RACEMOSA L.` (Page 55)
- `Morus indica L.` (Page 1) vs. `Morus INDICA L.` (Page 38)
- `Mirabilis jalapa L.` (Page 2) vs. `Mirabilis JALAPA L.` (Page 39)
- `Plumbago indica L.` (`Plumbaginaceae.`) (Page 2) vs. `Plumbago INDICA L.` (`Plumbaginaceae`) (Page 31)

> [!NOTE]
> Per the thesis design guidelines, these differences are **deliberately preserved** in the raw dataset. They represent authentic source idiosyncrasies that will be addressed in Stage 4 botanical normalization and reconciliation.

---

## 5. Family Field Audit

| Metric | Count |
| :--- | :--- |
| **Raw Unique Family Values** | 182 |
| **Normalized Unique Family Values** | 179 |
| **Leading / Trailing Whitespace** | 0 |
| **Empty or Blank Values** | 0 |

### Family Capitalization Inconsistencies
3 families appear under both Titlecase and ALL-CAPS in the upstream portal:
1. `Lauraceae` (14 records) vs. `LAURACEAE` (1 record on Page 90: `Actinodaphne obovata`)
2. `Annonaceae` (20 records) vs. `ANNONACEAE` (3 records on Page 90: `Uvaria hamiltonii`, `Desmos chinensislour.`, `Dasymaschalon longiflorum`)
3. `Magnoliaceae` (2 records) vs. `MAGNOLIACEAE` (1 record on Page 91: `Magnolia praecalva`)

### Top 10 Families by Record Count

| Rank | Family | Record Count | Percentage of Total |
| :--- | :--- | :--- | :--- |
| 1 | `Fabaceae` | 55 | 6.00% |
| 2 | `Euphorbiaceae` | 39 | 4.26% |
| 3 | `Rubiaceae` | 32 | 3.49% |
| 4 | `Asteraceae` | 30 | 3.28% |
| 5 | `Malvaceae` | 25 | 2.73% |
| 6 | `Lamiaceae` | 24 | 2.62% |
| 7 | `Zingiberaceae` | 22 | 2.40% |
| 8 | `Moraceae` | 20 | 2.18% |
| 9 | `Cucurbitaceae` | 20 | 2.18% |
| 10 | `Poaceae` | 19 | 2.07% |

---

## 6. Synonym Field Audit

- **Populated Synonyms**: 821 records (819 unique synonym string values).
- **Multi-Synonym Cells**: 738 cells contain multiple concatenated synonyms (e.g. `Chavica betle (L.) Miq. Betela mastica Raf. Chavica auriculata Miq.`).
- **Shared Synonym Values**: Exactly 2 pairs of records share identical synonym text:
  1. `Plumbago rosea L. Thela coccinea Lour.` (shared by `Plumbago indica L.` and `Plumbago INDICA L.`)
  2. `Anneslea spinosa Andrews Euryale indica Planch.` (shared by `Euryale ferox Salisb.` across different entries)

---

## 7. Source URL Audit

- **URL Pattern**: `^https://mpbd\.cu\.ac\.bd/plants\.php(\?pageno=\d+)?$`
- **Malformed URLs**: 0
- **Minimum Page**: 1 (`https://mpbd.cu.ac.bd/plants.php`)
- **Maximum Page**: 93 (`https://mpbd.cu.ac.bd/plants.php?pageno=93`)
- **Coverage**: Every integer page from 1 to 93 is represented in the output dataset.

---

## 8. Scrape Timestamp & Provenance Audit

- **Total Unique Timestamps**: 93 (exactly 1 timestamp per source page).
- **Earliest Timestamp**: `2026-09-22T15:35:25.096843+00:00` (Page 1, historical cache).
- **Latest Timestamp**: `2026-09-22T16:28:35.594799+00:00` (Page 93, live collection run).
- **Timestamp Stability**: Historical pages 1–20 retain identical timestamps across all warm-cache reruns.

### Provenance Mapping ([`scrapers/cache/mpbd/backfill_notes.csv`](file:///f:/bmppd-thesis/scrapers/cache/mpbd/backfill_notes.csv))
- **`BACKFILLED`**: 20 pages (198 final plant records). Inferred from filesystem modification time prior to metadata indexing.
- **`VERIFIED`**: 73 pages (718 final plant records). Captured synchronously during HTTP 200 retrieval.
- **Audit Result**: $198 + 718 = 916$ records. 100% accounted for.

---

## 9. Duplicate Validation

Deduplication was executed during collection using the key:
$$\text{Duplicate Key} = (\text{scientific\_name.strip()}, \text{family.strip()})$$

### Duplicates Removed (5 Records)

| Duplicate Name | Family | First Seen | Duplicate At | Action |
| :--- | :--- | :--- | :--- | :--- |
| *Mallotus philippensis (Lam.) Muell.-Arg.* | Euphorbiaceae | Page 7, Row 3 | Page 9, Row 8 | Omitted from final CSV |
| *Vitis vinifera L.* | Vitaceae | Page 7, Row 4 | Page 9, Row 9 | Omitted from final CSV |
| *Ocimum BASILICUM L.* | Lamiaceae | Page 35, Row 10 | Page 36, Row 1 | Omitted from final CSV |
| *Eclipta prostrata (L.) L.* | Asteraceae | Page 6, Row 5 | Page 58, Row 6 | Omitted from final CSV |
| *Grewia asiatica L.* | Tiliaceae | Page 52, Row 4 | Page 83, Row 5 | Omitted from final CSV |

- **Exact Duplicate Count in Final CSV**: 0
- **Independent Reconciliation**: PASS ($921 - 5 = 916$).

---

## 10. Cross-Page Extraction Distribution

- **Pages 1–92**: 10 raw rows per page ($92 \times 10 = 920$ rows).
- **Page 93**: Exactly 1 raw row (*Ficus auriculata Lour.*).
- **Total Raw Rows**: $920 + 1 = 921$.

| Page Range | Extracted Rows | Duplicates Removed | Net Records in CSV |
| :--- | :--- | :--- | :--- |
| **Pages 1–20** | 200 | 2 (Page 9) | 198 |
| **Page 21** | 10 | 0 | 10 |
| **Pages 22–92** | 710 | 3 (Pages 36, 58, 83) | 707 |
| **Page 93** | 1 | 0 | 1 |
| **Total (1–93)** | **921** | **5** | **916** |

---

## 11. Cache Integrity Audit

Inspection of [`scrapers/cache/mpbd/index.csv`](file:///f:/bmppd-thesis/scrapers/cache/mpbd/index.csv) against local `.html` files in [`scrapers/cache/mpbd/`](file:///f:/bmppd-thesis/scrapers/cache/mpbd/):

- **Indexed URLs**: 93
- **HTML Cache Files Present**: 93
- **Missing Cache Files**: 0
- **SHA-256 Hash Verification**: 93/93 content hashes recomputed from cached text match `index.csv` with zero mismatches.

---

## 12. Attrition Log Reconciliation

Inspection of [`data/attrition/mpbd_attrition.csv`](file:///f:/bmppd-thesis/data/attrition/mpbd_attrition.csv):

- **Full-run records**: Exactly 93 audit records (`run_timestamp: 2026-09-22T16:26:45.042578+00:00`).
- **Pages**: 1 through 93 inclusive, no missing or duplicate page entries.
- **Cache Hits**: 21
- **Cache Misses (Web Fetches)**: 72
- **Sum of `rows_extracted`**: 921
- **Sum of `duplicate_rows`**: 5
- **Sum of `rows_extracted` - `duplicate_rows`**: 916
- **Parser Status**: 93 `PASS`, 0 `ZERO_ROWS`, 0 `PARSE_FAILED`, 0 `FETCH_FAILED`.

---

## 13. Final Dataset Checksum & Immutability

The primary CSV artifact is validated and frozen:

```text
File: data/raw/mpbd/mpbd_plant_index.csv
Size: 187,111 bytes
Lines: 917 (1 header line + 916 data records)
SHA-256: 0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7
```

Historical Stage 2 artifacts remain bit-for-bit unchanged:
- `data/raw/mpbd/mpbd_plant_index_pages1_20.csv` SHA-256: `5731C829F57CC19E97177A5195E00E3FB127BB7A9F26DB76F8FC6106F2613199`
- `data/raw/mpbd/mpbd_plant_index_pilot.csv`: intact
- `data/raw/mpbd/mpbd_plant_index_pages1_5.csv`: intact
- `data/raw/mpbd/mpbd_plant_index_pages21_21.csv`: intact

---

## 14. Dataset Freeze Status: FROZEN

All 14 validation criteria have passed without exceptions. The dataset [`data/raw/mpbd/mpbd_plant_index.csv`](file:///f:/bmppd-thesis/data/raw/mpbd/mpbd_plant_index.csv) is officially designated as a **frozen source dataset** (`v1.0.0`) for all subsequent downstream pipeline operations (chemical enrichment, PubChem querying, and bioactivity screening).
