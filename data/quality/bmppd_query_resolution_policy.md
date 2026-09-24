# BMPPD Query-Resolution Policy Report (Stage 6E)

**Stage**: 6E — Deterministic Production Query-Resolution Layer  
**Execution Mode**: COMPLETELY OFFLINE (0 network requests)  
**Source Inventory**: `data/raw/mpbd/mpbd_plant_index.csv` (strictly read-only)  
**Frozen Dataset SHA-256**: `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` (Verified Unchanged)  
**Total Records**: `916`  
**Production READY**: `904` (98.69%)  
**MANUAL_REVIEW**: `12` (1.31%)  

---

## 1. Resolution Metrics & Status Counts

| Metric | Count | Percentage | Operational Role |
| :--- | :---: | :---: | :--- |
| **Total MPBD Plants** | 916 | 100.00% | Complete frozen master inventory |
| **`READY` (Automatic Rule)** | **904** | **98.69%** | Safe to query via deterministic rules |
| **`MANUAL_REVIEW` (Overrides)** | **12** | **1.31%** | Isolated defective names managed by override table |

### Breakdown by Structural Pattern

| Pattern Category | Count | Status | Query Source | Description |
| :--- | :---: | :---: | :---: | :--- |
| **`SIMPLE_BINOMIAL_WITH_AUTHORITY`** | **502** | `READY` | `OFFLINE_RULE` | Removed single author citation suffix; preserved exact binomial casing. |
| **`BINOMIAL_PARENTHETICAL_AUTHORITY`** | **335** | `READY` | `OFFLINE_RULE` | Removed parenthetical basionym & combining authors; preserved clean binomial. |
| **`MULTI_AUTHOR_OR_COMPLEX`** | **57** | `READY` | `OFFLINE_RULE` | Removed compound/multi-word author citations; preserved clean binomial. |
| **`INFRASPECIFIC_VAR`** | **7** | `READY` | `OFFLINE_RULE` | Preserved species binomial, 'var.' rank, and varietal epithet without collapsing. |
| **`INFRASPECIFIC_SUBSP`** | **3** | `READY` | `OFFLINE_RULE` | Preserved species binomial, 'subsp.' rank, and subspecies epithet without collapsing. |
| **`OTHER_REVIEW`** | **12** | `MANUAL_REVIEW` | `MANUAL_OVERRIDE` | Malformed/fused records managed explicitly via bmppd_query_overrides.csv. |

---

## 2. Infraspecific Taxa Preservation (Rules 4 & 5)

### Subspecies (`subsp.`) — 3 Records
All 3 subspecies records are preserved structurally. **Parent-binomial fallback is explicitly NOT enabled**:

- **[26] RAW**: `Raphanus raphanistrum subsp. SATIVUS(L.) Domin.`  
  **QUERY**: `Raphanus raphanistrum subsp. SATIVUS`  
  **STATUS**: `READY` (`OFFLINE_RULE`)  
  **NOTES**: Preserved species binomial and subsp. rank + epithet; stripped author citations.

- **[31] RAW**: `Acacia nilotica (L.) Delile subsp. INDICA(Benth) Brenan`  
  **QUERY**: `Acacia nilotica subsp. INDICA`  
  **STATUS**: `READY` (`OFFLINE_RULE`)  
  **NOTES**: Preserved species binomial and subsp. rank + epithet; stripped author citations.

- **[839] RAW**: `Drymaria cordata subsp.diandra (Blume) J.A.Duke.`  
  **QUERY**: `Drymaria cordata subsp. diandra`  
  **STATUS**: `READY` (`OFFLINE_RULE`)  
  **NOTES**: Preserved species binomial and subsp. rank + epithet; stripped author citations.

### Varieties (`var.`) — 7 Records
All 7 variety records preserve the varietal rank and epithet without collapsing to parent species:

- **[180] RAW**: `Trapa natans var. bispinosa (Roxb.) Makino`  
  **QUERY**: `Trapa natans var. bispinosa`  
  **STATUS**: `READY` (`OFFLINE_RULE`)  
  **NOTES**: Preserved species binomial and var. rank + epithet; stripped species and varietal authors.

- **[344] RAW**: `Ophiorrhiza rugosa VAR. PROSTRATA (D.Don) Deb & Mondal.`  
  **QUERY**: `Ophiorrhiza rugosa var. PROSTRATA`  
  **STATUS**: `READY` (`OFFLINE_RULE`)  
  **NOTES**: Preserved species binomial and var. rank + epithet; stripped species and varietal authors.

- **[412] RAW**: `Madhuca longifolia VAR. LATIFOLIA (Roxb.) A.Chev.`  
  **QUERY**: `Madhuca longifolia var. LATIFOLIA`  
  **STATUS**: `READY` (`OFFLINE_RULE`)  
  **NOTES**: Preserved species binomial and var. rank + epithet; stripped species and varietal authors.

