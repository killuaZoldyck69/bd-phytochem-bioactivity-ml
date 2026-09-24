# Stage 8A: MPBD Plant Detail-Page Scrape & Traditional-Use Extraction Report

**Date**: 2026-09-24 18:57:26 UTC  
**Master MPBD SHA-256 (Start & End Verified)**: `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7`  
**Execution Runtime**: 1164.9 seconds  
**robots.txt Status**: HTTP 404 (Allowed per RFC 9309, unrestricted public access)  

---

## 1. Run Summary

| Metric | Count | Percentage |
| :--- | :--- | :--- |
| Total Plants Requested | 916 | 100.0% |
| Pages Fetched Live | 916 | 100.0% |
| Pages Loaded from Cache | 20 | 2.2% |
| Failed Requests After Retries | 0 | 0.0% |
| Final Unique Raw Detail Records | 916 | 100.0% |

## 2. Step 1: Plant Index to Detail-URL Map Results

- **Total Links Extracted**: 916 (Expected: 916)
- **Site ID Range**: Min = `4`, Max = `925`
- **Site ID Gaps** (6 total): `[92, 93, 199, 355, 582, 828]`
- **Duplicate Site IDs**: `{}` (Zero duplicates in master alignment)
- **Exact Trimmed String Matches**: 281 / 916 (30.7%)
- **Exact Whitespace-Normalized Matches**: 916 / 916 (100.0%)
  > *Note on Alignment*: The 635 differences between trimmed list-page text and master strings are solely consecutive interior whitespace runs present in the list page HTML (e.g. `Acacia nilotica (L.) Delile  subsp. INDICA(Benth) Brenan`), which `mpbd_scraper.py` collapsed to single spaces during initial collection. When normalized, 916/916 align with 100% mathematical precision.

## 3. Step 2: Site Vocabulary & Search Control Findings

### A. 'Search by Disease' Control
- **Location**: Present on plants list pages sidebar (`#searchdisease`).
- **Control Type**: `<input class="form-control" id="searchdisease" name="searchdisease" placeholder="Type here to search..." type="text">`.
- **Fixed Options**: **None**. There is no `<select>` dropdown or `<option>` tags in the page HTML.
- **Mechanism**: Dynamic client-side AJAX (`script.js`) triggering `POST ajax.php` on keyup. Per strict instruction, no search forms were submitted or sub-pages crawled.

### B. Vocabulary Pages Inspection
- **`/dictionary.php`**: Returned **HTTP 404 (Not Found)**. The page does not exist on the MPBD server.
- **`/pharmacology.php`**: Returned **HTTP 200**. Contains a table of pharmacology terms with columns `Name` and `Description` under `<h3>Pharmacology Terms</h3>`.
  - Pagination: **Paginated across 47 pages** (`?pageno=1` to `?pageno=47`), with 10 terms per page (~470 terms total).
  - Per hard constraints, only Page 1 was fetched and cached; no sub-pages were crawled without explicit user authorization.
