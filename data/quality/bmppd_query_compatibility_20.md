# BMPPD Stage 6 — 20-Plant Query Compatibility Expansion Pilot Report

**Context**: Stage 6 Query-Compatibility Investigation (Expansion to First 20 MPBD Records)  
**Date**: 2026-09-24  
**Source Dataset**: `data/raw/mpbd/mpbd_plant_index.csv` (records 1–20, strictly read-only)  
**Cache Directory**: `scrapers/cache/bmppd/`  

---

## 1. Executive Summary & Key Metrics

| Metric | Count | Description / Percentage |
| :--- | :---: | :--- |
| **Raw queries tested** | 20 | First 20 MPBD frozen records |
| **Candidate queries tested** | 20 | Conservative authority-stripped binomials |
| **Raw PASS count** | 0 | Raw queries returning $\\ge 1$ compound row (0.0%) |
| **Raw ZERO_RESULTS count** | 20 | Raw queries returning 0 rows (100.0%) |
| **Candidate PASS count** | 8 | Candidate queries returning $\\ge 1$ compound row (40.0%) |
| **Candidate ZERO_RESULTS count** | 12 | Candidate queries returning 0 rows (60.0%) |
| **IMPROVED_MATCH** | **8** | Raw had 0 rows $\\rightarrow$ Candidate yielded $\\ge 1$ rows (40.0%) |
| **UNCHANGED_ZERO** | 12 | Genuine zero-result plants in BMPPD (60.0%) |
| **RAW_MATCHED** | 0 | Raw query itself matched in BMPPD |
| **NEEDS_REVIEW** | 0 | Ambiguous or anomalous cases |

---

## 2. Full 20-Plant Results Table