- **[546] RAW**: `Ficus BENJAMINA L. var. comosa (Roxb.) Kurz.`  
  **QUERY**: `Ficus BENJAMINA var. comosa`  
  **STATUS**: `READY` (`OFFLINE_RULE`)  
  **NOTES**: Preserved species binomial and var. rank + epithet; stripped species and varietal authors.

- **[561] RAW**: `Erythrina VARIEGATA L. var. orientalis (L.) Merr.`  
  **QUERY**: `Erythrina VARIEGATA var. orientalis`  
  **STATUS**: `READY` (`OFFLINE_RULE`)  
  **NOTES**: Preserved species binomial and var. rank + epithet; stripped species and varietal authors.

- **[564] RAW**: `Cissampelos PAREIRA L. Var. hirsuta (Buch. ex Dc.) Forman`  
  **QUERY**: `Cissampelos PAREIRA var. hirsuta`  
  **STATUS**: `READY` (`OFFLINE_RULE`)  
  **NOTES**: Preserved species binomial and var. rank + epithet; stripped species and varietal authors.

- **[586] RAW**: `Diospyros MONTANA Roxb. Var. CORDIFOLIA (Roxb.) Heirn.`  
  **QUERY**: `Diospyros MONTANA var. CORDIFOLIA`  
  **STATUS**: `READY` (`OFFLINE_RULE`)  
  **NOTES**: Preserved species binomial and var. rank + epithet; stripped species and varietal authors.

---

## 3. The 12 `OTHER_REVIEW` Records (Rule 6 — Manual Override Table)

Managed via `data/processed/mpbd/bmppd_query_overrides.csv` and classified as `MANUAL_REVIEW`:

- **[316] RAW**: `. PHYLLANTHUS EMBLICA L. (Euphorbiaceae)`  
  **OVERRIDE QUERY**: `PHYLLANTHUS EMBLICA`  
  **STATUS**: `MANUAL_REVIEW` (`MANUAL_OVERRIDE`)  
  **RATIONALE**: Manual override: Stripped leading period and extraneous family annotation in parentheses

- **[382] RAW**: `Mollugo PENTAPHYLLA L. ()`  
  **OVERRIDE QUERY**: `Mollugo PENTAPHYLLA`  
  **STATUS**: `MANUAL_REVIEW` (`MANUAL_OVERRIDE`)  
  **RATIONALE**: Manual override: Stripped trailing empty parentheses and author citation 'L.'

- **[391] RAW**: `Mesua NAGESSARIUM (Burm.) Kost. ()`  
  **OVERRIDE QUERY**: `Mesua NAGESSARIUM`  
  **STATUS**: `MANUAL_REVIEW` (`MANUAL_OVERRIDE`)  
  **RATIONALE**: Manual override: Stripped trailing empty parentheses and parenthetical/combining author citations

- **[460] RAW**: `. JATROPHA CURCAS L.`  
  **OVERRIDE QUERY**: `JATROPHA CURCAS`  
  **STATUS**: `MANUAL_REVIEW` (`MANUAL_OVERRIDE`)  
  **RATIONALE**: Manual override: Stripped leading period and author citation 'L.'

- **[802] RAW**: `Solenaamplexicaulis(lam.) gandhi.`  
  **OVERRIDE QUERY**: `Solena amplexicaulis`  
  **STATUS**: `MANUAL_REVIEW` (`MANUAL_OVERRIDE`)  
  **RATIONALE**: Manual override: Decomposed fused genus+species 'Solenaamplexicaulis' and stripped parenthetical/combining authors

- **[807] RAW**: `Sida orientaliscav.`  
  **OVERRIDE QUERY**: `Sida orientalis`  
  **STATUS**: `MANUAL_REVIEW` (`MANUAL_OVERRIDE`)  
  **RATIONALE**: Manual override: Separated species epithet from fused Cavanilles author abbreviation 'cav.'

- **[809] RAW**: `Sidacordata(burm.f.) borss.waalk.`  
  **OVERRIDE QUERY**: `Sida cordata`  
  **STATUS**: `MANUAL_REVIEW` (`MANUAL_OVERRIDE`)  
  **RATIONALE**: Manual override: Decomposed fused genus+species 'Sidacordata' and stripped author citation '(burm.f.) borss.waalk.'

- **[822] RAW**: `Elaeocarpus serratusl.`  
  **OVERRIDE QUERY**: `Elaeocarpus serratus`  
  **STATUS**: `MANUAL_REVIEW` (`MANUAL_OVERRIDE`)  
  **RATIONALE**: Manual override: Separated species epithet from fused Linnaean author abbreviation 'l.'

- **[865] RAW**: `Cardiospermum HALICACABUML.`  
  **OVERRIDE QUERY**: `Cardiospermum HALICACABUM`  
  **STATUS**: `MANUAL_REVIEW` (`MANUAL_OVERRIDE`)  
  **RATIONALE**: Manual override: Separated uppercase species epithet from fused author citation 'L.'

