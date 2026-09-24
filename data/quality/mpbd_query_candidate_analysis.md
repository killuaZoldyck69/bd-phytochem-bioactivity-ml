# MPBD Query Candidate Syntactic Structure Analysis Report

**Stage**: 6C — Offline Name-Structure & Syntactic Analysis  
**Execution Mode**: COMPLETELY OFFLINE (0 network requests)  
**Source File**: `data/raw/mpbd/mpbd_plant_index.csv` (strictly read-only)  
**Frozen Dataset SHA-256**: `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` (Verified Identical)  
**Total Records Analyzed**: `916`  

---

## 1. Executive Summary & Distribution Overview

### Pattern Distribution

| Pattern Category | Count | Percentage | Description |
| :--- | :---: | :---: | :--- |
| **`SIMPLE_BINOMIAL_WITH_AUTHORITY`** | **502** | 54.80% | Binomial species followed by a single author abbreviation token. |
| **`BINOMIAL_PARENTHETICAL_AUTHORITY`** | **335** | 36.57% | Binomial species followed by a parenthetical basionym author citation. |
| **`INFRASPECIFIC_SUBSP`** | **3** | 0.33% | Botanical names containing the taxonomic rank 'subsp.' (subspecies). |
| **`INFRASPECIFIC_VAR`** | **7** | 0.76% | Botanical names containing the taxonomic rank 'var.' (variety). |
| **`INFRASPECIFIC_FORM`** | **0** | 0.00% | Botanical names containing the taxonomic rank 'f.' (forma). |
| **`MULTI_AUTHOR_OR_COMPLEX`** | **57** | 6.22% | Binomial species with multiple, connecting ('ex', '&'), or compound authors. |
| **`POSSIBLY_NO_AUTHORITY`** | **0** | 0.00% | Names appearing to contain only two tokens without an author citation. |
| **`OTHER_REVIEW`** | **12** | 1.31% | Anomalous, fused, or malformed strings requiring manual botanical review. |

### Candidate Status Distribution

| Candidate Status | Count | Percentage | Definition |
| :--- | :---: | :---: | :--- |
| **`SAFE_CANDIDATE`** | **904** | 98.69% | Deterministic structural transformation applied with high confidence. |
| **`NEEDS_REVIEW`** | **12** | 1.31% | Structure is ambiguous, fused, or malformed; requires manual review. |
| **`NO_TRANSFORMATION`** | **0** | 0.00% | No authority-like suffix was detected. |

---

## 2. Examples from Every Structural Pattern

For each category, up to 5 representative records are detailed below:

### Pattern: `SIMPLE_BINOMIAL_WITH_AUTHORITY` (Total: 502)

- **Index**: `1`
  - **RAW**: `Piper betle L.`
  - **CANDIDATE**: `Piper betle`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Removed single botanical author abbreviation suffix.

- **Index**: `2`
  - **RAW**: `Piper cubeba Vahl`
  - **CANDIDATE**: `Piper cubeba`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Removed single botanical author abbreviation suffix.

- **Index**: `3`
  - **RAW**: `Berberis aristata DC.`
  - **CANDIDATE**: `Berberis aristata`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Removed single botanical author abbreviation suffix.

- **Index**: `4`
  - **RAW**: `Papaver somniferum L.`
  - **CANDIDATE**: `Papaver somniferum`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Removed single botanical author abbreviation suffix.

- **Index**: `5`
  - **RAW**: `Artocarpus heterophyllus Lam.`
  - **CANDIDATE**: `Artocarpus heterophyllus`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Removed single botanical author abbreviation suffix.

### Pattern: `BINOMIAL_PARENTHETICAL_AUTHORITY` (Total: 335)

- **Index**: `12`
  - **RAW**: `Opuntia dellenii (Ker Gawl.) Haw.`
  - **CANDIDATE**: `Opuntia dellenii`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Extracted clean genus and species epithet preceding parenthetical basionym author citation.

- **Index**: `18`
  - **RAW**: `Abelmoschus esculentus (L.) Moench`
  - **CANDIDATE**: `Abelmoschus esculentus`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Extracted clean genus and species epithet preceding parenthetical basionym author citation.

- **Index**: `21`
  - **RAW**: `Benincasa hispida (Thunb.) Cogn.`
  - **CANDIDATE**: `Benincasa hispida`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Extracted clean genus and species epithet preceding parenthetical basionym author citation.

