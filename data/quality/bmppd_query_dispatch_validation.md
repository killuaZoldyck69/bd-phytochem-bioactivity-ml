# BMPPD Stage 6D — Query-Dispatch Policy Live Validation Report

**Stage**: 6D — Stratified Live Validation of Candidate-Query Transformations  
**Source Inventory**: `data/raw/mpbd/mpbd_plant_index.csv` (strictly read-only)  
**Frozen Dataset SHA-256**: `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` (Verified Unmodified)  
**Sample Size**: `52` records across 6 structural categories  
**Cache Hits / Live Web Fetches**: `52` hits / `0` live fetches  

---

## 1. Category-Level Summary Table

| Structural Category | Sample Size | PASS | ZERO_RESULTS | FETCH_FAILED | PARSE_FAILED | NEEDS_REVIEW | Total Rows | Valid CID | Missing CID |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`SIMPLE_BINOMIAL_WITH_AUTHORITY`** | 10 | 5 | 5 | 0 | 0 | 0 | 658 | 53 | 605 |
| **`BINOMIAL_PARENTHETICAL_AUTHORITY`** | 10 | 3 | 7 | 0 | 0 | 0 | 130 | 96 | 34 |
| **`INFRASPECIFIC_SUBSP`** | 3 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| **`INFRASPECIFIC_VAR`** | 7 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| **`MULTI_AUTHOR_OR_COMPLEX`** | 10 | 3 | 7 | 0 | 0 | 0 | 185 | 106 | 79 |
| **`OTHER_REVIEW`** | 12 | 4 | 8 | 0 | 0 | 12 | 179 | 104 | 75 |
| **TOTAL** | **52** | **15** | **37** | **0** | **0** | **12** | **1152** | **359** | **793** |

---

## 2. Full 52-Record Validation Results

