# MPBD Stage 4 — Botanical Reconciliation Report

**Stage**: 4 — Botanical Reconciliation & Normalization  
**Source Dataset**: `data/raw/mpbd/mpbd_plant_index.csv` (`v1.0.0`)  
**Source SHA-256**: `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7`  
**Run Timestamp**: `2026-09-22T16:41:35.921496+00:00`  
**Report Generated**: `2026-09-22T16:41:35.922130+00:00`

---

## Dataset Summary

| Metric | Value |
| :--- | :--- |
| **Raw records (frozen input)** | 916 |
| **Normalized records produced** | 916 |
| **Raw unique scientific names** | 915 |
| **Normalized unique scientific names** | 890 |
| **Potential duplicate groups** | 26 |
| **Records requiring review** | 52 |
| **UNCHANGED** | 0 |
| **NORMALIZED\_ONLY** | 864 |
| **POTENTIAL\_DUPLICATE** | 52 |
| **CANONICAL\_MATCH** | 0 |
| **SYNONYM\_CANDIDATE** | 0 |
| **REVIEW\_REQUIRED** | 0 |

> [!NOTE]
> `CANONICAL_MATCH` and `SYNONYM_CANDIDATE` require external authoritative botanical evidence. None has been assigned automatically. All zero values here are correct — not a pipeline gap.

---

## Scientific-Name Normalization

Layer A normalization applies: Unicode NFC, whitespace collapsing, trimming, and case-folding (lowercase for comparison only).

| Metric | Value |
| :--- | :--- |
| **Raw unique scientific names** | 915 |
| **Normalized unique scientific names** | 890 |
| **Reduction after normalization** | 25 |
| **Potential duplicate groups** | 26 |

### Potential Duplicate Groups (Normalized Name Appears > 1 Time)