- **Index**: `22`
  - **RAW**: `Citrullus colocynthis (L.) Schard.`
  - **CANDIDATE**: `Citrullus colocynthis`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Extracted clean genus and species epithet preceding parenthetical basionym author citation.

- **Index**: `24`
  - **RAW**: `Mukia maderaspatana (L.) M. Roem`
  - **CANDIDATE**: `Mukia maderaspatana`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Extracted clean genus and species epithet preceding parenthetical basionym author citation.

### Pattern: `INFRASPECIFIC_SUBSP` (Total: 3)

- **Index**: `26`
  - **RAW**: `Raphanus raphanistrum subsp. SATIVUS(L.) Domin.`
  - **CANDIDATE**: `Raphanus raphanistrum subsp. SATIVUS`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Preserved species binomial, subsp. rank, and infraspecific epithet; stripped parenthetical/combining authors.

- **Index**: `31`
  - **RAW**: `Acacia nilotica (L.) Delile subsp. INDICA(Benth) Brenan`
  - **CANDIDATE**: `Acacia nilotica subsp. INDICA`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Preserved species binomial, subsp. rank, and infraspecific epithet; stripped parenthetical/combining authors.

- **Index**: `839`
  - **RAW**: `Drymaria cordata subsp.diandra (Blume) J.A.Duke.`
  - **CANDIDATE**: `Drymaria cordata subsp. diandra`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Preserved species binomial, subsp. rank, and infraspecific epithet; stripped parenthetical/combining authors.

### Pattern: `INFRASPECIFIC_VAR` (Total: 7)

- **Index**: `180`
  - **RAW**: `Trapa natans var. bispinosa (Roxb.) Makino`
  - **CANDIDATE**: `Trapa natans var. bispinosa`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Preserved species binomial, var. rank, and varietal epithet; stripped species author and varietal author.

- **Index**: `344`
  - **RAW**: `Ophiorrhiza rugosa VAR. PROSTRATA (D.Don) Deb & Mondal.`
  - **CANDIDATE**: `Ophiorrhiza rugosa var. PROSTRATA`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Preserved species binomial, var. rank, and varietal epithet; stripped species author and varietal author.

- **Index**: `412`
  - **RAW**: `Madhuca longifolia VAR. LATIFOLIA (Roxb.) A.Chev.`
  - **CANDIDATE**: `Madhuca longifolia var. LATIFOLIA`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Preserved species binomial, var. rank, and varietal epithet; stripped species author and varietal author.

- **Index**: `546`
  - **RAW**: `Ficus BENJAMINA L. var. comosa (Roxb.) Kurz.`
  - **CANDIDATE**: `Ficus BENJAMINA var. comosa`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Preserved species binomial, var. rank, and varietal epithet; stripped species author and varietal author.

- **Index**: `561`
  - **RAW**: `Erythrina VARIEGATA L. var. orientalis (L.) Merr.`
  - **CANDIDATE**: `Erythrina VARIEGATA var. orientalis`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Preserved species binomial, var. rank, and varietal epithet; stripped species author and varietal author.

### Pattern: `INFRASPECIFIC_FORM` (Total: 0)

*No records in this dataset matched this pattern.*
*(Note: All 55 occurrences of 'f.' in MPBD represent author filius citations (e.g. 'Hook. f.', 'L. f.', 'Burm. f.') or author initials ('F. Muell.'), rather than the botanical rank forma. See Section 3 for full analysis.)*

### Pattern: `MULTI_AUTHOR_OR_COMPLEX` (Total: 57)

- **Index**: `23`
  - **RAW**: `Momordica dioica Roxb. ex Willd.`
  - **CANDIDATE**: `Momordica dioica`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Preserved first two tokens as binomial; stripped compound or multi-token author citation.

- **Index**: `38`
  - **RAW**: `Pterocarpus SANTALINUS L. f.`
  - **CANDIDATE**: `Pterocarpus SANTALINUS`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Preserved first two tokens as binomial; stripped compound or multi-token author citation.

- **Index**: `67`
  - **RAW**: `Semecarpus anacardium L. F.`
  - **CANDIDATE**: `Semecarpus anacardium`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Preserved first two tokens as binomial; stripped compound or multi-token author citation.

