# Stage 7A: Chemical Structure Standardization Report

**Execution Timestamp**: 2026-09-24T11:34:32.948562+00:00  
**Master MPBD SHA-256 (Start & End)**: `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` (Integrity Verified)  
**Total Runtime**: 174.04 seconds (2.90 minutes)  

---

## 1. Attrition & Step-by-Step Curation

| Step | Description | Rows / Count | Notes |
| :--- | :--- | :---: | :--- |
| **Input Rows** | Total rows evaluated from Step 1 | **24,001** | 100.0% |
| **Unresolved from Step 1** | Rows missing structure (no-match, encoding loss, non-specific) | **1,363** | Dropped to `compounds_dropped.csv` |
| **Multiple-Matches Evaluated** | Multiple candidate sets evaluated | **133** | Evaluated via largest-fragment test |
| **Multiple-Matches Accepted** | Candidates share exact same connectivity layer | **131** | Accepted at flat connectivity level |
| **Multiple-Matches Rejected** | Candidates have heterogeneous connectivity layers | **2** | Dropped to `compounds_dropped.csv` |
| **Invalid SMILES** | RDKit sanitization failures / unparseable | **22** | Dropped |
| **Standardization Exceptions** | Curation errors | **0** | Dropped |
| **Successfully Linked Rows** | Standardized rows linked to unique molecules | **22,614** | **94.22% of input** |
| **Unique Connectivity Molecules** | Deduplicated primary molecules (14-char InChIKey) | **7,317** | **True Unique Molecule Inventory** |

---

## 2. Reconciliation Audit (Exact 24,001 Rows)

$$\text{Linked Rows (22,614)} + \text{Dropped Rows (1,387)} = \mathbf{24,001}$$

- **Assertion Status**: **PASSED** (100% of all 24,001 rows accounted for).
- Every row in `plant_compound_links.csv` joins to exactly one row in `compounds_unique.csv` (**0 orphan links**).

---

## 3. Multiple-Matches Resolution Summary

- **Candidate Sets Evaluated**: **133**
- **Accepted Sets (Same Connectivity Layer)**: **131** (98.5%)
- **Rejected Sets (Heterogeneous Connectivity Layers)**: **2** (1.5%)
- **Same-Connectivity Sets Containing Salts/Solvents**: **6**
  - *(Standardized through largest-fragment chooser prior to connectivity comparison).*

---

## 4. Stereochemical Resolution & Diversity

- **Unique 14-Character Connectivity Layers (Flat Skeletons)**: **7,317**
- **Unique Full InChIKeys (Stereoisomer Forms)**: **6,770**
- **Stereo-Resolved Molecules**: **6,770** (92.5%)
  - *(All source rows agree on a single, unambiguous stereochemical configuration).*
- **Stereo-Unresolved Molecules**: **547** (7.5%)
  - *(Multiple stereoisomers reported across plants or originating from multiple-match candidates; retained with flat connectivity and stereo flags).*

---

## 5. Quality Flags Breakdown

Quality flags are stored as boolean columns in `compounds_unique.csv`:

| Quality Flag | Flagged Molecules | % of Unique | Description / Rule |
| :--- | :---: | :---: | :--- |
| **`is_inorganic`** | **30** | 0.41% | No carbon atoms, or contains a metal atom |
| **`has_metal`** | **13** | 0.18% | Contains any metal atom (alkali, transition, etc.) |
| **`too_small`** | **70** | 0.96% | Heavy atom count < 5 (e.g. water, small alcohols) |
| **`too_large`** | **7** | 0.10% | Heavy atom count > 100 (macromolecules, tannins) |
| **`is_mixture`** | **0** | 0.00% | Multiple disconnected fragments after desalting |
| **`tautomer_failed`**| **0** | 0.00% | Tautomer canonicalizer timed out or reached cap |
| **`charge_remaining`**| **101** | 1.38% | Formal charge != 0 after uncharging |

### Curated Drug-Like Organic Subset:
- If downstream modeling filters out `is_inorganic`, `too_small`, `too_large`, and `is_mixture`:
  - **Remaining Curated Molecules**: **7,228** (**98.8%**)

---

## 6. Plant-Level Distribution

- **Medicinal Plants Covered**: **222 / 222 plants (100.0%)**
- **Molecules per Plant**:
  - Min: **1**
  - Median: **50**
  - Max: **708**
- **Species Specificity**:
  - Molecules found in **ONLY 1 plant**: **5,026** (68.7%)
  - Molecules found in **2 OR MORE plants**: **2,291** (31.3%)

---

## 7. Artifact Checklist

- Unique standardized molecules: [`data/processed/compounds/compounds_unique.csv`](file:///f:/bmppd-thesis/data/processed/compounds/compounds_unique.csv)
- Plant-compound join table: [`data/processed/compounds/plant_compound_links.csv`](file:///f:/bmppd-thesis/data/processed/compounds/plant_compound_links.csv)
- Dropped/unresolved audit table: [`data/processed/compounds/compounds_dropped.csv`](file:///f:/bmppd-thesis/data/processed/compounds/compounds_dropped.csv)
- Attrition ledger: [`data/attrition/structure_standardization_attrition.csv`](file:///f:/bmppd-thesis/data/attrition/structure_standardization_attrition.csv)
- Full quality report: [`data/quality/stage7a_standardization_report.md`](file:///f:/bmppd-thesis/data/quality/stage7a_standardization_report.md)