| Normalized Name | Count | Raw Variants | Source Pages |
| :--- | :--- | :--- | :--- |
| `ficus racemosa l.` | 2 | Ficus racemosa L. | Ficus RACEMOSA L. | https://mpbd.cu.ac.bd/plants.php | https://mpbd.cu.ac.bd/plants.php?pageno=55 |
| `morus indica l.` | 2 | Morus indica L. | Morus INDICA L. | https://mpbd.cu.ac.bd/plants.php | https://mpbd.cu.ac.bd/plants.php?pageno=38 |
| `mirabilis jalapa l.` | 2 | Mirabilis jalapa L. | Mirabilis JALAPA L. | https://mpbd.cu.ac.bd/plants.php?pageno=39 | https://mpbd.cu.ac.bd/plants.php?pageno=2 |
| `achyranthes aspera l.` | 2 | Achyranthes aspera L. | Achyranthes ASPERA L. | https://mpbd.cu.ac.bd/plants.php?pageno=11 | https://mpbd.cu.ac.bd/plants.php?pageno=2 |
| `plumbago indica l.` | 2 | Plumbago indica L. | Plumbago INDICA L. | https://mpbd.cu.ac.bd/plants.php?pageno=31 | https://mpbd.cu.ac.bd/plants.php?pageno=2 |
| `helicteres isora l.` | 2 | Helicteres isora L. | Helicteres ISORA L. | https://mpbd.cu.ac.bd/plants.php?pageno=51 | https://mpbd.cu.ac.bd/plants.php?pageno=2 |
| `abelmoschus esculentus (l.) moench` | 2 | Abelmoschus esculentus (L.) Moench | Abelmoschus ESCULENTUS (L.) Moench | https://mpbd.cu.ac.bd/plants.php?pageno=10 | https://mpbd.cu.ac.bd/plants.php?pageno=2 |
| `benincasa hispida (thunb.) cogn.` | 2 | Benincasa hispida (Thunb.) Cogn. | Benincasa HISPIDA (Thunb.) Cogn. | https://mpbd.cu.ac.bd/plants.php?pageno=3 | https://mpbd.cu.ac.bd/plants.php?pageno=77 |
| `mimosa pudica l.` | 2 | Mimosa pudica L. | Mimosa PUDICA L. | https://mpbd.cu.ac.bd/plants.php?pageno=4 | https://mpbd.cu.ac.bd/plants.php?pageno=39 |
| `mucuna pruriens (l.) dc.` | 2 | Mucuna pruriens (L.) DC. | Mucuna PRURIENS (L.) DC. | https://mpbd.cu.ac.bd/plants.php?pageno=4 | https://mpbd.cu.ac.bd/plants.php?pageno=38 |
| `sesbania sesban (l.) merr.` | 2 | Sesbania sesban (L.) Merr. | Sesbania SESBAN (L.) Merr. | https://mpbd.cu.ac.bd/plants.php?pageno=25 | https://mpbd.cu.ac.bd/plants.php?pageno=5 |
| `mentha arvensis l.` | 2 | Mentha arvensis L. | Mentha ARVENSIS L. | https://mpbd.cu.ac.bd/plants.php?pageno=40 | https://mpbd.cu.ac.bd/plants.php?pageno=5 |
| `sesamum indicum l.` | 2 | Sesamum indicum L. | Sesamum INDICUM L. | https://mpbd.cu.ac.bd/plants.php?pageno=25 | https://mpbd.cu.ac.bd/plants.php?pageno=5 |
| `saccharum officinarum l.` | 2 | Saccharum officinarum L. | Saccharum OFFICINARUM L. | https://mpbd.cu.ac.bd/plants.php?pageno=27 | https://mpbd.cu.ac.bd/plants.php?pageno=6 |
| `sapindus saponaria l.` | 2 | Sapindus saponaria L. | Sapindus SAPONARIA L. | https://mpbd.cu.ac.bd/plants.php?pageno=7 | https://mpbd.cu.ac.bd/plants.php?pageno=10 |
| `uvaria hamiltonii hook. f. & thom.` | 2 | Uvaria HAMILTONII Hook. f. & Thom. | Uvaria hamiltonii HOOK. F. & THOM. | https://mpbd.cu.ac.bd/plants.php?pageno=17 | https://mpbd.cu.ac.bd/plants.php?pageno=90 |
| `sida cordifolia l.` | 2 | Sida CORDIFOLIA L. | Sida cordifolia L. | https://mpbd.cu.ac.bd/plants.php?pageno=24 | https://mpbd.cu.ac.bd/plants.php?pageno=82 |
| `sida acuta burm. f.` | 2 | Sida ACUTA Burm. f. | Sida acuta Burm. f. | https://mpbd.cu.ac.bd/plants.php?pageno=25 | https://mpbd.cu.ac.bd/plants.php?pageno=82 |
| `shorea robusta gaertn.` | 2 | Shorea ROBUSTA Gaertn. | Shorea robusta Gaertn. | https://mpbd.cu.ac.bd/plants.php?pageno=25 | https://mpbd.cu.ac.bd/plants.php?pageno=84 |
| `ranunculus sceleratus l.` | 2 | Ranunculus SCELERATUS L. | Ranunculus sceleratus L. | https://mpbd.cu.ac.bd/plants.php?pageno=92 | https://mpbd.cu.ac.bd/plants.php?pageno=29 |
| `nymphaea nouchali burm. f.` | 2 | Nymphaea nouchali Burm. f. | Nymphaea NOUCHALI Burm. f. | https://mpbd.cu.ac.bd/plants.php?pageno=36 |
| `melochia corchorifolia l.` | 2 | Melochia CORCHORIFOLIA L. | Melochia corchorifolia L. | https://mpbd.cu.ac.bd/plants.php?pageno=40 | https://mpbd.cu.ac.bd/plants.php?pageno=83 |
| `hypericum japonicum thunb.` | 2 | Hypericum JAPONICUM Thunb. | Hypericum japonicum Thunb. | https://mpbd.cu.ac.bd/plants.php?pageno=49 | https://mpbd.cu.ac.bd/plants.php?pageno=83 |
| `euryale ferox salisb.` | 2 | Euryale FEROX Salisb. | Euryale ferox Salisb. | https://mpbd.cu.ac.bd/plants.php?pageno=92 | https://mpbd.cu.ac.bd/plants.php?pageno=56 |
| `dillenia indica l.` | 2 | Dillenia INDICA L. | Dillenia indica L. | https://mpbd.cu.ac.bd/plants.php?pageno=60 | https://mpbd.cu.ac.bd/plants.php?pageno=84 |
| `cassytha filiformis l.` | 2 | Cassytha FILIFORMIS L. | Cassytha FILIFORMIS L. | https://mpbd.cu.ac.bd/plants.php?pageno=90 | https://mpbd.cu.ac.bd/plants.php?pageno=89 |