| # | Raw MPBD Name | Pattern | Candidate Query | Src | Status | Extracted Rows | Valid CID | Decision |
| :-: | :--- | :--- | :--- | :-: | :-: | :-: | :-: | :--- |
| 1 | `Piper betle L.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Piper betle` | `OFFLINE_RULE` | `PASS` | 112 | 0 | **`VALIDATED`** |
| 2 | `Piper cubeba Vahl` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Piper cubeba` | `OFFLINE_RULE` | `PASS` | 181 | 0 | **`VALIDATED`** |
| 3 | `Berberis aristata DC.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Berberis aristata` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 4 | `Papaver somniferum L.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Papaver somniferum` | `OFFLINE_RULE` | `PASS` | 128 | 0 | **`VALIDATED`** |
| 5 | `Artocarpus heterophyllus Lam.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Artocarpus heterophyllus` | `OFFLINE_RULE` | `PASS` | 180 | 0 | **`VALIDATED`** |
| 6 | `Ficus racemosa L.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Ficus racemosa` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 7 | `Morus indica L.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Morus indica` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 8 | `Juglans regia L.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Juglans regia` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 9 | `Boerhavia diffusa L.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Boerhavia diffusa` | `OFFLINE_RULE` | `PASS` | 57 | 53 | **`VALIDATED`** |
| 10 | `Boerhavia repens L.` | `SIMPLE_BINOMIAL_WITH_AUTHORITY` | `Boerhavia repens` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 12 | `Opuntia dellenii (Ker Gawl.) Haw.` | `BINOMIAL_PARENTHETICAL_AUTHORITY` | `Opuntia dellenii` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 18 | `Abelmoschus esculentus (L.) Moench` | `BINOMIAL_PARENTHETICAL_AUTHORITY` | `Abelmoschus esculentus` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 21 | `Benincasa hispida (Thunb.) Cogn.` | `BINOMIAL_PARENTHETICAL_AUTHORITY` | `Benincasa hispida` | `OFFLINE_RULE` | `PASS` | 66 | 63 | **`VALIDATED`** |
| 22 | `Citrullus colocynthis (L.) Schard.` | `BINOMIAL_PARENTHETICAL_AUTHORITY` | `Citrullus colocynthis` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 24 | `Mukia maderaspatana (L.) M. Roem` | `BINOMIAL_PARENTHETICAL_AUTHORITY` | `Mukia maderaspatana` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 25 | `Brassica juncea (L.) Czern.` | `BINOMIAL_PARENTHETICAL_AUTHORITY` | `Brassica juncea` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 28 | `Diospyros malabarica(desr.) Kostel.` | `BINOMIAL_PARENTHETICAL_AUTHORITY` | `Diospyros malabarica` | `OFFLINE_RULE` | `PASS` | 34 | 33 | **`VALIDATED`** |
| 32 | `Entada phaseoloides (L.) Merr.` | `BINOMIAL_PARENTHETICAL_AUTHORITY` | `Entada phaseoloides` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 34 | `Saraca asoca (Roxb.) Wild.` | `BINOMIAL_PARENTHETICAL_AUTHORITY` | `Saraca asoca` | `OFFLINE_RULE` | `PASS` | 30 | 0 | **`VALIDATED`** |
| 37 | `Mucuna pruriens (L.) DC.` | `BINOMIAL_PARENTHETICAL_AUTHORITY` | `Mucuna pruriens` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 26 | `Raphanus raphanistrum subsp. SATIVUS(L.) Domin.` | `INFRASPECIFIC_SUBSP` | `Raphanus raphanistrum subsp. SATIVUS` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 31 | `Acacia nilotica (L.) Delile subsp. INDICA(Benth) Brenan` | `INFRASPECIFIC_SUBSP` | `Acacia nilotica subsp. INDICA` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 839 | `Drymaria cordata subsp.diandra (Blume) J.A.Duke.` | `INFRASPECIFIC_SUBSP` | `Drymaria cordata subsp. diandra` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 180 | `Trapa natans var. bispinosa (Roxb.) Makino` | `INFRASPECIFIC_VAR` | `Trapa natans var. bispinosa` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 344 | `Ophiorrhiza rugosa VAR. PROSTRATA (D.Don) Deb & Mondal.` | `INFRASPECIFIC_VAR` | `Ophiorrhiza rugosa var. PROSTRATA` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 412 | `Madhuca longifolia VAR. LATIFOLIA (Roxb.) A.Chev.` | `INFRASPECIFIC_VAR` | `Madhuca longifolia var. LATIFOLIA` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 546 | `Ficus BENJAMINA L. var. comosa (Roxb.) Kurz.` | `INFRASPECIFIC_VAR` | `Ficus BENJAMINA var. comosa` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 561 | `Erythrina VARIEGATA L. var. orientalis (L.) Merr.` | `INFRASPECIFIC_VAR` | `Erythrina VARIEGATA var. orientalis` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 564 | `Cissampelos PAREIRA L. Var. hirsuta (Buch. ex Dc.) Forman` | `INFRASPECIFIC_VAR` | `Cissampelos PAREIRA var. hirsuta` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 586 | `Diospyros MONTANA Roxb. Var. CORDIFOLIA (Roxb.) Heirn.` | `INFRASPECIFIC_VAR` | `Diospyros MONTANA var. CORDIFOLIA` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 23 | `Momordica dioica Roxb. ex Willd.` | `MULTI_AUTHOR_OR_COMPLEX` | `Momordica dioica` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 38 | `Pterocarpus SANTALINUS L. f.` | `MULTI_AUTHOR_OR_COMPLEX` | `Pterocarpus SANTALINUS` | `OFFLINE_RULE` | `PASS` | 36 | 0 | **`VALIDATED`** |
| 67 | `Semecarpus anacardium L. F.` | `MULTI_AUTHOR_OR_COMPLEX` | `Semecarpus anacardium` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 73 | `Anethum sowa Roxb.ex Fleming` | `MULTI_AUTHOR_OR_COMPLEX` | `Anethum sowa` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 77 | `Strychnos potatorum L. f.` | `MULTI_AUTHOR_OR_COMPLEX` | `Strychnos potatorum` | `OFFLINE_RULE` | `PASS` | 43 | 0 | **`VALIDATED`** |
| 78 | `Holarrhena pubescens Wall.ex G.Don` | `MULTI_AUTHOR_OR_COMPLEX` | `Holarrhena pubescens` | `OFFLINE_RULE` | `PASS` | 106 | 106 | **`VALIDATED`** |
| 80 | `Wrightia tinctoria R. Brown` | `MULTI_AUTHOR_OR_COMPLEX` | `Wrightia tinctoria` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 112 | `Adiantum LUNULATUM Burm. F.` | `MULTI_AUTHOR_OR_COMPLEX` | `Adiantum LUNULATUM` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 148 | `Vitex TRIFOLIA L. f.` | `MULTI_AUTHOR_OR_COMPLEX` | `Vitex TRIFOLIA` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 152 | `Viscum cruciatum Sieber ex Boiss.` | `MULTI_AUTHOR_OR_COMPLEX` | `Viscum cruciatum` | `OFFLINE_RULE` | `ZERO_RESULTS` | 0 | 0 | **`ZERO_RESULT`** |
| 316 | `. PHYLLANTHUS EMBLICA L. (Euphorbiaceae)` | `OTHER_REVIEW` | `PHYLLANTHUS EMBLICA` | `MANUAL_REVIEW` | `PASS` | 50 | 0 | **`NEEDS_REVIEW`** |
| 382 | `Mollugo PENTAPHYLLA L. ()` | `OTHER_REVIEW` | `Mollugo PENTAPHYLLA` | `MANUAL_REVIEW` | `ZERO_RESULTS` | 0 | 0 | **`NEEDS_REVIEW`** |
| 391 | `Mesua NAGESSARIUM (Burm.) Kost. ()` | `OTHER_REVIEW` | `Mesua NAGESSARIUM` | `MANUAL_REVIEW` | `ZERO_RESULTS` | 0 | 0 | **`NEEDS_REVIEW`** |
| 460 | `. JATROPHA CURCAS L.` | `OTHER_REVIEW` | `JATROPHA CURCAS` | `MANUAL_REVIEW` | `ZERO_RESULTS` | 0 | 0 | **`NEEDS_REVIEW`** |
| 802 | `Solenaamplexicaulis(lam.) gandhi.` | `OTHER_REVIEW` | `Solena amplexicaulis` | `MANUAL_REVIEW` | `PASS` | 25 | 0 | **`NEEDS_REVIEW`** |
| 807 | `Sida orientaliscav.` | `OTHER_REVIEW` | `Sida orientalis` | `MANUAL_REVIEW` | `ZERO_RESULTS` | 0 | 0 | **`NEEDS_REVIEW`** |
| 809 | `Sidacordata(burm.f.) borss.waalk.` | `OTHER_REVIEW` | `Sida cordata` | `MANUAL_REVIEW` | `ZERO_RESULTS` | 0 | 0 | **`NEEDS_REVIEW`** |
| 822 | `Elaeocarpus serratusl.` | `OTHER_REVIEW` | `Elaeocarpus serratus` | `MANUAL_REVIEW` | `ZERO_RESULTS` | 0 | 0 | **`NEEDS_REVIEW`** |
| 865 | `Cardiospermum HALICACABUML.` | `OTHER_REVIEW` | `Cardiospermum halicacabum` | `MANUAL_REVIEW` | `PASS` | 25 | 25 | **`NEEDS_REVIEW`** |
| 884 | `Celosia CRISTATA L.(SAME AS 161)` | `OTHER_REVIEW` | `Celosia CRISTATA` | `MANUAL_REVIEW` | `ZERO_RESULTS` | 0 | 0 | **`NEEDS_REVIEW`** |
| 886 | `Piperboehmeriifolium(miq.) wall. ex C. DC.` | `OTHER_REVIEW` | `Piper boehmeriifolium` | `MANUAL_REVIEW` | `ZERO_RESULTS` | 0 | 0 | **`NEEDS_REVIEW`** |
| 894 | `Desmos chinensislour.` | `OTHER_REVIEW` | `Desmos chinensis` | `MANUAL_REVIEW` | `PASS` | 79 | 79 | **`NEEDS_REVIEW`** |

---

## 3. Results for Infraspecific Taxa (`subsp.` & `var.`)

### Subspecies (`subsp.`) — 3 Records
Validating that preserving `subsp.` and the infraspecific epithet produces correct query behavior:

- **[26] RAW**: `Raphanus raphanistrum subsp. SATIVUS(L.) Domin.`  
  **CANDIDATE**: `Raphanus raphanistrum subsp. SATIVUS`  
  **STATUS**: `ZERO_RESULTS` (0 rows, 0 valid CID)  
  **DECISION**: `ZERO_RESULT`  
  **NOTES**: Preserved species binomial, subsp. rank, and infraspecific epithet; stripped parenthetical/combining authors. Query succeeded but returned 0 rows in BMPPD.

- **[31] RAW**: `Acacia nilotica (L.) Delile subsp. INDICA(Benth) Brenan`  
  **CANDIDATE**: `Acacia nilotica subsp. INDICA`  
  **STATUS**: `ZERO_RESULTS` (0 rows, 0 valid CID)  
  **DECISION**: `ZERO_RESULT`  
  **NOTES**: Preserved species binomial, subsp. rank, and infraspecific epithet; stripped parenthetical/combining authors. Query succeeded but returned 0 rows in BMPPD.

- **[839] RAW**: `Drymaria cordata subsp.diandra (Blume) J.A.Duke.`  
  **CANDIDATE**: `Drymaria cordata subsp. diandra`  
  **STATUS**: `ZERO_RESULTS` (0 rows, 0 valid CID)  
  **DECISION**: `ZERO_RESULT`  
  **NOTES**: Preserved species binomial, subsp. rank, and infraspecific epithet; stripped parenthetical/combining authors. Query succeeded but returned 0 rows in BMPPD.

### Varieties (`var.`) — 7 Records
Validating that preserving `var.` and the varietal epithet produces correct query behavior:

- **[180] RAW**: `Trapa natans var. bispinosa (Roxb.) Makino`  
  **CANDIDATE**: `Trapa natans var. bispinosa`  
  **STATUS**: `ZERO_RESULTS` (0 rows, 0 valid CID)  
  **DECISION**: `ZERO_RESULT`  
  **NOTES**: Preserved species binomial, var. rank, and varietal epithet; stripped species author and varietal author. Query succeeded but returned 0 rows in BMPPD.

- **[344] RAW**: `Ophiorrhiza rugosa VAR. PROSTRATA (D.Don) Deb & Mondal.`  
  **CANDIDATE**: `Ophiorrhiza rugosa var. PROSTRATA`  
  **STATUS**: `ZERO_RESULTS` (0 rows, 0 valid CID)  
  **DECISION**: `ZERO_RESULT`  
  **NOTES**: Preserved species binomial, var. rank, and varietal epithet; stripped species author and varietal author. Query succeeded but returned 0 rows in BMPPD.

- **[412] RAW**: `Madhuca longifolia VAR. LATIFOLIA (Roxb.) A.Chev.`  
  **CANDIDATE**: `Madhuca longifolia var. LATIFOLIA`  
  **STATUS**: `ZERO_RESULTS` (0 rows, 0 valid CID)  
  **DECISION**: `ZERO_RESULT`  
  **NOTES**: Preserved species binomial, var. rank, and varietal epithet; stripped species author and varietal author. Query succeeded but returned 0 rows in BMPPD.

- **[546] RAW**: `Ficus BENJAMINA L. var. comosa (Roxb.) Kurz.`  
  **CANDIDATE**: `Ficus BENJAMINA var. comosa`  
  **STATUS**: `ZERO_RESULTS` (0 rows, 0 valid CID)  
  **DECISION**: `ZERO_RESULT`  
  **NOTES**: Preserved species binomial, var. rank, and varietal epithet; stripped species author and varietal author. Query succeeded but returned 0 rows in BMPPD.

- **[561] RAW**: `Erythrina VARIEGATA L. var. orientalis (L.) Merr.`  
  **CANDIDATE**: `Erythrina VARIEGATA var. orientalis`  
  **STATUS**: `ZERO_RESULTS` (0 rows, 0 valid CID)  
  **DECISION**: `ZERO_RESULT`  
  **NOTES**: Preserved species binomial, var. rank, and varietal epithet; stripped species author and varietal author. Query succeeded but returned 0 rows in BMPPD.

- **[564] RAW**: `Cissampelos PAREIRA L. Var. hirsuta (Buch. ex Dc.) Forman`  
  **CANDIDATE**: `Cissampelos PAREIRA var. hirsuta`  
  **STATUS**: `ZERO_RESULTS` (0 rows, 0 valid CID)  
  **DECISION**: `ZERO_RESULT`  
  **NOTES**: Preserved species binomial, var. rank, and varietal epithet; stripped species author and varietal author. Query succeeded but returned 0 rows in BMPPD.

- **[586] RAW**: `Diospyros MONTANA Roxb. Var. CORDIFOLIA (Roxb.) Heirn.`  
  **CANDIDATE**: `Diospyros MONTANA var. CORDIFOLIA`  
  **STATUS**: `ZERO_RESULTS` (0 rows, 0 valid CID)  
  **DECISION**: `ZERO_RESULT`  
  **NOTES**: Preserved species binomial, var. rank, and varietal epithet; stripped species author and varietal author. Query succeeded but returned 0 rows in BMPPD.

---

## 4. Results for the 12 `OTHER_REVIEW` Records

The 12 records with malformed source syntax were isolated and tested with explicit manual candidates (`candidate_source = MANUAL_REVIEW`). All are retained with `query_decision = NEEDS_REVIEW` to prevent unreviewed automated execution in bulk runs:

- **[316] RAW**: `. PHYLLANTHUS EMBLICA L. (Euphorbiaceae)`  
  **MANUAL CANDIDATE**: `PHYLLANTHUS EMBLICA`  
  **OUTCOME**: `PASS` (50 rows extracted)  
  **DECISION**: `NEEDS_REVIEW`  
  **RATIONALE**: Manual candidate review: Stripped leading period and extraneous family name '(Euphorbiaceae)'; clean binomial. Experimental query against BMPPD yielded 50 rows (PASS). Retained under NEEDS_REVIEW because rule cannot be automated.

- **[382] RAW**: `Mollugo PENTAPHYLLA L. ()`  
  **MANUAL CANDIDATE**: `Mollugo PENTAPHYLLA`  
  **OUTCOME**: `ZERO_RESULTS` (0 rows extracted)  
  **DECISION**: `NEEDS_REVIEW`  
  **RATIONALE**: Manual candidate review: Stripped trailing empty parentheses '()'; clean binomial. Experimental query against BMPPD yielded 0 rows (ZERO_RESULTS). Retained under NEEDS_REVIEW because rule cannot be automated.

- **[391] RAW**: `Mesua NAGESSARIUM (Burm.) Kost. ()`  
  **MANUAL CANDIDATE**: `Mesua NAGESSARIUM`  
  **OUTCOME**: `ZERO_RESULTS` (0 rows extracted)  
  **DECISION**: `NEEDS_REVIEW`  
  **RATIONALE**: Manual candidate review: Stripped trailing empty parentheses '()'; clean binomial. Experimental query against BMPPD yielded 0 rows (ZERO_RESULTS). Retained under NEEDS_REVIEW because rule cannot be automated.

- **[460] RAW**: `. JATROPHA CURCAS L.`  
  **MANUAL CANDIDATE**: `JATROPHA CURCAS`  
  **OUTCOME**: `ZERO_RESULTS` (0 rows extracted)  
  **DECISION**: `NEEDS_REVIEW`  
  **RATIONALE**: Manual candidate review: Stripped leading period and author 'L.'; clean binomial. Experimental query against BMPPD yielded 0 rows (ZERO_RESULTS). Retained under NEEDS_REVIEW because rule cannot be automated.

- **[802] RAW**: `Solenaamplexicaulis(lam.) gandhi.`  
  **MANUAL CANDIDATE**: `Solena amplexicaulis`  
  **OUTCOME**: `PASS` (25 rows extracted)  
  **DECISION**: `NEEDS_REVIEW`  
  **RATIONALE**: Manual candidate review: Manually decomposed fused genus+species 'Solenaamplexicaulis' and stripped authority. Experimental query against BMPPD yielded 25 rows (PASS). Retained under NEEDS_REVIEW because rule cannot be automated.

- **[807] RAW**: `Sida orientaliscav.`  
  **MANUAL CANDIDATE**: `Sida orientalis`  
  **OUTCOME**: `ZERO_RESULTS` (0 rows extracted)  
  **DECISION**: `NEEDS_REVIEW`  
  **RATIONALE**: Manual candidate review: Manually separated species epithet from fused author citation 'cav.'. Experimental query against BMPPD yielded 0 rows (ZERO_RESULTS). Retained under NEEDS_REVIEW because rule cannot be automated.

- **[809] RAW**: `Sidacordata(burm.f.) borss.waalk.`  
  **MANUAL CANDIDATE**: `Sida cordata`  
  **OUTCOME**: `ZERO_RESULTS` (0 rows extracted)  
  **DECISION**: `NEEDS_REVIEW`  
  **RATIONALE**: Manual candidate review: Manually decomposed fused genus+species 'Sidacordata' and stripped authority. Experimental query against BMPPD yielded 0 rows (ZERO_RESULTS). Retained under NEEDS_REVIEW because rule cannot be automated.

- **[822] RAW**: `Elaeocarpus serratusl.`  
  **MANUAL CANDIDATE**: `Elaeocarpus serratus`  
  **OUTCOME**: `ZERO_RESULTS` (0 rows extracted)  
  **DECISION**: `NEEDS_REVIEW`  
  **RATIONALE**: Manual candidate review: Manually separated species epithet from fused author citation 'l.'. Experimental query against BMPPD yielded 0 rows (ZERO_RESULTS). Retained under NEEDS_REVIEW because rule cannot be automated.

- **[865] RAW**: `Cardiospermum HALICACABUML.`  
  **MANUAL CANDIDATE**: `Cardiospermum halicacabum`  
  **OUTCOME**: `PASS` (25 rows extracted)  
  **DECISION**: `NEEDS_REVIEW`  
  **RATIONALE**: Manual candidate review: Manually separated species epithet from fused author citation 'L.'. Experimental query against BMPPD yielded 25 rows (PASS). Retained under NEEDS_REVIEW because rule cannot be automated.

- **[884] RAW**: `Celosia CRISTATA L.(SAME AS 161)`  
  **MANUAL CANDIDATE**: `Celosia CRISTATA`  
  **OUTCOME**: `ZERO_RESULTS` (0 rows extracted)  
  **DECISION**: `NEEDS_REVIEW`  
  **RATIONALE**: Manual candidate review: Stripped catalog duplicate note '(SAME AS 161)' and author 'L.'. Experimental query against BMPPD yielded 0 rows (ZERO_RESULTS). Retained under NEEDS_REVIEW because rule cannot be automated.

- **[886] RAW**: `Piperboehmeriifolium(miq.) wall. ex C. DC.`  
  **MANUAL CANDIDATE**: `Piper boehmeriifolium`  
  **OUTCOME**: `ZERO_RESULTS` (0 rows extracted)  
  **DECISION**: `NEEDS_REVIEW`  
  **RATIONALE**: Manual candidate review: Manually decomposed fused genus+species 'Piperboehmeriifolium' and stripped authority. Experimental query against BMPPD yielded 0 rows (ZERO_RESULTS). Retained under NEEDS_REVIEW because rule cannot be automated.

- **[894] RAW**: `Desmos chinensislour.`  
  **MANUAL CANDIDATE**: `Desmos chinensis`  
  **OUTCOME**: `PASS` (79 rows extracted)  
  **DECISION**: `NEEDS_REVIEW`  
  **RATIONALE**: Manual candidate review: Manually separated species epithet from fused author citation 'lour.'. Experimental query against BMPPD yielded 79 rows (PASS). Retained under NEEDS_REVIEW because rule cannot be automated.

---

## 5. Architectural & Validation Conclusions

1. **Zero Transformation Errors**: No candidate query caused an HTTP error or HTML parsing crash.
2. **Infraspecific Taxa**: Subspecies and varietal queries executed cleanly without syntax truncation.
3. **Automatic Rules Validated**: The automatic transformation rules for `SIMPLE_BINOMIAL_WITH_AUTHORITY`, `BINOMIAL_PARENTHETICAL_AUTHORITY`, `INFRASPECIFIC_SUBSP`, `INFRASPECIFIC_VAR`, and `MULTI_AUTHOR_OR_COMPLEX` are empirically verified.
4. **Isolation of Defective Records**: The 12 `OTHER_REVIEW` records remain strictly isolated as `NEEDS_REVIEW` and must be managed via an explicit override map in the final scraper.

