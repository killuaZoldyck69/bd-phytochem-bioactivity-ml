# Design Note: Recovering Traditional Anti-Inflammatory Uses of Bangladeshi Medicinal Plants with Bioactivity Models

**Author:** Nahid | **Supervisor:** [name] | **Date:** 25 September 2026
**Status:** Written before any model is trained. Later changes go in the amendment log (Section 11), never as silent edits.

---

## 1. Purpose

This note fixes the study design before any model exists. The targets, thresholds, splits and controls below were chosen without seeing model output, so that results cannot steer the method. If a choice has to change, I record when and why in Section 11.

## 2. Research question and hypothesis

**Question.** Can machine-learning models trained on public bioactivity data recover the traditional anti-inflammatory and analgesic uses of Bangladeshi medicinal plants?

**Hypothesis.** Plants traditionally used for pain or inflammation contain a larger share of compounds predicted active against COX-1 or COX-2 than plants without those uses.

**Null.** No difference remains once compound count and widely shared compounds are controlled for. Because two targets are tested, p-values are Holm-corrected. A null result is an acceptable outcome if the method is sound.

## 3. Data foundation (already built and verified)

| Item                                                                | Value                                     |
| :------------------------------------------------------------------ | :---------------------------------------- |
| Plants (MPBD, frozen, SHA-256 verified)                             | 916                                       |
| Plant-compound rows (BMPPD)                                         | 24,001, covering 222 plants               |
| Unique molecules after PubChem resolution and RDKit standardization | 7,317 (identity at 2D-connectivity level) |
| Matched to ChEMBL 37                                                | 3,263 (44.6%)                             |
| With usable / strict single-protein activity                        | 1,581 / 1,083                             |
| Flora molecules tested on COX-1 / COX-2 (strict assays)             | 32 / 25                                   |

Traditional-use text comes from the MPBD detail pages. The Disease field is non-placeholder for 218 of the 222 compound plants and is cut at the site's 255-character limit in 15 of them (6.8%). The Uses field is cut in 117 (52.7%), so **Disease is the primary source and Uses is supporting only.**

## 4. Targets

| Role        | Target                       | Traditional-use link           | Basis                                                                                                          |
| :---------- | :--------------------------- | :----------------------------- | :------------------------------------------------------------------------------------------------------------- |
| Primary     | COX-1 (PTGS1), COX-2 (PTGS2) | Pain, inflammation, rheumatism | About 86 and 80 of 222 plants match pain and inflammation keywords (exploratory substring counts, overlapping) |
| Exploratory | Xanthine oxidase             | Gout                           | About 8 plants; descriptive only                                                                               |
| Exploratory | MAO-A                        | Nervous disorders              | About 33 plants; descriptive only                                                                              |

Not pursued: acetylcholinesterase (almost no memory or cognition terms in the use text), PTP1B (1 active among 63 tested), carbonic anhydrases (no traditional-use link), and diabetes and cancer targets (few plants, noisy terms). Exploratory targets get no significance claims.

## 5. Labels

- **Source:** ChEMBL 37, human targets only.
- **Records kept:** relation "=", nM units, IC50/Ki/Kd/EC50, no duplicate or validity flags, from binding or functional assays with confidence score 8 or 9 on a single protein.
- **Active:** median pChEMBL of at least 6 per molecule-target pair. A threshold of 5 is run as a sensitivity analysis.
- **Inactive:** measured and below the threshold. A molecule that was never measured is **not** inactive and is never used as a negative.
- **Conflicts:** pairs whose records fall on both sides of the threshold by more than one log unit are excluded and counted in the report.

## 6. Leakage control

Every one of the 7,317 flora connectivity layers is removed from the ChEMBL training data for the target being modelled. Flora molecules are therefore unseen at test time. Any flora molecule found in a training set voids that experiment.

## 7. Models and evaluation

- **Baseline:** ECFP4 fingerprints with random forest or XGBoost. One additional model (a graph network or a second fingerprint family) only if time allows.
- **Internal validation:** scaffold split within ChEMBL, reporting AUROC, AUPRC and calibration. The cut-off for "predicted active" is set on internal validation data only.
- **External test:** the labeled flora molecules. With 32 and 25 tested molecules, and fewer actives, this set is small. I report bootstrap confidence intervals and treat it as supporting evidence, not proof.
- **Applicability domain:** each flora molecule's similarity to its nearest training neighbours is reported, and low-similarity predictions are flagged rather than trusted.

## 8. Plant-level test

1. **Use categories.** Six to ten categories are defined in writing first. The most frequent ~300 Disease terms are mapped by hand, pure action terms (tonic, diuretic, astringent and similar) are excluded, and the long tail stays unmapped. A second reviewer checks at least 50 terms and I report agreement. Keyword matching is exploratory only and is not the mapping.
2. **Plant score.** Primary: the fraction of a plant's compounds predicted active. Secondary: mean predicted probability. Fractions prevent very rich plants (such as _Citrus reticulata_, 708 compounds) from dominating.
3. **Test.** Permutation test with at least 10,000 shuffles of use labels across plants.
4. **Controls.** Comparison against plants matched on compound count, and a repeat with the 20 and 50 most widespread compounds removed (quercetin, beta-sitosterol and palmitic acid would otherwise inflate every category).

## 9. Go/no-go check

Before any training, I count human COX-1 and COX-2 labeled compounds in ChEMBL 37 after removing flora molecules. If either target has fewer than roughly 1,000, I return to my supervisor before continuing.

## 10. Scope exclusions and known limitations

**Excluded:** BindingDB, SwissTargetPrediction, network pharmacology, taxonomic harmonization (unless a specific plant-matching failure requires it), a second-pass repair of unresolved compound names, and any new scraping.

**Limitations to state in the thesis:** truncated and partly lost text in MPBD (255-character limit, upstream encoding loss); BMPPD covers only 222 of 916 plants (24%); 55% of molecules have no ChEMBL match; ChEMBL is biased toward well-studied compounds; identity is at connectivity level, not stereo level; and the flora test set is small.

## 11. Amendment log

| Date | Change | Reason |
| :--- | :----- | :----- |
|      |        |        |