---

## Family Normalization

| Metric | Value |
| :--- | :--- |
| **Raw unique family values** | 182 |
| **Normalized unique families** | 175 |
| **Family variant groups reconciled** | 7 |

### Family Variant Groups

| Normalized Family | Raw Variants | Record Count |
| :--- | :--- | :--- |
| `annonaceae` | ANNONACEAE | Annonaceae | 9 |
| `cactaceae` | Cactaceae | Cactaceae. | 2 |
| `cucurbitaceae` | Cucurbitaceae | Cucurbitaceae. | 24 |
| `lauraceae` | LAURACEAE | Lauraceae | 12 |
| `magnoliaceae` | MAGNOLIACEAE | Magnoliaceae | 3 |
| `nyctaginaceae` | Nyctaginaceae | Nyctaginaceae. | 6 |
| `plumbaginaceae` | Plumbaginaceae | Plumbaginaceae. | 3 |

---

## Reconciliation Status Distribution

| Status | Count | Description |
| :--- | :--- | :--- |
| `UNCHANGED` | 0 | Raw fields already match normalized representation. |
| `NORMALIZED_ONLY` | 864 | Only text formatting/case/punctuation changed; no botanical content change. |
| `POTENTIAL_DUPLICATE` | 52 | Normalized scientific name occurs more than once; may be MPBD redundancy. |
| `REVIEW_REQUIRED` | 0 | Unclassified variation; needs human review. |
| `CANONICAL_MATCH` | 0 | Confirmed canonical identity (requires external authoritative evidence). |
| `SYNONYM_CANDIDATE` | 0 | Potential synonym relationship (requires external authoritative evidence). |

---

## Confidence Distribution

| Confidence | Count |
| :--- | :--- |
| `HIGH` | 0 (in review queue) |
| `MEDIUM` | 52 (in review queue) |
| `LOW` | 0 (in review queue) |
| `UNKNOWN` | 0 |

---

## Review Queue

All 52 records flagged for human review are listed below.