- **Index**: `73`
  - **RAW**: `Anethum sowa Roxb.ex Fleming`
  - **CANDIDATE**: `Anethum sowa`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Preserved first two tokens as binomial; stripped compound or multi-token author citation.

- **Index**: `77`
  - **RAW**: `Strychnos potatorum L. f.`
  - **CANDIDATE**: `Strychnos potatorum`
  - **STATUS**: `SAFE_CANDIDATE`
  - **NOTES**: Preserved first two tokens as binomial; stripped compound or multi-token author citation.

### Pattern: `POSSIBLY_NO_AUTHORITY` (Total: 0)

*No records in this dataset matched this pattern.*
*(Note: Every record in the frozen MPBD inventory originally contained an author citation or fused author abbreviation. Zero bare binomials exist in the source data.)*

### Pattern: `OTHER_REVIEW` (Total: 12)

- **Index**: `316`
  - **RAW**: `. PHYLLANTHUS EMBLICA L. (Euphorbiaceae)`
  - **CANDIDATE**: `PHYLLANTHUS EMBLICA`
  - **STATUS**: `NEEDS_REVIEW`
  - **NOTES**: Leading period and/or appended family name in source record; requires manual review.

- **Index**: `382`
  - **RAW**: `Mollugo PENTAPHYLLA L. ()`
  - **CANDIDATE**: `Mollugo PENTAPHYLLA`
  - **STATUS**: `NEEDS_REVIEW`
  - **NOTES**: Trailing empty parentheses in source record; requires manual review.

- **Index**: `391`
  - **RAW**: `Mesua NAGESSARIUM (Burm.) Kost. ()`
  - **CANDIDATE**: `Mesua NAGESSARIUM`
  - **STATUS**: `NEEDS_REVIEW`
  - **NOTES**: Trailing empty parentheses in source record; requires manual review.

- **Index**: `460`
  - **RAW**: `. JATROPHA CURCAS L.`
  - **CANDIDATE**: `JATROPHA CURCAS`
  - **STATUS**: `NEEDS_REVIEW`
  - **NOTES**: Leading period and/or appended family name in source record; requires manual review.

- **Index**: `802`
  - **RAW**: `Solenaamplexicaulis(lam.) gandhi.`
  - **CANDIDATE**: `Solenaamplexicaulis(lam.) gandhi.`
  - **STATUS**: `NEEDS_REVIEW`
  - **NOTES**: Genus and species epithet are fused without a space; cannot safely decompose without botanical knowledge.

---

## 3. Special Infraspecific Taxa & Botanical Author 'f.' Analysis