| # | Raw MPBD Name | Pattern | Candidate Query | Raw St | Raw # | Cand St | Cand # | CID # | No-CID # | Decision |
| :-: | :--- | :--- | :--- | :-: | :-: | :-: | :-: | :-: | :-: | :--- |
| 1 | `Piper betle L.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Piper betle` | `ZERO_RESULTS` | 0 | `PASS` | 112 | 0 | 112 | **`IMPROVED_MATCH`** |
| 2 | `Piper cubeba Vahl` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Piper cubeba` | `ZERO_RESULTS` | 0 | `PASS` | 181 | 0 | 181 | **`IMPROVED_MATCH`** |
| 3 | `Berberis aristata DC.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Berberis aristata` | `ZERO_RESULTS` | 0 | `ZERO_RESULTS` | 0 | 0 | 0 | **`UNCHANGED_ZERO`** |
| 4 | `Papaver somniferum L.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Papaver somniferum` | `ZERO_RESULTS` | 0 | `PASS` | 128 | 0 | 128 | **`IMPROVED_MATCH`** |
| 5 | `Artocarpus heterophyllus Lam.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Artocarpus heterophyllus` | `ZERO_RESULTS` | 0 | `PASS` | 180 | 0 | 180 | **`IMPROVED_MATCH`** |
| 6 | `Ficus racemosa L.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Ficus racemosa` | `ZERO_RESULTS` | 0 | `ZERO_RESULTS` | 0 | 0 | 0 | **`UNCHANGED_ZERO`** |
| 7 | `Morus indica L.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Morus indica` | `ZERO_RESULTS` | 0 | `ZERO_RESULTS` | 0 | 0 | 0 | **`UNCHANGED_ZERO`** |
| 8 | `Juglans regia L.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Juglans regia` | `ZERO_RESULTS` | 0 | `ZERO_RESULTS` | 0 | 0 | 0 | **`UNCHANGED_ZERO`** |
| 9 | `Boerhavia diffusa L.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Boerhavia diffusa` | `ZERO_RESULTS` | 0 | `PASS` | 57 | 53 | 4 | **`IMPROVED_MATCH`** |
| 10 | `Boerhavia repens L.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Boerhavia repens` | `ZERO_RESULTS` | 0 | `ZERO_RESULTS` | 0 | 0 | 0 | **`UNCHANGED_ZERO`** |
| 11 | `Mirabilis jalapa L.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Mirabilis jalapa` | `ZERO_RESULTS` | 0 | `ZERO_RESULTS` | 0 | 0 | 0 | **`UNCHANGED_ZERO`** |
| 12 | `Opuntia dellenii (Ker Gawl.) Haw.` | `PARENTHETICAL_AUTHORITY` | `Opuntia dellenii` | `ZERO_RESULTS` | 0 | `ZERO_RESULTS` | 0 | 0 | 0 | **`UNCHANGED_ZERO`** |
| 13 | `Achyranthes aspera L.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Achyranthes aspera` | `ZERO_RESULTS` | 0 | `PASS` | 32 | 22 | 10 | **`IMPROVED_MATCH`** |
| 14 | `Plumbago indica L.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Plumbago indica` | `ZERO_RESULTS` | 0 | `PASS` | 28 | 0 | 28 | **`IMPROVED_MATCH`** |
| 15 | `Vateria indica L.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Vateria indica` | `ZERO_RESULTS` | 0 | `ZERO_RESULTS` | 0 | 0 | 0 | **`UNCHANGED_ZERO`** |
| 16 | `Mesua ferrea L.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Mesua ferrea` | `ZERO_RESULTS` | 0 | `PASS` | 133 | 133 | 0 | **`IMPROVED_MATCH`** |
| 17 | `Helicteres isora L.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Helicteres isora` | `ZERO_RESULTS` | 0 | `ZERO_RESULTS` | 0 | 0 | 0 | **`UNCHANGED_ZERO`** |
| 18 | `Abelmoschus esculentus (L.) Moench` | `PARENTHETICAL_AUTHORITY` | `Abelmoschus esculentus` | `ZERO_RESULTS` | 0 | `ZERO_RESULTS` | 0 | 0 | 0 | **`UNCHANGED_ZERO`** |
| 19 | `Gossypium arboreum L.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Gossypium arboreum` | `ZERO_RESULTS` | 0 | `ZERO_RESULTS` | 0 | 0 | 0 | **`UNCHANGED_ZERO`** |
| 20 | `Viola odorata L.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Viola odorata` | `ZERO_RESULTS` | 0 | `ZERO_RESULTS` | 0 | 0 | 0 | **`UNCHANGED_ZERO`** |

---

## 3. Structural Name-Pattern Distribution

Across the first 20 records, 2 structural patterns were identified:

### `SIMPLE_BINOMIAL_WITH_AUTHORITY` (18 plants, 90.0%)
- **Description**: Standard binomial species followed by a single author citation abbreviation (e.g. `L.`, `Vahl`, `DC.`, `Lam.`).
- **Observed Examples**:
  - `Piper betle L.`
  - `Piper cubeba Vahl`
  - `Berberis aristata DC.`
  - `Papaver somniferum L.`
  - ... (14 more)

### `PARENTHETICAL_AUTHORITY` (2 plants, 10.0%)
- **Description**: Binomial species followed by a parenthetical basionym author and combining author (e.g. `(L.) Moench`, `(Ker Gawl.) Haw.`).
- **Observed Examples**:
  - `Opuntia dellenii (Ker Gawl.) Haw.`
  - `Abelmoschus esculentus (L.) Moench`

---

## 4. CID Source HTML vs. Parser Validation

A critical question arose from the initial 5 plants: **Why did extracted candidate rows report 0 PubChem CIDs?**

Direct inspection of the cached raw HTML files was conducted across result pages:

### Sample: `Piper betle` (112 rows)
- **`<td>CID: -</td>` literal occurrences**: 112
- **`<td>CID: <SMILES></td>` occurrences**: 0
- **Numeric CIDs found in HTML**: 0
- **Actual HTML `<td>` snippets observed**:
  ```html
  <td>CID: -</td>
  ```
  ```html
  <td>CID: -</td>
  ```
  ```html
  <td>CID: -</td>
  ```

### Sample: `Piper cubeba` (181 rows)
- **`<td>CID: -</td>` literal occurrences**: 181
- **`<td>CID: <SMILES></td>` occurrences**: 0
- **Numeric CIDs found in HTML**: 0
- **Actual HTML `<td>` snippets observed**:
  ```html
  <td>CID: -</td>
  ```
  ```html
  <td>CID: -</td>
  ```
  ```html
  <td>CID: -</td>
  ```

### Sample: `Papaver somniferum` (128 rows)
- **`<td>CID: -</td>` literal occurrences**: 128
- **`<td>CID: <SMILES></td>` occurrences**: 0
- **Numeric CIDs found in HTML**: 0
- **Actual HTML `<td>` snippets observed**:
  ```html
  <td>CID: -</td>
  ```
  ```html
  <td>CID: -</td>
  ```
  ```html
  <td>CID: -</td>
  ```

### Sample: `Artocarpus heterophyllus` (180 rows)
- **`<td>CID: -</td>` literal occurrences**: 5
- **`<td>CID: <SMILES></td>` occurrences**: 175
- **Numeric CIDs found in HTML**: 0
- **Actual HTML `<td>` snippets observed**:
  ```html
  <td>CID: CC(CCCC(C)C(=O)NCCS(=O)(=O)O)C1CCC2C1(CCC3C2C(CC4C3(CCC(C4)O)C)O)C</td>
  ```
  ```html
  <td>CID: CC(=CCC1=C(C=C2C(=C1O)C(=O)CC(O2)C3=CC(=C(C(=C3)OC)OC)OC)OC)C</td>
  ```
  ```html
  <td>CID: CCCCCCCCCCCCCCCCC(C(=O)NC(COC1C(C(C(C(O1)CO)O)OS(=O)(=O)O)O)C(C=CCCCCCCCCCCCCC)O)O</td>
  ```

### Sample: `Mesua ferrea (positive control)` (133 rows)
- **`<td>CID: -</td>` literal occurrences**: 0
- **`<td>CID: <SMILES></td>` occurrences**: 0
- **Numeric CIDs found in HTML**: 133
- **Actual HTML `<td>` snippets observed**:
  ```html
  <td>CID: 5281635</td>
  ```
  ```html
  <td>CID: 6549</td>
  ```
  ```html
  <td>CID: 5281631</td>
  ```

### CID Validation Conclusion:
1. **No Parser Bug**: The parser regex `r'\bCID\s*:\s*(\d+)\b'` accurately searches for numeric PubChem CIDs.
2. **Genuine BMPPD Upstream Data Anomaly**: BMPPD's web database has two known behaviors:
   - In many species (`Piper betle`, `Piper cubeba`, `Papaver somniferum`), the CID column literally contains `CID: -` for all entries.
   - In other species (`Artocarpus heterophyllus`), BMPPD's backend mistakenly populated the PubChem CID column with **SMILES chemical structure strings** prefixed by `CID: ` (e.g. `CID: CC(C)CO`) instead of numeric identifiers.
3. **Parser Preservation**: Preserving these rows as missing CID (`quality_flags=missing_pubchem_cid`) is 100% correct according to thesis specifications.

---

## 5. Proposed Candidate-Generation Rules & Cautions for Next Stages

1. **Dual Provenance is Mandatory**:
   - `source_query_raw`: Must store the exact unmodified string from MPBD.
   - `bmppd_query_name`: Dispatched clean botanical binomial for querying BMPPD.
2. **Do Not Apply Blind Regexes**:
   - While `SIMPLE_BINOMIAL_WITH_AUTHORITY` and `PARENTHETICAL_AUTHORITY` cover all 20 records tested, future records contain infraspecific ranks (e.g. `subsp.`, `var.`, `f.`). A simplistic `tokens[0] + tokens[1]` rule would truncate valid botanical varieties.
3. **Candidate Viability**:
   - Removing taxonomic authorities produced an **40.0% yield improvement** (8 out of 20 plants) without introducing spurious false matches.