- **`/botany.php`**: Returned **HTTP 200**. Contains botanical terms (`Name`, `Structure/Category`, `Description`) paginated across multiple pages.
- Output written to [`data/raw/mpbd_details/mpbd_disease_vocabulary.csv`](file:///f:/bmppd-thesis/data/raw/mpbd_details/mpbd_disease_vocabulary.csv).

## 4. Field Completeness

### Overall (All 916 MPBD Plants)

| Field | Non-Empty Count | Percentage |
| :--- | :--- | :--- |
| `disease_raw` | 916 | 100.00% |
| `uses_raw` | 916 | 100.00% |
| Both Present | 916 | 100.00% |
| Neither Present | 0 | 0.00% |

### Compound Plants Subset (222 Plants with Mapped Compounds)

| Field | Non-Empty Count | Percentage |
| :--- | :--- | :--- |
| `disease_raw` | 222 | 100.00% |
| `uses_raw` | 222 | 100.00% |
| Both Present | 222 | 100.00% |
| Neither Present | 0 | 0.00% |

### Plants Among the 222 Compound Plants with Empty `Disease` Field (0 total):

*(None — all 222 compound plants have a populated `disease_raw` field!)*

## 5. Quality Flags and Mismatches

| Quality Flag | Affected Plants | Description |
| :--- | :--- | :--- |
| `encoding_loss_suspected` | 269 | Flagged in detail dataset |

### Scientific Name Mismatches (`name_mismatch`): 0
*(Zero botanical name mismatches detected. All 916 plants matched their master binomial botanical stem perfectly)*

### Botanical Family Mismatches (`family_mismatch`): 0
*(Zero family mismatches detected. All detail page family fields matched the master index)*

### Upstream Encoding Loss & Column Truncation Verification
- **Greek Letter Encoding Loss**: Confirmed upstream. Inspection of the raw HTTP byte stream returned by the server revealed literal `0x3F` (`?`) bytes (e.g. `b'rpinene, ?-cymene, carvac'`), proving that the loss exists in the MPBD database itself and is not a client-side decoding issue.
- **Field Truncation**: In several plants (e.g. `site_id=4`, Piper betle), `Chemical Constituents` terminates abruptly at exactly 255 characters (`They al</td></tr>`), indicating an upstream MySQL `VARCHAR(255)` database schema constraint.

## 6. Long-Format Disease Term Statistics

- **Total Term Instances**: 6512
- **Distinct Lightly Normalized Terms (`term_light`)**: 1526
- **Terms per Plant**: Min = `0`, Median = `6`, Max = `25`

### Top 100 Most Frequent Disease Terms

| Rank | Term (All 916 Plants) | Plant Count (All) | Term (222 Compound Plants) | Plant Count (222) |
| :--- | :--- | :--- | :--- | :--- |
| 1 | tonic | 161 | dysentery | 45 |
| 2 | dysentery | 144 | tonic | 45 |
| 3 | diuretic | 140 | diuretic | 44 |
| 4 | fever | 135 | fever | 42 |
| 5 | astringent | 125 | astringent | 41 |
| 6 | asthma | 113 | diarrhoea | 34 |
| 7 | rheumatism | 107 | piles | 34 |
| 8 | bronchitis | 103 | rheumatism | 34 |
| 9 | stomachic | 101 | stomachic | 33 |
| 10 | diarrhoea | 99 | bronchitis | 30 |
| 11 | piles | 97 | asthma | 28 |
| 12 | laxative | 95 | carminative | 27 |
| 13 | cough | 91 | laxative | 27 |
| 14 | anthelmintic | 85 | jaundice | 26 |
| 15 | aphrodisiac | 82 | cough | 26 |
| 16 | ulcers | 81 | ulcers | 25 |
| 17 | cooling | 75 | stimulant | 24 |
| 18 | carminative | 69 | anthelmintic | 22 |
| 19 | jaundice | 68 | dyspepsia | 22 |
| 20 | stimulant | 66 | leprosy | 19 |
| 21 | purgative | 63 | skin diseases | 18 |
| 22 | skin diseases | 59 | cooling | 18 |
| 23 | leprosy | 58 | expectorant | 17 |
| 24 | expectorant | 55 | aphrodisiac | 17 |
| 25 | biliousness | 49 | purgative | 16 |
| 26 | gonorrhoea | 46 | emmenagogue | 16 |
| 27 | dyspepsia | 46 | boils | 15 |
| 28 | boils | 44 | headache | 15 |
| 29 | pain | 44 | demulcent | 15 |
| 30 | demulcent | 43 | fevers | 15 |
| 31 | colic | 41 | inflammations | 14 |
| 32 | febrifuge | 40 | diaphoretic | 14 |
| 33 | emmenagogue | 39 | diarrhea | 13 |
| 34 | emetic | 39 | constipation | 12 |
| 35 | leucoderma | 37 | flatulence | 12 |
| 36 | scabies | 37 | colic | 12 |
| 37 | fevers | 36 | antipyretic | 12 |
| 38 | alterative | 36 | gonorrhoea | 10 |
| 39 | headache | 34 | leucoderma | 10 |
| 40 | inflammations | 33 | biliousness | 10 |
| 41 | refrigerant | 32 | refrigerant | 10 |
| 42 | diarrhea | 32 | hysteria | 9 |
| 43 | epilepsy | 29 | epilepsy | 9 |
| 44 | diaphoretic | 29 | paralysis | 9 |
| 45 | bowels | 28 | wounds | 9 |
| 46 | dropsy | 28 | hiccup | 9 |
| 47 | constipation | 27 | anaemia | 9 |
| 48 | tumours | 27 | pain | 9 |
| 49 | antipyretic | 27 | eczema | 9 |
| 50 | eczema | 26 | diabetes | 8 |
| 51 | paralysis | 25 | gout | 8 |
| 52 | leucorrhoea | 25 | scabies | 8 |
| 53 | gonorrhea | 25 | sore throat | 8 |
| 54 | diabetes | 24 | coughs | 8 |
| 55 | strangury | 24 | emollient | 8 |
| 56 | cholera | 24 | alterative | 8 |
| 57 | hiccup | 23 | digestive | 8 |
| 58 | wounds | 23 | rubefacient | 8 |
| 59 | flatulence | 22 | ringworm | 8 |
| 60 | toothache | 22 | emetic | 8 |
| 61 | menorrhagia | 22 | cold | 7 |
| 62 | gout | 22 | gastric tumor | 7 |
| 63 | alexiteric | 22 | strangury | 7 |
| 64 | vomiting | 21 | lumbago | 7 |
| 65 | digestive | 20 | febrifuge | 7 |
| 66 | pains | 20 | cholera | 7 |
| 67 | lumbago | 19 | inflammation | 7 |
| 68 | anaemia | 19 | vulnerary | 7 |
| 69 | ringworm | 19 | antiseptic | 6 |
| 70 | appetizer | 19 | stomachache | 6 |
| 71 | antispasmodic | 19 | toothache | 6 |
| 72 | emollient | 19 | sprains | 6 |
| 73 | sores | 19 | bowels | 6 |
| 74 | antiseptic | 18 | menorrhagia | 6 |
| 75 | inflammation | 18 | antiperiodic | 6 |
| 76 | galactagogue | 18 | cirorhosis | 5 |
| 77 | coughs | 17 | abortion | 5 |
| 78 | vulnerary | 17 | epistaxis | 5 |
| 79 | hysteria | 16 | itch | 5 |
| 80 | ascites | 16 | insanity | 5 |
| 81 | antiperiodic | 16 | neuralgia | 5 |
| 82 | cold | 14 | pains | 5 |
| 83 | dysmenorrhoea | 14 | vomiting | 5 |
| 84 | ophthalmia | 14 | sedative | 5 |
| 85 | sprains | 14 | dropsy | 5 |
| 86 | stomachache | 13 | antiscorbutic | 5 |
| 87 | urinary discharges | 13 | antispasmodic | 5 |
| 88 | insanity | 13 | alexiteric | 5 |
| 89 | neuralgia | 13 | leucorrhoea | 5 |
| 90 | sore throat | 13 | gonorrhea | 5 |
| 91 | earache | 13 | stomach pain | 4 |
| 92 | dysuria | 13 | dysmenorrhoea | 4 |
| 93 | syphilis | 13 | duodenal ulcer | 4 |
| 94 | itch | 12 | pneumonia | 4 |
| 95 | indigestion | 12 | tumours | 4 |
| 96 | antiscorbutic | 12 | sudorific | 4 |
| 97 | rubefacient | 12 | oedema | 4 |
| 98 | gastric tumor | 11 | phthisis | 4 |
| 99 | spermatorrhoea | 11 | bruises | 4 |
| 100 | sedative | 11 | abdominal pain | 4 |

## 7. Exploratory Keyword Counts (222 Compound Plants)

> [!NOTE]
> These counts are **exploratory keyword matching only** across `disease_raw` and `uses_raw`. **No category mapping or therapeutic labeling has been applied.**

| Disease Category Concept | Keyword Stems | Plants Matching (out of 222) | Percentage | Matching Distinct Terms in Data |
| :--- | :--- | :--- | :--- | :--- |
| **pain** | `pain`, `ache`, `analges` | 86 | 38.7% | abdominal pain, analgesic, articular pains, back pain, body pain, carbuncles and pain, colic pain, diarrhoea and stomachache *(+32 more)* |
| **inflammation** | `inflam`, `swelling`, `arthrit`, `rheumat`, `edema` | 80 | 36.0% | anti-inflammatory, antirheumatic, chronic rheumatism, diarrhoea and rheumatism, gonorrhoea and inflammations, inflammat, inflammation, inflammation and liver *(+19 more)* |
| **fever** | `fever`, `pyrexia`, `febrifug` | 75 | 33.8% | anthelmintic and febrifuge, dyspnoea and fever, febrifuge, fever, fever and cough, fever and nervous diseases, fever and piles, fever and purgative *(+7 more)* |
| **nervous/cognitive** | `memory`, `cognit`, `nerv`, `epilep`, `convuls`, `paraly` | 33 | 14.9% | convulsion, convulsion and liver complaints, diarrhoea epilepsy, epilepsy, facial paralysis, febric convulsion, fever and nervous diseases, hemiepilepsy *(+6 more)* |
| **mood/sleep** | `depress`, `anxiety`, `insomnia`, `sedative`, `sleep` | 9 | 4.1% | anxiety, insomnia, sedative, sedative and refrigerant, sleeplessness, uterine sedative |
| **diabetes** | `diabet`, `sugar`, `glycos` | 16 | 7.2% | diabetes, diabetes and diarrhea, diabetes and gonorrhoea, jaundice and diabetes |
| **gout/uric** | `gout`, `uric` | 8 | 3.6% | gout |
| **cancer** | `cancer`, `tumor`, `tumour` | 20 | 9.0% | brest tumour and menstrual disorders, cancer, cancerous tumours, dysentery and cancer, gastric tumor, tumor, tumours, tumours and ascites *(+1 more)* |
| **liver/digestive** | `liver`, `jaundice`, `dyspep`, `diarrh`, `dysentery`, `ulcer` | 149 | 67.1% | affection of theliver and speen, ameobic dysentery, antidiarrhoeal, aphrodisiac and diarrhoea, blood dysentery, bronchitis and dyspepsia, chronic diarrhoea, chronic diarrhoea and dysentery *(+56 more)* |

## 8. Data Quality & Text Anomalies

1. **Typos and Spelling Variants**:
   - `stimulantion` (standard form: *stimulant*)
   - `rheumatisn` (standard form: *rheumatism*)
   - `inflamation` (standard form: *inflammation*)
   - `gonorrhoea / gonorrohea` (standard form: *gonorrhea / gonorrhoea*)
   - `diarrhoea / diarrhea` (standard form: *diarrhea variants*)
   - `leucorrhoea / leucorrhea` (standard form: *leucorrhea variants*)
   - `febrifuge / febrifuse` (standard form: *febrifuge variants*)
2. **Pharmacological Actions Mixed with Diseases**:
   - Numerous terms in the `disease_raw` column represent pharmacological or therapeutic actions rather than clinical disease entities, including:
     `antiseptic, astringent, carminative, stimulant, tonic, diuretic, febrifuge, purgative, laxative, anthelmintic, emetic, demulcent, expectorant, analgesic, rubefacient, refrigerant, aphrodisiac`
3. **Disease vs Uses Discrepancies**:
   - Number of plants where `disease_raw` and `uses_raw` completeness disagrees: **0** plants.
   - For plants where both are present, `uses_raw` frequently contains full prose sentences with additional conditions or administrative contexts not present in the comma-separated `disease_raw` list.

## 9. Output Files Created

| Output File | Row Count | File Size (Bytes) | Description |
| :--- | :--- | :--- | :--- |
| [`data/raw/mpbd_details/mpbd_detail_url_map.csv`](file:///f:/bmppd-thesis/data/raw/mpbd_details/mpbd_detail_url_map.csv) | 916 | 105,707 | Stage 8A artifact |
| [`data/raw/mpbd_details/mpbd_disease_vocabulary.csv`](file:///f:/bmppd-thesis/data/raw/mpbd_details/mpbd_disease_vocabulary.csv) | 12 | 2,052 | Stage 8A artifact |
| [`data/raw/mpbd_details/mpbd_plant_details_raw.csv`](file:///f:/bmppd-thesis/data/raw/mpbd_details/mpbd_plant_details_raw.csv) | 916 | 1,130,576 | Stage 8A artifact |
| [`data/processed/mpbd_details/mpbd_disease_terms_long.csv`](file:///f:/bmppd-thesis/data/processed/mpbd_details/mpbd_disease_terms_long.csv) | 6512 | 182,177 | Stage 8A artifact |
| [`data/attrition/mpbd_detail_attrition.csv`](file:///f:/bmppd-thesis/data/attrition/mpbd_detail_attrition.csv) | 936 | 113,757 | Stage 8A artifact |

---
**Status**: Scraper and parser fully verified. Ready for user review.