- **[884] RAW**: `Celosia CRISTATA L.(SAME AS 161)`  
  **OVERRIDE QUERY**: `Celosia CRISTATA`  
  **STATUS**: `MANUAL_REVIEW` (`MANUAL_OVERRIDE`)  
  **RATIONALE**: Manual override: Stripped administrative duplicate catalog annotation '(SAME AS 161)' and author 'L.'

- **[886] RAW**: `Piperboehmeriifolium(miq.) wall. ex C. DC.`  
  **OVERRIDE QUERY**: `Piper boehmeriifolium`  
  **STATUS**: `MANUAL_REVIEW` (`MANUAL_OVERRIDE`)  
  **RATIONALE**: Manual override: Decomposed fused genus+species 'Piperboehmeriifolium' and stripped complex author citation

- **[894] RAW**: `Desmos chinensislour.`  
  **OVERRIDE QUERY**: `Desmos chinensis`  
  **STATUS**: `MANUAL_REVIEW` (`MANUAL_OVERRIDE`)  
  **RATIONALE**: Manual override: Separated species epithet from fused Loureiro author citation 'lour.'

---

## 4. Examples from Automatic Transformation Rules

### Rule 1 — `SIMPLE_BINOMIAL_WITH_AUTHORITY` (502 records)
- `[1]` RAW: `Piper betle L.` $\rightarrow$ QUERY: `Piper betle`
- `[2]` RAW: `Piper cubeba Vahl` $\rightarrow$ QUERY: `Piper cubeba`
- `[3]` RAW: `Berberis aristata DC.` $\rightarrow$ QUERY: `Berberis aristata`
- `[4]` RAW: `Papaver somniferum L.` $\rightarrow$ QUERY: `Papaver somniferum`
- `[5]` RAW: `Artocarpus heterophyllus Lam.` $\rightarrow$ QUERY: `Artocarpus heterophyllus`

### Rule 2 — `BINOMIAL_PARENTHETICAL_AUTHORITY` (335 records)
- `[12]` RAW: `Opuntia dellenii (Ker Gawl.) Haw.` $\rightarrow$ QUERY: `Opuntia dellenii`
- `[18]` RAW: `Abelmoschus esculentus (L.) Moench` $\rightarrow$ QUERY: `Abelmoschus esculentus`
- `[21]` RAW: `Benincasa hispida (Thunb.) Cogn.` $\rightarrow$ QUERY: `Benincasa hispida`
- `[22]` RAW: `Citrullus colocynthis (L.) Schard.` $\rightarrow$ QUERY: `Citrullus colocynthis`
- `[28]` RAW: `Diospyros malabarica(desr.) Kostel.` $\rightarrow$ QUERY: `Diospyros malabarica`

### Rule 3 — `MULTI_AUTHOR_OR_COMPLEX` (57 records)
- `[23]` RAW: `Momordica dioica Roxb. ex Willd.` $\rightarrow$ QUERY: `Momordica dioica`
- `[38]` RAW: `Pterocarpus SANTALINUS L. f.` $\rightarrow$ QUERY: `Pterocarpus SANTALINUS`
- `[67]` RAW: `Semecarpus anacardium L. F.` $\rightarrow$ QUERY: `Semecarpus anacardium`
- `[73]` RAW: `Anethum sowa Roxb.ex Fleming` $\rightarrow$ QUERY: `Anethum sowa`
- `[78]` RAW: `Holarrhena pubescens Wall.ex G.Don` $\rightarrow$ QUERY: `Holarrhena pubescens`

---

## 5. Offline Validation Checklist (--validate)

| # | Validation Requirement | Result | Status |
| :-: | :--- | :--- | :---: |
| 1 | Exactly 916 records generated | 916 rows | **PASS** |
| 2 | Raw MPBD name matches frozen source exactly | 916/916 exact match | **PASS** |
| 3 | No blank plant_index values (1-916 sequential) | Clean sequential index | **PASS** |
| 4 | Exactly one valid query_status (READY / MANUAL_REVIEW) | 904 READY / 12 MANUAL_REVIEW | **PASS** |
| 5 | All 12 OTHER_REVIEW records isolated | Exactly 12 records mapped | **PASS** |
| 6 | All 3 subsp. records preserve rank + epithet | All 3 preserve 'subsp.' | **PASS** |
| 7 | All 7 var. records preserve rank + epithet | All 7 preserve 'var.' | **PASS** |
| 8 | Candidate queries stripped of author suffixes in auto rules | All 894 binomials clean | **PASS** |
| 9 | Infraspecific taxa not truncated to first two tokens | 10/10 retain >2 tokens | **PASS** |
| 10 | Parent-binomial fallback NOT enabled | Infraspecific rank preserved | **PASS** |
| 11 | Frozen dataset SHA-256 matches manifest | `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` | **PASS** |
| 12 | Zero network requests made (offline pure transformation) | 0 sockets / 0 requests | **PASS** |
| 13 | Byte-identical deterministic output between runs | Identical SHA-256 across runs | **PASS** |