| Raw Scientific Name | Normalized | Raw Family | Page | Status | Reason |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Ficus racemosa L.` | `ficus racemosa l.` | `Moraceae` | plants.php | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Morus indica L.` | `morus indica l.` | `Moraceae` | plants.php | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Mirabilis jalapa L.` | `mirabilis jalapa l.` | `Nyctaginaceae` | plants.php?pageno=2 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Achyranthes aspera L.` | `achyranthes aspera l.` | `Amaranthaceae` | plants.php?pageno=2 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Plumbago indica L.` | `plumbago indica l.` | `Plumbaginaceae.` | plants.php?pageno=2 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Helicteres isora L.` | `helicteres isora l.` | `Sterculiaceae` | plants.php?pageno=2 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Abelmoschus esculentus (L.) Moench` | `abelmoschus esculentus (l.) moench` | `Malvaceae` | plants.php?pageno=2 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Benincasa hispida (Thunb.) Cogn.` | `benincasa hispida (thunb.) cogn.` | `Cucurbitaceae` | plants.php?pageno=3 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Mimosa pudica L.` | `mimosa pudica l.` | `Mimosaceae` | plants.php?pageno=4 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Mucuna pruriens (L.) DC.` | `mucuna pruriens (l.) dc.` | `Fabaceae` | plants.php?pageno=4 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Sesbania sesban (L.) Merr.` | `sesbania sesban (l.) merr.` | `Fabaceae` | plants.php?pageno=5 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Mentha arvensis L.` | `mentha arvensis l.` | `Lamiaceae` | plants.php?pageno=5 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Sesamum indicum L.` | `sesamum indicum l.` | `Pedaliaceae` | plants.php?pageno=5 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Saccharum officinarum L.` | `saccharum officinarum l.` | `Poaceae` | plants.php?pageno=6 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Sapindus saponaria L.` | `sapindus saponaria l.` | `Sapindaceae` | plants.php?pageno=7 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Sapindus SAPONARIA L.` | `sapindus saponaria l.` | `Sapindaceae` | plants.php?pageno=10 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Abelmoschus ESCULENTUS (L.) Moench` | `abelmoschus esculentus (l.) moench` | `Malvaceae` | plants.php?pageno=10 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Achyranthes ASPERA L.` | `achyranthes aspera l.` | `Amaranthaceae` | plants.php?pageno=11 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Uvaria HAMILTONII Hook. f. & Thom.` | `uvaria hamiltonii hook. f. & thom.` | `Annonaceae` | plants.php?pageno=17 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Sida CORDIFOLIA L.` | `sida cordifolia l.` | `Malvaceae` | plants.php?pageno=24 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Sida ACUTA Burm. f.` | `sida acuta burm. f.` | `Malvaceae` | plants.php?pageno=25 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Shorea ROBUSTA Gaertn.` | `shorea robusta gaertn.` | `Dipterocarpaceae` | plants.php?pageno=25 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Sesbania SESBAN (L.) Merr.` | `sesbania sesban (l.) merr.` | `Fabaceae` | plants.php?pageno=25 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Sesamum INDICUM L.` | `sesamum indicum l.` | `Pedaliaceae` | plants.php?pageno=25 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Saccharum OFFICINARUM L.` | `saccharum officinarum l.` | `Poaceae` | plants.php?pageno=27 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Ranunculus SCELERATUS L.` | `ranunculus sceleratus l.` | `Ranunculaceae` | plants.php?pageno=29 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Plumbago INDICA L.` | `plumbago indica l.` | `Plumbaginaceae` | plants.php?pageno=31 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Nymphaea nouchali Burm. f.` | `nymphaea nouchali burm. f.` | `Nymphaeaceae` | plants.php?pageno=36 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Nymphaea NOUCHALI Burm. f.` | `nymphaea nouchali burm. f.` | `Nymphaeaceae` | plants.php?pageno=36 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Mucuna PRURIENS (L.) DC.` | `mucuna pruriens (l.) dc.` | `Fabaceae` | plants.php?pageno=38 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Morus INDICA L.` | `morus indica l.` | `Moraceae` | plants.php?pageno=38 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Mirabilis JALAPA L.` | `mirabilis jalapa l.` | `Nyctaginaceae` | plants.php?pageno=39 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Mimosa PUDICA L.` | `mimosa pudica l.` | `Mimosaceae` | plants.php?pageno=39 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Mentha ARVENSIS L.` | `mentha arvensis l.` | `Lamiaceae` | plants.php?pageno=40 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Melochia CORCHORIFOLIA L.` | `melochia corchorifolia l.` | `Sterculiaceae` | plants.php?pageno=40 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Hypericum JAPONICUM Thunb.` | `hypericum japonicum thunb.` | `Hypericaceae` | plants.php?pageno=49 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Helicteres ISORA L.` | `helicteres isora l.` | `Sterculiaceae` | plants.php?pageno=51 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Ficus RACEMOSA L.` | `ficus racemosa l.` | `Moraceae` | plants.php?pageno=55 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Euryale FEROX Salisb.` | `euryale ferox salisb.` | `Nymphaeaceae` | plants.php?pageno=56 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Dillenia INDICA L.` | `dillenia indica l.` | `Dilleniaceae` | plants.php?pageno=60 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Benincasa HISPIDA (Thunb.) Cogn.` | `benincasa hispida (thunb.) cogn.` | `Cucurbitaceae` | plants.php?pageno=77 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Sida cordifolia L.` | `sida cordifolia l.` | `-` | plants.php?pageno=82 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Sida acuta Burm. f.` | `sida acuta burm. f.` | `Malvaceae` | plants.php?pageno=82 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Melochia corchorifolia L.` | `melochia corchorifolia l.` | `Tiliaceae` | plants.php?pageno=83 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Hypericum japonicum Thunb.` | `hypericum japonicum thunb.` | `Clusiaceae` | plants.php?pageno=83 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Shorea robusta Gaertn.` | `shorea robusta gaertn.` | `Dipterocarpaceae` | plants.php?pageno=84 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Dillenia indica L.` | `dillenia indica l.` | `Dilleniaceae` | plants.php?pageno=84 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Cassytha FILIFORMIS L.` | `cassytha filiformis l.` | `Lauraceae` | plants.php?pageno=89 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Cassytha FILIFORMIS L.` | `cassytha filiformis l.` | `LAURACEAE` | plants.php?pageno=90 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Uvaria hamiltonii HOOK. F. & THOM.` | `uvaria hamiltonii hook. f. & thom.` | `ANNONACEAE` | plants.php?pageno=90 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Euryale ferox Salisb.` | `euryale ferox salisb.` | `Nymphaeaceae` | plants.php?pageno=92 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |
| `Ranunculus sceleratus L.` | `ranunculus sceleratus l.` | `Ranunculaceae` | plants.php?pageno=92 | `POTENTIAL_DUPLICATE` | Normalized scientific name appears 2 times. Original change type: CASE_ONLY. |

---

## Raw Dataset Immutability

The frozen source dataset was verified before and after Stage 4 execution:

```text
data/raw/mpbd/mpbd_plant_index.csv
SHA-256: 0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7
Status: UNCHANGED
```

---

## Derived Output SHA-256 (Reproducibility)

| Output File | SHA-256 |
| :--- | :--- |
| `mpbd_plant_index_normalized.csv` | `44ED4560916A5EAB8F309C5CAE9BE448CB46636803539B8B2C743E09EFAD1056` |
| `mpbd_botanical_reconciliation.csv` | `B4DEF98C29B3E30DEE513850382F8C1FAF2A9E56F48CDEB642906FEDD8636188` |
| `mpbd_family_normalization.csv` | `B2D96B00864D697582D2D928533C5658F1210CB104A7C313B0B61EEE947C480C` |

---

## Architecture Notes

### Layer A — Text Normalization (deterministic, no botanical knowledge)
- NFC Unicode normalization
- Non-breaking space → regular space
- Whitespace collapse
- Trim
- Lowercase (comparison key only; raw value is always preserved)
- Safe terminal punctuation removal (family field only)

### Layer B — Botanical Reconciliation (evidence-based only)
- No speculative canonical name assignment
- No automatic synonym invention
- `CANONICAL_MATCH` and `SYNONYM_CANDIDATE` require explicit external evidence
- Every non-trivial reconciliation is traceable via `reconciliation_reason` and `evidence_source`

> [!IMPORTANT]
> A text normalization operation is never treated as equivalent to a taxonomic correction. Both the raw and normalized representations are preserved in every output file.

---

## Stage 4 Status: COMPLETE