All names containing `subsp.`, `var.`, and `f.` were extracted into [`data/quality/mpbd_infraspecific_review.csv`](file:///f:/bmppd-thesis/data/quality/mpbd_infraspecific_review.csv).

### Infraspecific Subspecies (`subsp.`) — 3 Records
All 3 records were successfully transformed preserving the species binomial, the rank `subsp.`, and the infraspecific epithet:

- **[26] RAW**: `Raphanus raphanistrum subsp. SATIVUS(L.) Domin.`  
  **CANDIDATE**: `Raphanus raphanistrum subsp. SATIVUS`  
  **STATUS**: `SAFE_CANDIDATE`  
  **NOTES**: Preserved species binomial, subsp. rank, and infraspecific epithet; stripped parenthetical/combining authors.

- **[31] RAW**: `Acacia nilotica (L.) Delile subsp. INDICA(Benth) Brenan`  
  **CANDIDATE**: `Acacia nilotica subsp. INDICA`  
  **STATUS**: `SAFE_CANDIDATE`  
  **NOTES**: Preserved species binomial, subsp. rank, and infraspecific epithet; stripped parenthetical/combining authors.

- **[839] RAW**: `Drymaria cordata subsp.diandra (Blume) J.A.Duke.`  
  **CANDIDATE**: `Drymaria cordata subsp. diandra`  
  **STATUS**: `SAFE_CANDIDATE`  
  **NOTES**: Preserved species binomial, subsp. rank, and infraspecific epithet; stripped parenthetical/combining authors.

### Infraspecific Varieties (`var.`) — 7 Records
All 7 records were successfully transformed preserving the species binomial, the rank `var.`, and the varietal epithet while stripping both species authors and varietal authors:

- **[180] RAW**: `Trapa natans var. bispinosa (Roxb.) Makino`  
  **CANDIDATE**: `Trapa natans var. bispinosa`  
  **STATUS**: `SAFE_CANDIDATE`  
  **NOTES**: Preserved species binomial, var. rank, and varietal epithet; stripped species author and varietal author.

- **[344] RAW**: `Ophiorrhiza rugosa VAR. PROSTRATA (D.Don) Deb & Mondal.`  
  **CANDIDATE**: `Ophiorrhiza rugosa var. PROSTRATA`  
  **STATUS**: `SAFE_CANDIDATE`  
  **NOTES**: Preserved species binomial, var. rank, and varietal epithet; stripped species author and varietal author.

- **[412] RAW**: `Madhuca longifolia VAR. LATIFOLIA (Roxb.) A.Chev.`  
  **CANDIDATE**: `Madhuca longifolia var. LATIFOLIA`  
  **STATUS**: `SAFE_CANDIDATE`  
  **NOTES**: Preserved species binomial, var. rank, and varietal epithet; stripped species author and varietal author.

- **[546] RAW**: `Ficus BENJAMINA L. var. comosa (Roxb.) Kurz.`  
  **CANDIDATE**: `Ficus BENJAMINA var. comosa`  
  **STATUS**: `SAFE_CANDIDATE`  
  **NOTES**: Preserved species binomial, var. rank, and varietal epithet; stripped species author and varietal author.

- **[561] RAW**: `Erythrina VARIEGATA L. var. orientalis (L.) Merr.`  
  **CANDIDATE**: `Erythrina VARIEGATA var. orientalis`  
  **STATUS**: `SAFE_CANDIDATE`  
  **NOTES**: Preserved species binomial, var. rank, and varietal epithet; stripped species author and varietal author.

- **[564] RAW**: `Cissampelos PAREIRA L. Var. hirsuta (Buch. ex Dc.) Forman`  
  **CANDIDATE**: `Cissampelos PAREIRA var. hirsuta`  
  **STATUS**: `SAFE_CANDIDATE`  
  **NOTES**: Preserved species binomial, var. rank, and varietal epithet; stripped species author and varietal author.

- **[586] RAW**: `Diospyros MONTANA Roxb. Var. CORDIFOLIA (Roxb.) Heirn.`  
  **CANDIDATE**: `Diospyros MONTANA var. CORDIFOLIA`  
  **STATUS**: `SAFE_CANDIDATE`  
  **NOTES**: Preserved species binomial, var. rank, and varietal epithet; stripped species author and varietal author.

### Detailed Finding on Botanical Author 'f.' vs. Forma
A critical botanical finding emerges from analyzing all 55 records containing `f.`:  
**Zero records** contain `f.` as the taxonomic rank *forma*. Instead, 100% of these records represent:
1. **Filius Author Citations**: `L. f.` (Linnaeus the Younger), `Hook. f.` (Hooker the Younger), `Burm. f.` (Burman the Younger), `Forst. f.` (Forster the Younger), `Schult. f.`, `Hallier f.`.
2. **Author Initials**: `F. Muell.` (Ferdinand von Mueller), `C.F Gaertn.`.

Because these are author citations and not infraspecific ranks, stripping them to yield the clean species binomial (e.g. `Pterocarpus SANTALINUS L. f.` $\rightarrow$ `Pterocarpus SANTALINUS`) is botanically accurate and required for BMPPD query matching.

---

## 4. Unsafe & Ambiguous Cases (`NEEDS_REVIEW` — 12 Records)

The following 12 records cannot be deterministically transformed without risk of corrupting botanical identity or failing query resolution:

- **[316] RAW**: `. PHYLLANTHUS EMBLICA L. (Euphorbiaceae)`  
  **CANDIDATE**: `PHYLLANTHUS EMBLICA`  
  **ISSUE**: Leading period and/or appended family name in source record; requires manual review.

- **[382] RAW**: `Mollugo PENTAPHYLLA L. ()`  
  **CANDIDATE**: `Mollugo PENTAPHYLLA`  
  **ISSUE**: Trailing empty parentheses in source record; requires manual review.

- **[391] RAW**: `Mesua NAGESSARIUM (Burm.) Kost. ()`  
  **CANDIDATE**: `Mesua NAGESSARIUM`  
  **ISSUE**: Trailing empty parentheses in source record; requires manual review.

- **[460] RAW**: `. JATROPHA CURCAS L.`  
  **CANDIDATE**: `JATROPHA CURCAS`  
  **ISSUE**: Leading period and/or appended family name in source record; requires manual review.

- **[802] RAW**: `Solenaamplexicaulis(lam.) gandhi.`  
  **CANDIDATE**: `Solenaamplexicaulis(lam.) gandhi.`  
  **ISSUE**: Genus and species epithet are fused without a space; cannot safely decompose without botanical knowledge.

- **[807] RAW**: `Sida orientaliscav.`  
  **CANDIDATE**: `Sida orientaliscav.`  
  **ISSUE**: Author abbreviation is fused directly to species epithet without space delimiter; requires manual decomposition.

- **[809] RAW**: `Sidacordata(burm.f.) borss.waalk.`  
  **CANDIDATE**: `Sidacordata(burm.f.) borss.waalk.`  
  **ISSUE**: Genus and species epithet are fused without a space; cannot safely decompose without botanical knowledge.

- **[822] RAW**: `Elaeocarpus serratusl.`  
  **CANDIDATE**: `Elaeocarpus serratusl.`  
  **ISSUE**: Author abbreviation is fused directly to species epithet without space delimiter; requires manual decomposition.

- **[865] RAW**: `Cardiospermum HALICACABUML.`  
  **CANDIDATE**: `Cardiospermum HALICACABUML.`  
  **ISSUE**: Author abbreviation is fused directly to species epithet without space delimiter; requires manual decomposition.

- **[884] RAW**: `Celosia CRISTATA L.(SAME AS 161)`  
  **CANDIDATE**: `Celosia CRISTATA`  
  **ISSUE**: Source record contains administrative annotation '(SAME AS ...)' rather than botanical authority.

- **[886] RAW**: `Piperboehmeriifolium(miq.) wall. ex C. DC.`  
  **CANDIDATE**: `Piperboehmeriifolium(miq.) wall. ex C. DC.`  
  **ISSUE**: Genus and species epithet are fused without a space; cannot safely decompose without botanical knowledge.

- **[894] RAW**: `Desmos chinensislour.`  
  **CANDIDATE**: `Desmos chinensislour.`  
  **ISSUE**: Author abbreviation is fused directly to species epithet without space delimiter; requires manual decomposition.

### Categories of Review Cases:
1. **Fused Genus + Species** (3 records: `Solenaamplexicaulis(lam.) gandhi.`, `Sidacordata(burm.f.) borss.waalk.`, `Piperboehmeriifolium(miq.) wall. ex C. DC.`):  
   Lacks a space between genus and species. Automated whitespace splitting cannot separate them safely.
2. **Fused Species + Author** (4 records: `Sida orientaliscav.`, `Elaeocarpus serratusl.`, `Cardiospermum HALICACABUML.`, `Desmos chinensislour.`):  
   Author citation (`cav.`, `l.`, `L.`, `lour.`) is merged directly to the end of the epithet.
3. **Leading / Trailing Punctuation Anomalies** (5 records: `. PHYLLANTHUS EMBLICA L. (Euphorbiaceae)`, `Mollugo PENTAPHYLLA L. ()`, `Mesua NAGESSARIUM (Burm.) Kost. ()`, `. JATROPHA CURCAS L.`, `Celosia CRISTATA L.(SAME AS 161)`):  
   Malformed formatting in source MPBD catalog including extraneous periods, empty parentheses, or administrative cross-reference notes.

---

## 5. Proposed Query-Transformation Architecture for Next Stages

1. **904 Safe Transformations (98.69%)**:  
   The conservative pattern-based rules developed here successfully cover 904 out of 916 records with high confidence and deterministic behavior.
2. **Dual-Column Provenance Preservation**:  
   In all output datasets, `source_query_raw` must strictly retain the frozen MPBD string, while `bmppd_query_name` receives the candidate query.
3. **Explicit Handling of the 12 Edge Cases**:  
   The 12 `NEEDS_REVIEW` records should be maintained in an explicit, auditable override lookup table rather than attempting complex, fragile heuristic regexes.

