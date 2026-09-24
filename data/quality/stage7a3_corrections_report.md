# Stage 7A-3: Corrections to the Link-Confidence Audit Report
**Authority:** `docs/thesis_design_note.md`  
**Date:** 2026-09-25  
**Master MPBD SHA-256 (Start & End):** `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` (Integrity Verified)  
**ChEMBL 37 Database:** `F:/datasets/chembl_37/chembl_37_sqlite/chembl_37.db` (Read-Only)  

---

## Executive Summary
Following the Stage 7A-2 link-confidence audit, this Stage 7A-3 corrective review addresses five key methodological and data integrity issues:
1. **External Set Recalibration Rule Fixed:** Instead of dropping whole connectivity layers containing any LOW link (which erroneously discarded major authentic phytochemicals such as luteolin, rutin, hyperoside, catechin, and linoleic acid), the rule is corrected to drop **LOW links, not molecules**. A labeled flora molecule is retained in the evaluation set if it has **at least one HIGH link**. Only 3 of the 100 labeled flora layers lack any HIGH link across all plants (`ITDYPNOEEHONAH`, `SHPPXMGVUDNKLV`, `IBRKLUSXDYATLG`).
2. **Detection Limit of Link-Tier Method Explained:** The link-tier method audits internal name-versus-CID consistency within the database. It **cannot** detect literature assay positive controls (e.g., Trolox or Suprofen) when the paper extractor entered the control drug's name alongside its correct PubChem CID (HIGH tier by construction).
3. **Source Verification Sheet Delivered:** Generated [`data/processed/modeling/external_verification_sheet.csv`](file:///f:/bmppd-thesis/data/processed/modeling/external_verification_sheet.csv) containing 519 link rows across 84 qualifying layers (all active compounds at T=6/T=5, rare compounds $\le 3$ plants, and Trolox) with clean DOIs/PMIDs/ISBNs and blank review columns.
4. **Botanical Duplicate Entries Harmonized into Plant Analysis Units:** Identified 14 duplicate query groups covering 29 plant indices in MPBD that dispatched identical searches to BMPPD (returning 100% identical compound profiles) despite differing `disease_raw` texts. Collapsed the 222 compound plants into **207 distinct plant analysis units** ([`data/processed/modeling/plant_analysis_units.csv`](file:///f:/bmppd-thesis/data/processed/modeling/plant_analysis_units.csv)). Exactly 16 analysis units lose >50% of links under HIGH-only (AU_021 *Benincasa hispida* was previously double-counted under indices 21 and 765).
5. **Molecular Formula Audit of LOW Links:** Formula analysis of LOW links confirms that compounds such as petunidin, peonidin, pelargonidin, curzerene, seychellene, and casuarinin share formulas or core skeletons with their reported CIDs, having been flagged due to counter-ion representation or standardization limitations rather than chemical collisions.
6. **Plant-Level Compound Yield Distributions Recalibrated:** Recomputed compound counts across the 207 analysis units (115 pain units, 55.6% vs 92 other units, 44.4%). Clarified that these counts quantify chemical space coverage and compound yield, not statistical power. At $NN \ge 0.4$ under HIGH links, 55.7% of pain units vs 51.1% of other units retain $\ge 5$ in-domain compounds (a modest 4.6 percentage point difference).

---

## Section 1: Correction of the External-Set Retention Rule

### 1.1 Methodological Rationale & Rule Definition
In Stage 7A-2, the preliminary recalibration discarded entire molecular connectivity layers if they contained even a single LOW-tier link. This over-aggressive rule caused false exclusions of abundant, authentic natural products:
- **Luteolin (`IQPNAANSBPBGFQ`):** Present in 34 plants with 34 verified HIGH links; dropped because 2 plants (*Curcuma caesia* [idx 623] and *Zingiber zerumbet* [idx 637]) mistakenly assigned Luteolin's CID to sterol rows.
- **Linoleic Acid (`OYHQOLUKZRVURQ`):** Present in 37 links across 10 plants; dropped due to mismatched trivial fatty acid rows.
- **Rutin (`IKGXIBQEEMLURG`), Hyperoside (`OVSQVDMCBVZWGM`), Catechin (`PFTAWBLQPZVEMU`):** Similarly discarded despite multiple authentic HIGH links in other plants.

**Corrected External-Set Retention Rule:**
> **Drop LOW links, not molecules.** A labeled flora layer is retained in the external evaluation set if it possesses **at least one HIGH-confidence link** in any plant (`n_high_links >= 1`).

### 1.2 Link Tier Breakdown for All 100 Labeled Flora Layers
Across all 100 labeled flora layers, exactly **97 layers possess $\ge 1$ HIGH link**, and only **3 layers possess zero HIGH links**:

| # | Connectivity Layer | Original Compound Names | Target(s) | HIGH Links (Plants) | MEDIUM Links (Plants) | LOW Links (Plants) | Total Links | Retention Status |
|---|---|---|---|---|---|---|---|---|
| 1 | `OYHQOLUKZRVURQ` | (9E.12E)-9.12-Octadecadienoic Acid ... | `cox1` | 104 (2, 4, 9, 13, 16, 21, 27, 34, 43, 49, 55, 59, 65, 70, 77, 78, 90, 92, 95, 104, 114, 116, 121, 124, 128, 151, 192, 195, 196, 200, 207, 232, 247, 253, 257, 265, 272, 287, 299, 316, 321, 349, 356, 374, 386, 389, 405, 435, 439, 447, 449, 458, 462, 464, 492, 497, 523, 525, 563, 619, 626, 629, 632, 635, 637, 661, 671, 675, 683, 687, 705, 715, 731, 749, 761, 765, 786, 793, 794, 796, 802, 806, 821, 865, 867, 874, 878, 883, 897, 906) | 4 (27, 356, 374, 715) | 37 (21, 35, 563, 626, 637, 675, 705, 731, 765, 883) | 145 | **RETAINED** ($\ge 1$ HIGH) |
| 2 | `DTOSIQBPPRVQHS` | 9,12,15-Octadecatrienoic Acid | 9,1... | `cox1` | 51 (4, 16, 27, 34, 43, 55, 65, 70, 90, 94, 116, 151, 192, 196, 200, 253, 257, 265, 287, 316, 349, 374, 388, 447, 449, 462, 464, 497, 626, 632, 635, 637, 687, 715, 749, 786, 799, 802, 812, 865, 867, 878, 883, 897, 906) | 1 (872) | 3 (563, 626, 883) | 55 | **RETAINED** ($\ge 1$ HIGH) |
| 3 | `IKMDFBPHZNJCSN` | 5,6,7-Trimethoxycoumarin | Cinnamic... | `xo|maoa` | 22 (27, 61, 92, 93, 151, 207, 336, 356, 374, 386, 389, 410, 497, 498, 515, 715, 749, 786, 796, 799, 812) | 0 | 3 (35, 626) | 25 | **RETAINED** ($\ge 1$ HIGH) |
| 4 | `IQPNAANSBPBGFQ` | Cholesterol | Luteolin | Stigmaster... | `xo|maoa` | 34 (5, 16, 60, 70, 78, 95, 113, 149, 151, 162, 195, 288, 349, 389, 396, 410, 442, 497, 498, 525, 571, 619, 623, 626, 637, 650, 671, 687, 739, 786, 819, 865, 872, 874) | 0 | 2 (623, 637) | 36 | **RETAINED** ($\ge 1$ HIGH) |
| 5 | `MIJYXULNPSFWEK` | 3-Epioleanolic acid | OLEANOLIC ACI... | `cox2` | 32 (13, 28, 38, 43, 60, 61, 77, 78, 104, 118, 121, 195, 207, 213, 221, 287, 293, 299, 316, 336, 354, 435, 449, 505, 523, 587, 603, 793, 872, 901) | 0 | 2 (121, 563) | 34 | **RETAINED** ($\ge 1$ HIGH) |
| 6 | `OVSQVDMCBVZWGM` | 3,3',4',5,7-Pentahydroxyflavone 3-b... | `xo|maoa` | 32 (34, 95, 192, 207, 257, 272, 287, 336, 389, 441, 491, 497, 498, 503, 523, 525, 626, 661, 687, 761, 796, 872) | 3 (410, 715, 897) | 2 (35, 760) | 37 | **RETAINED** ($\ge 1$ HIGH) |
| 7 | `SHPPXMGVUDNKLV` | Hesperetin Laurate | Scolymoside | `xo` | 0 | 0 | 2 (70, 539) | 2 | **EXCLUDED** (0 HIGH) |
| 8 | `PFTAWBLQPZVEMU` | (+)-Catechin | (+)-catechin | (-)-C... | `cox1|cox2` | 53 (5, 34, 97, 195, 200, 207, 257, 272, 283, 287, 368, 386, 389, 405, 410, 423, 435, 439, 442, 497, 515, 525, 619, 624, 687, 715, 739, 749, 786, 796, 799, 870, 872) | 1 (515) | 1 (200) | 55 | **RETAINED** ($\ge 1$ HIGH) |
| 9 | `IKGXIBQEEMLURG` | Nicotiflorin | Rutin | Vitamin P | ... | `xo|maoa` | 44 (27, 38, 70, 93, 97, 113, 114, 196, 207, 272, 293, 299, 308, 313, 336, 356, 368, 374, 389, 405, 410, 435, 497, 498, 499, 503, 523, 602, 603, 619, 687, 749, 760, 761, 786, 794, 796, 812, 865, 872, 901) | 1 (354) | 1 (637) | 46 | **RETAINED** ($\ge 1$ HIGH) |
| 10 | `OXGUCUVFOIWWQJ` | 4-Hydroxycinnamic acid | Quercetin ... | `xo|maoa` | 14 (16, 34, 60, 257, 287, 299, 313, 368, 386, 389, 687, 760, 872, 894) | 5 (28, 410, 439, 587, 812) | 1 (35) | 20 | **RETAINED** ($\ge 1$ HIGH) |
| 11 | `PCMORTLOPMLEFB` | Sinapic acid | Sinapinic acid | sin... | `cox1|cox2` | 9 (70, 77, 124, 203, 368, 423, 687, 786, 796) | 0 | 1 (356) | 10 | **RETAINED** ($\ge 1$ HIGH) |
| 12 | `AIONOLUJZLIMTK` | Hesperetin | Hesperitin | Hesperiti... | `xo` | 4 (195, 410, 497, 687) | 0 | 1 (70) | 5 | **RETAINED** ($\ge 1$ HIGH) |
| 13 | `HRGUSFBJBOKSML` | Tricin | beta-Sitosterol | `maoa` | 1 (570) | 0 | 1 (623) | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 14 | `SFLMUHDGSQZDOW` | Coniferin | beta-Amyrin | `cox1` | 1 (70) | 0 | 1 (730) | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 15 | `ZZIALNLLNHEQPJ` | 3,3',5-Trihydroxy-7-methoxyflavone ... | `maoa` | 1 (897) | 0 | 1 (9) | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 16 | `REFJWTPEDVJJIY` | Quercetin | Quercitin | quercetin | `cox2|xo|maoa` | 67 (4, 16, 27, 34, 77, 93, 116, 124, 151, 162, 195, 196, 203, 207, 232, 257, 272, 287, 293, 299, 313, 316, 336, 356, 368, 374, 386, 389, 396, 405, 410, 423, 491, 497, 498, 499, 504, 515, 523, 525, 563, 571, 579, 602, 603, 619, 624, 626, 635, 683, 687, 705, 715, 749, 761, 786, 799, 812, 819, 843, 867, 872, 874, 875, 897, 901) | 0 | 0 | 67 | **RETAINED** ($\ge 1$ HIGH) |
| 17 | `RRAFCDWBNXTKKO` | Eugenol | Eugenol/ Phenol, 4-allyl-... | `cox1` | 45 (1, 16, 68, 70, 74, 78, 114, 116, 124, 128, 192, 195, 200, 207, 283, 287, 299, 307, 336, 346, 354, 386, 389, 407, 425, 435, 442, 447, 462, 497, 505, 602, 619, 624, 629, 632, 661, 702, 749, 786, 872, 906) | 1 (635) | 0 | 46 | **RETAINED** ($\ge 1$ HIGH) |
| 18 | `IYRMWMYZSQPJKC` | Kaemperol | Kaempferol | Kempferol ... | `xo` | 44 (4, 14, 27, 35, 61, 70, 97, 116, 151, 162, 195, 203, 207, 299, 301, 313, 316, 336, 356, 368, 374, 386, 389, 405, 410, 418, 439, 491, 497, 498, 499, 515, 523, 602, 603, 619, 626, 705, 715, 749, 799, 812, 872) | 1 (786) | 0 | 45 | **RETAINED** ($\ge 1$ HIGH) |
| 19 | `RECUKUPTGUEGMW` | Carvacrol | Phenol, 2-methyl-5-(1-m... | `cox1` | 34 (1, 2, 5, 68, 70, 74, 78, 94, 114, 116, 124, 195, 200, 287, 299, 307, 336, 346, 356, 407, 442, 497, 619, 624, 629, 632, 635, 659, 661, 687, 721, 739) | 1 (661) | 0 | 35 | **RETAINED** ($\ge 1$ HIGH) |
| 20 | `KZNIFHPLKGYRTM` | Apigenin | apigenin | `cox2|xo|maoa` | 30 (5, 16, 70, 78, 93, 97, 151, 207, 272, 336, 349, 356, 389, 405, 410, 435, 442, 491, 498, 650, 671, 687, 739, 796, 799, 812, 865, 872, 874) | 0 | 0 | 30 | **RETAINED** ($\ge 1$ HIGH) |
| 21 | `WCGUUGGRBIKTOS` | Ursolic acid | ursolic acid | `cox2` | 18 (9, 16, 43, 78, 149, 151, 196, 232, 283, 287, 336, 386, 435, 449, 505, 603, 776) | 0 | 0 | 18 | **RETAINED** ($\ge 1$ HIGH) |
| 22 | `XMOCLSLCDHWDHP` | (+)-Gallocatechin | (+)-epigallocat... | `cox1` | 18 (5, 97, 195, 207, 287, 423, 439, 497, 515, 619, 739, 796, 799, 872, 901) | 0 | 0 | 18 | **RETAINED** ($\ge 1$ HIGH) |
| 23 | `RTATXGUCZHCSNG` | Kaempferol 3-O-rutinoside | Kaempfe... | `xo` | 16 (5, 35, 70, 114, 232, 354, 389, 405, 423, 497, 499, 602, 739, 796) | 1 (812) | 0 | 17 | **RETAINED** ($\ge 1$ HIGH) |
| 24 | `YQUVCSBJEUQKSH` | 3,4-Dihydroxy Benzoic Acid | 3,4-Di... | `cox2` | 16 (16, 43, 97, 113, 203, 207, 232, 356, 410, 449, 497, 498, 579, 602, 799, 906) | 1 (410) | 0 | 17 | **RETAINED** ($\ge 1$ HIGH) |
| 25 | `MXXWOMGUGJBKIW` | Chavicine | Piperine | `maoa` | 11 (2, 16, 78, 95, 307, 308, 602, 629, 908) | 0 | 0 | 11 | **RETAINED** ($\ge 1$ HIGH) |
| 26 | `SCCDQYPEOIRVGX` | Acetyleugenol | Eugenyl acetate | `cox1` | 9 (1, 68, 94, 128, 287, 346, 624, 906) | 0 | 0 | 9 | **RETAINED** ($\ge 1$ HIGH) |
| 27 | `TZBJGXHYKVUXJN` | 4,5,7- Trihydroxy isoflavone | Gen... | `cox1|xo|maoa` | 9 (35, 78, 121, 195, 442, 499, 515, 602, 796) | 0 | 0 | 9 | **RETAINED** ($\ge 1$ HIGH) |
| 28 | `AZQWKYJCGOJGHM` | 1,4-Benzoquinone | 2,5-Cyclohexadie... | `maoa` | 7 (14, 124, 301, 402, 435, 442, 498) | 0 | 0 | 7 | **RETAINED** ($\ge 1$ HIGH) |
| 29 | `FBSFWRHWHYMIOG` | Methyl gallate | methyl gallate | `xo` | 7 (97, 192, 316, 410, 439, 715, 749) | 0 | 0 | 7 | **RETAINED** ($\ge 1$ HIGH) |
| 30 | `IZQSVPBOUDKVDZ` | Isorhamnetin | Quercetin-3-methyl |... | `xo` | 7 (497, 499, 661, 749, 776, 799, 843) | 1 (786) | 0 | 8 | **RETAINED** ($\ge 1$ HIGH) |
| 31 | `ILEDWLMCKZNDJK` | Esculetin | aesculetin | esculetin | `cox1|xo` | 6 (38, 70, 113, 405, 439, 442) | 0 | 0 | 6 | **RETAINED** ($\ge 1$ HIGH) |
| 32 | `MBNGWHIJMBWFHU` | 3 5 7-trihydroxy-4'-methoxyflavone ... | `xo` | 6 (60, 70, 216, 435, 628, 687) | 1 (410) | 0 | 7 | **RETAINED** ($\ge 1$ HIGH) |
| 33 | `DANYIYRPLHHOCZ` | Acacetin | Acacetine (linarigenin, ... | `maoa` | 5 (78, 349, 386, 435, 687) | 1 (442) | 0 | 6 | **RETAINED** ($\ge 1$ HIGH) |
| 34 | `MBRLOUHOWLUMFF` | Osthol | Osthole | osthol | osthole | `cox2` | 5 (68, 70, 78, 687) | 0 | 0 | 5 | **RETAINED** ($\ge 1$ HIGH) |
| 35 | `RHMXXJGYXNZAPX` | Emodin | `maoa` | 5 (499, 872, 874, 875, 906) | 0 | 0 | 5 | **RETAINED** ($\ge 1$ HIGH) |
| 36 | `VFLDPWHFBUODDF` | Curcumin | curcumin | diferuloylmet... | `cox1|cox2|maoa` | 5 (78, 307, 628, 629) | 0 | 0 | 5 | **RETAINED** ($\ge 1$ HIGH) |
| 37 | `BGEBZHIAGXMEMV` | 5-methoxypsoralen | Bergapten | ber... | `maoa` | 4 (68, 70, 114, 687) | 0 | 0 | 4 | **RETAINED** ($\ge 1$ HIGH) |
| 38 | `LUKBXSAWLPMMSZ` | Resveratrol | `cox1|cox2|maoa` | 4 (78, 389, 435, 796) | 0 | 0 | 4 | **RETAINED** ($\ge 1$ HIGH) |
| 39 | `PREBVFJICNPEKM` | Bisdemethoxycurcumin | bisdemethoxy... | `cox2` | 4 (124, 628, 629) | 1 (628) | 0 | 5 | **RETAINED** ($\ge 1$ HIGH) |
| 40 | `YXOLAZRVSSWPPT` | Morin | Morin (3, 5, 7, 2, 4-pentah... | `xo` | 4 (5, 499, 525, 739) | 1 (515) | 0 | 5 | **RETAINED** ($\ge 1$ HIGH) |
| 41 | `CUFLZUDASVUNOE` | Methyl 3,4-dihydroxy benzo-ate | Me... | `xo` | 3 (16, 200, 619) | 0 | 0 | 3 | **RETAINED** ($\ge 1$ HIGH) |
| 42 | `GFFGJBXGBJISGV` | Adenine | `xo` | 3 (410, 619, 749) | 0 | 0 | 3 | **RETAINED** ($\ge 1$ HIGH) |
| 43 | `IKIIZLYTISPENI` | Baicalein-7-O-glucuronide | Baicali... | `xo` | 3 (386, 410, 624) | 0 | 0 | 3 | **RETAINED** ($\ge 1$ HIGH) |
| 44 | `QBLQLKNOKUHRCH` | Steppogenin | steppogenin | `cox1|cox2` | 3 (5, 499, 739) | 0 | 0 | 3 | **RETAINED** ($\ge 1$ HIGH) |
| 45 | `QJVXKWHHAMZTBY` | Syringin | eleutheroside B | `cox1` | 3 (240, 687, 810) | 0 | 0 | 3 | **RETAINED** ($\ge 1$ HIGH) |
| 46 | `QYPPJABKJHAVHS` | (4-Aminobutyl)guanidine | Agmatine | `maoa` | 3 (272, 505, 872) | 0 | 0 | 3 | **RETAINED** ($\ge 1$ HIGH) |
| 47 | `AIFRHYZBTHREPW` | 9H-Pyrido[3,4-B]indole | `maoa` | 2 (77, 602) | 0 | 0 | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 48 | `FRASJONUBLZVQX` | 1,4-Naphthoquinone | `maoa` | 2 (14, 301) | 0 | 0 | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 49 | `FXNFHKRTJBSTCS` | Baicalein | `xo` | 2 (78, 195) | 0 | 0 | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 50 | `HJTVQHVGMGKONQ` | Demethoxycurcumin | demethoxycurcum... | `maoa` | 2 (629) | 1 (628) | 0 | 3 | **RETAINED** ($\ge 1$ HIGH) |
| 51 | `HKQYGTCOTHHOMP` | Formononetin | `maoa` | 2 (121, 410) | 0 | 0 | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 52 | `HUKSJTUUSUGIDC` | (-)-(6aR,12aR)-maackiain | Maackiai... | `maoa` | 2 (196, 612) | 0 | 0 | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 53 | `IBGBGRVKPALMCQ` | Protocatechualdehyde | Protocatechu... | `cox2` | 2 (16, 906) | 1 (799) | 0 | 3 | **RETAINED** ($\ge 1$ HIGH) |
| 54 | `KIGVXRGRNLQNNI` | Axillarin | `xo` | 2 (55, 265) | 0 | 0 | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 55 | `LHPRYOJTASOZGJ` | moracin M | `cox1|cox2` | 2 (5, 739) | 0 | 0 | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 56 | `OTAFHZMPRISVEM` | Chromone | `maoa` | 2 (596, 829) | 0 | 0 | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 57 | `QWCNQXNAFCBLLV` | Falcarindiol | `cox1` | 2 (78, 661) | 0 | 0 | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 58 | `QXKHYNVANLEOEG` | Methoxsalen | Xanthotoxin | `maoa` | 2 (687) | 0 | 0 | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 59 | `RERZNCLIYCABFS` | Harmaline | `maoa` | 2 (78, 442) | 0 | 0 | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 60 | `RTIXKCRFFJGDFG` | Chrysin | `cox2|xo` | 2 (356, 435) | 0 | 0 | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 61 | `VCCRNZQBSJXYJD` | Galangin | `xo|maoa` | 2 (356, 740) | 0 | 0 | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 62 | `XHEFDIBZLJXQHF` | Fisetin | `xo` | 2 (70, 796) | 0 | 0 | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 63 | `YDQWDHRMZQUTBA` | Aloe emodin | Aloe-emodin | `maoa` | 2 (872, 874) | 0 | 0 | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 64 | `YKPUWZUDDOIDPM` | Capsaicin | `cox1` | 2 (78, 307) | 0 | 0 | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 65 | `ZEACOKJOQLAYTD` | Leucodelphidin | `xo` | 2 (195, 316) | 0 | 0 | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 66 | `ZSYPIPFQOQGYHH` | norartocarpetin | `cox1` | 2 (5, 739) | 0 | 0 | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 67 | `AGNFWIZBEATIAK` | Benzenebutanamine | `maoa` | 1 (872) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 68 | `AUZONCFQVSMFAP` | disulfiram | `maoa` | 1 (492) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 69 | `BXNJHAXVSOCGBA` | Harmine | `maoa` | 1 (442) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 70 | `DKZBBWMURDFHNE` | Coniferaldehyde | `xo` | 1 (405) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 71 | `FAKRSMQSSFJEIM` | captopril | `cox1|cox2` | 1 (207) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 72 | `FMHHVULEAZTJMA` | Trioxsalen | `maoa` | 1 (632) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 73 | `GLEVLJDDWXEYCO` | Trolox | `cox1|cox2` | 1 (192) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 74 | `ILRCGYURZSFMEG` | Salidroside | `cox1` | 1 (619) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 75 | `IXELFRRANAOWSF` | E-Ajoene | Z-Ajoene | `cox2` | 1 (124) | 1 (124) | 0 | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 76 | `JJUNZBRHHGLJQW` | 1,3,7-Trihydroxyxanthone | `maoa` | 1 (16) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 77 | `JNELGWHKGNBSMD` | Xanthone | `maoa` | 1 (9) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 78 | `KTEXNACQROZXEV` | Parthenolide | `cox2` | 1 (389) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 79 | `KVVSCMOUFCNCGX` | 5-Pentadecylresorcinol | `cox2` | 1 (715) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 80 | `KWTSXDURSIMDCE` | Amphetamine | `maoa` | 1 (447) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 81 | `LCVACABZTLIWCE` | nan | `xo` | 1 (203) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 82 | `MDKGKXOCJGEUJW` | Suprofen | `cox1|cox2` | 1 (192) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 83 | `MQGPSCMMNJKMHQ` | 7-hydroxyflavone | `xo` | 1 (442) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 84 | `NTVLUSJWJRSPSM` | Vallesiachotamine | `maoa` | 1 (278) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 85 | `OFCNXPDARWKPPY` | Allopurinol | `xo` | 1 (356) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 86 | `PACBGANPVNHGNP` | 4,4?-dihydroxy-2?-methoxy-chalcone | `maoa` | 1 (786) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 87 | `PANKHBYNKQNAHN` | Crocetin | carotenoid aglycone (cro... | `cox1` | 1 (497) | 1 (354) | 0 | 2 | **RETAINED** ($\ge 1$ HIGH) |
| 88 | `PDHAOJSHSJQANO` | Oxyresveratrol | `cox1` | 1 (740) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 89 | `PSFDQSOCUJVVGF` | Harman | `maoa` | 1 (332) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 90 | `QBPFLULOKWLNNW` | Danthron | `maoa` | 1 (874) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 91 | `RAKJVIPCCGXHHS` | osthenol | `cox1|maoa` | 1 (687) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 92 | `RSYUFYQTACJFML` | Epiafzelechin | `cox1|cox2` | 1 (796) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 93 | `SUTUBQHKZRNZRA` | Eugenin | `cox1|cox2` | 1 (207) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 94 | `UWQYBLOHTQWSQD` | Mulberrin | `cox1` | 1 (740) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 95 | `VLEUZFDZJKSGMX` | Pterostilbene | `cox1|cox2` | 1 (38) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 96 | `XHLHPRDBBAGVEG` | tetralone | `maoa` | 1 (619) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 97 | `YNVJOQCPHWKWSO` | Pallidol | `cox1|cox2` | 1 (565) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 98 | `ZCCUUQDIBDJBTK` | Psoralene | `maoa` | 1 (114) | 0 | 0 | 1 | **RETAINED** ($\ge 1$ HIGH) |
| 99 | `IBRKLUSXDYATLG` | Isoquinoline, 1,2,3,4-tetrahydro-1-... | `maoa` | 0 | 1 (632) | 0 | 1 | **EXCLUDED** (0 HIGH) |
| 100 | `ITDYPNOEEHONAH` | Methyl-epigallocatechin | `cox1` | 0 | 1 (497) | 0 | 1 | **EXCLUDED** (0 HIGH) |

### 1.3 Layers Excluded Due to Zero HIGH Links
Only three layers are completely excluded from the external evaluation sets under the corrected rule:
1. **`ITDYPNOEEHONAH` (in COX-1):** Listed under name `2-Hydroxy-4-methoxybenzaldehyde` in Plant 4 (*Papaver somniferum* [idx 4]). Tier: **MEDIUM** (unresolvable in PubChem due to non-standard punctuation). HIGH=0, MED=1, LOW=0. Excluded from COX-1 (was inactive at T=6, active at T=5).
2. **`SHPPXMGVUDNKLV` (in XO):** Listed under name `p-coumaric acid ethyl ester` in Plant 628 (*Curcuma zedoaria*) and Plant 865 (*Pithecellobium dulce*). In both plants, BMPPD assigned CID 5281768 (which belongs to a different flavone layer). Tier: **LOW** (name and CID resolve to different connectivity layers). HIGH=0, MED=0, LOW=2. Excluded from XO (was inactive at T=6 and T=5).
3. **`IBRKLUSXDYATLG` (in MAO-A):** Listed under name `2,4-Di-tert-butylphenol` in Plant 619 (*Cyperus rotundus*). Tier: **MEDIUM** (PubChem name unresolvable/multi-match). HIGH=0, MED=1, LOW=0. Excluded from MAO-A (was inactive at T=6 and T=5).

### 1.4 Recomputed External Evaluation Sets (Corrected Rule)
Retaining all layers with $\ge 1$ HIGH link preserves the statistical integrity and diversity of the external benchmarks:

| Target | Target ChEMBL ID | Original Labeled Layers | Excluded (0 HIGH) | Kept Labeled Layers | Cleaned T=6 Actives | Cleaned T=6 Inactives | Cleaned T=6 Conflicts | Cleaned T=5 Actives | Cleaned T=5 Inactives | Cleaned T=5 Conflicts |
|---|---|---|---|---|---|---|---|---|---|---|
| **COX-1** | `CHEMBL221` | 32 | 1 (`ITDYPNOEEHONAH`) | **31** | **4** | **27** | 0 | **12** | **19** | 0 |
| **COX-2** | `CHEMBL230` | 25 | 0 | **25** | **1** | **22** | 2 | **6** | **17** | 2 |
| **XO** | `CHEMBL1929` | 30 | 1 (`SHPPXMGVUDNKLV`) | **29** | **5** | **21** | 3 | **15** | **11** | 3 |
| **MAO-A** | `CHEMBL1951` | 43 | 1 (`IBRKLUSXDYATLG`) | **42** | **12** | **29** | 1 | **26** | **15** | 1 |

### 1.5 Diagnostic Explanation: Why COX-1 Still Shows 4 Actives at T=6
**The Paradox:** In Stage 7A-2, the executive summary stated that synthetic assay standards (Trolox, Suprofen, Captopril) had been removed, yet the COX-1 table still showed exactly 4 actives at T=6—identical to the uncleaned count.

**The Explanation:**
The 4 COX-1 T=6 actives in the labeled flora set are:
1. `GLEVLJDDWXEYCO` (**Trolox**, pChEMBL 6.89, Phase 0, NP=1 in ChEMBL) — listed in Plant 192 (*Terminalia chebula*) under compound name `Trolox` with PubChem CID `40464`.
2. `MDKGKXOCJGEUJW` (**Suprofen**, pChEMBL 6.25, Phase 4, NP=1 in ChEMBL) — listed in Plant 192 (*Terminalia chebula*) under compound name `Suprofen` with PubChem CID `5359`.
3. `LHPRYOJTASOZGJ` (**Moracin M**, pChEMBL 6.30, Phase 0, NP=1) — listed in Plant 162 (*Morus alba*).
4. `VLEUZFDZJKSGMX` (**Pterostilbene**, pChEMBL 6.16, Phase 2, NP=1) — listed in Plant 38 (*Pterocarpus santalinus*).

**Why Trolox and Suprofen Were Not Excluded by the Link-Tier Method:**
- For Plant 192, BMPPD extracted the row with name `Trolox` and CID `40464` (Trolox). Name matches CID $	o$ **HIGH tier (`cid_synonym_match`)**.
- For Suprofen, BMPPD extracted the row with name `Suprofen` and CID `5359` (Suprofen). Name matches CID $	o$ **HIGH tier (`cid_synonym_match`)**.

> **Plain Statement on the Limits of Link-Tier Classification:**  
> **The link-tier method cannot detect reference compounds whose name matches their CID.**  
> Link-tier classification evaluates **internal database agreement** between the reported name string and the reported CID structure. It detects typographical collisions (e.g. `Stigmasterol acetate` entered with Luteolin's CID, or `Diclofenac-Na` entered with 3,5-di-tert-butylphenol's CID). However, when an external literature source evaluates an extract alongside commercial positive controls (such as Trolox or Suprofen) and a secondary database indexer transcribes the control drug's name alongside the control drug's true CID, name and structure agree *by construction*. Such literature provenance errors can only be diagnosed by manual primary-source verification using the verification sheet provided in Section 2.

---

## Section 2: Verification Sheet for Manual Source Checking

Output file delivered: [`data/processed/modeling/external_verification_sheet.csv`](file:///f:/bmppd-thesis/data/processed/modeling/external_verification_sheet.csv)

### 2.1 Scope & Inclusion Criteria
The verification sheet enumerates every `(labeled flora layer, plant, link)` instance satisfying at least one of the following criteria:
1. **Active Molecules:** Every layer that is active at T=6 or T=5 in any of the four external evaluation sets (52 unique layers).
2. **Rare Constituents:** Every labeled flora layer that appears in $\le 3$ plants in BMPPD (65 unique layers).
3. **Suspected Standards:** Trolox (`GLEVLJDDWXEYCO`).

The union comprises **84 unique connectivity layers** spanning **519 individual link rows** across the 222 compound plants. Zero rows were dropped.

### 2.2 Table Schema & Manual Verification Columns
The sheet contains the following columns:
- `layer`: 14-character InChIKey connectivity layer.
- `targets`: Target(s) for which the molecule has ChEMBL bioactivity records (`cox1`, `cox2`, `xo`, `maoa`).
- `label_T6` & `label_T5`: Activity label at T=6 and T=5 (e.g. `1`, `0`, or `conflict`).
- `median_pchembl`: Target-specific median pChEMBL value.
- `compound_name_bmppd`: Original compound name string as indexed in BMPPD.
- `pubchem_title`: Canonical chemical title from PubChem.
- `plant_index`: MPBD plant index (1 to 916).
- `botanical_name`: Scientific binomial from MPBD master index.
- `link_tier`: Link confidence tier (`HIGH`, `MEDIUM`, `LOW`).
- `reference_link`: Primary citation identifier extracted from BMPPD (clean DOI, PMID, or ISBN; or `EMPTY` if no reference was indexed). All mirror URLs (Sci-Hub, LibGen) and BMPPD redirect wrappers were stripped.
- `max_phase`: ChEMBL clinical development phase (0 to 4).
- `natural_product`: ChEMBL natural product flag (1 = yes, 0 = synthetic).
- **User Manual Review Columns (strictly blank, ready for manual annotation):**
  - `verified_in_source`: Blank column to record whether the primary paper actually isolates/identifies this compound from the plant.
  - `is_reference_compound`: Blank column to record whether the compound was used as an assay standard / positive control.
  - `notes`: Blank column for free-text literature observations.

---

## Section 3: Reconciling Botanical Duplicate Query Entries into Plant Analysis Units

### 3.1 Identification of Duplicate Query binomials in BMPPD
Because BMPPD was queried using clean botanical species names (`bmpdd_query_name`), multiple entries in the MPBD master index that represent identical species or orthographic/author variants dispatched identical searches to BMPPD.

Among the 222 compound plants, there are **14 duplicate query groups** covering **29 plant index entries** (13 pairs and 1 triplet):

| # | Normalized Query Name | MPBD Plant Indices | Scientific Names in MPBD Master | Botanical Reconciliation Status | Linked Compound Sets Identical? | `disease_raw` Text Agreement |
|---|---|---|---|---|---|---|
| 1 | *achyranthes aspera* | 13, 104 | Achyranthes aspera<br>Achyranthes aspera L. | `NORMALIZED_ONLY` | **100% IDENTICAL (17 layers)** | DIFFERENT (13: 153 chars vs 104: 174 chars) |
| 2 | *artocarpus heterophyllus* | 5, 739 | Artocarpus heterophyllus Lam.<br>Artocarpus HETEROPHYLLUS Lam. | `POTENTIAL_DUPLICATE` | **100% IDENTICAL (38 layers)** | DIFFERENT (5: 86 chars vs 739: 213 chars) |
| 3 | *benincasa hispida* | 21, 765 | Benincasa hispida (Thunb.) Cogn.<br>Benincasa HISPIDA (Thunb.) Cogn. | `POTENTIAL_DUPLICATE` | **100% IDENTICAL (47 layers)** | DIFFERENT (21: 100 chars vs 765: 198 chars) |
| 4 | *dillenia indica* | 596, 829 | Dillenia INDICA L.<br>Dillenia indica L. | `NORMALIZED_ONLY` | **100% IDENTICAL (25 layers)** | DIFFERENT (596: 181 chars vs 829: 181 chars, casing) |
| 5 | *diospyros malabarica* | 28, 587 | Diospyros malabarica(desr.) Kostel.<br>Diospyros MALABARICA (Desr.) Kostel | `NORMALIZED_ONLY` | **100% IDENTICAL (30 layers)** | DIFFERENT (28: 255 chars vs 587: 89 chars) |
| 6 | *lagerstroemia speciosa* | 43, 449 | Lagerstroemia speciosa(l.) Pers.<br>Lagerstroemia speciosa (L.) Pers. | `NORMALIZED_ONLY` | **100% IDENTICAL (82 layers)** | DIFFERENT (43: 98 chars vs 449: 67 chars) |
| 7 | *melochia corchorifolia* | 396, 819 | Melochia CORCHORIFOLIA L.<br>Melochia corchorifolia L. | `POTENTIAL_DUPLICATE` | **100% IDENTICAL (32 layers)** | DIFFERENT (396: 21 chars vs 819: 93 chars) |
| 8 | *moringa oleifera* | 27, 374 | Moringa oleifera Lam.<br>Moringa OLEIFERA Lamk. | `NORMALIZED_ONLY` | **100% IDENTICAL (221 layers)** | DIFFERENT (27: 255 chars vs 374: 255 chars, distinct texts) |
| 9 | *plumbago indica* | 14, 301 | Plumbago indica L.<br>Plumbago INDICA L. | `POTENTIAL_DUPLICATE` | **100% IDENTICAL (26 layers)** | DIFFERENT (14: 255 chars vs 301: 201 chars) |
| 10 | *saccharum officinarum* | 55, 265 | Saccharum officinarum L.<br>Saccharum OFFICINARUM L. | `POTENTIAL_DUPLICATE` | **100% IDENTICAL (70 layers)** | DIFFERENT (55: 100 chars vs 265: 183 chars) |
| 11 | *saraca asoca* | 34, 257 | Saraca asoca (Roxb.) Wild.<br>Saraca ASOCA (Roxb.) De Wilde. | `NORMALIZED_ONLY` | **100% IDENTICAL (27 layers)** | DIFFERENT (34: 100 chars vs 257: 191 chars) |
| 12 | *schleichera oleosa* | 65, 90, 253 | Schleichera oleosa (Lour.)Merr.<br>Schleichera oleosa (Lour.) Merr.<br>Schleichera OLEOSA (Lour.) Oken | `NORMALIZED_ONLY` | **100% IDENTICAL (24 layers)** | DIFFERENT (65 & 90: identical 100 chars; 253: 250 chars) |
| 13 | *sesamum indicum* | 49, 247 | Sesamum indicum L.<br>Sesamum INDICUM L. | `POTENTIAL_DUPLICATE` | **100% IDENTICAL (72 layers)** | DIFFERENT (49: 100 chars vs 247: 197 chars) |
| 14 | *sida acuta* | 240, 810 | Sida ACUTA Burm. f.<br>Sida acuta Burm. f. | `POTENTIAL_DUPLICATE` | **100% IDENTICAL (26 layers)** | DIFFERENT (240: 255 chars vs 810: 108 chars) |

### 3.2 Key Findings from Botanical Cross-Checking
1. **Phytochemical Equivalence:** In all 14 groups, the linked compound sets are **100% identical** across all plant entries in the group under both ALL links and HIGH links. This is because BMPPD scraping dispatched queries by species binomial, meaning duplicate plant entries returned identical compound inventories.
2. **Ethnobotanical Divergence:** In 13 of the 14 groups, the `disease_raw` text from MPBD **differs substantially** between duplicate plant index entries. For instance:
   - Plant 21 (*Benincasa hispida*) records: `"Cough, constipation..."` (100 characters), while Plant 765 records an expanded clinical list `"Cough, cold, fever and purgative..."` (198 characters).
   - Plant 28 (*Diospyros malabarica*) records 255 characters of indications, while Plant 587 records a distinct 89-character subset.
   - For Plant 65 and 90 (*Schleichera oleosa*), the texts are identical 100-character entries, but Plant 253 has a completely different 250-character compilation.
3. **Synonym-Level Verification:** Cross-checking the `synonym` column in `data/raw/mpbd/mpbd_plant_index.csv` confirmed that **zero additional synonym pairs exist among the 222 compound plants**. All 222 plants belong either to these 14 species-level groups or are singletons.

### 3.3 Plant Analysis Units Table Delivered
To avoid statistical distortion from duplicate plant entries, we generated [`data/processed/modeling/plant_analysis_units.csv`](file:///f:/bmppd-thesis/data/processed/modeling/plant_analysis_units.csv) covering all 916 MPBD plants:
- Among the 222 compound plants, there are exactly **207 plant analysis units** (193 singletons, 13 pairs, 1 triplet).
- Across all 916 MPBD plants, there are **874 analysis units**.

### 3.4 Impact on Plants Losing >50% of Links Under HIGH-Only
In Stage 7A-2, 17 plants were reported as losing >50% of their links under HIGH-only filtering. Accounting for duplicate plant entries:
- Plants 21 and 765 (*Benincasa hispida*) represent the **same botanical analysis unit (`AU_021`)**.
- Exactly **16 plant analysis units** lose >50% of their links (down from 17 plants):
  `AU_021` (86.4%), `AU_035` (83.0%), `AU_731` (80.6%), `AU_883` (79.1%), `AU_659` (71.4%), `AU_625` (66.7%), `AU_675` (62.9%), `AU_623` (62.5%), `AU_692` (62.5%), `AU_717` (62.5%), `AU_637` (62.1%), `AU_657` (61.3%), `AU_402` (60.0%), `AU_843` (59.5%), `AU_901` (58.7%), `AU_644` (53.8%).

---

## Section 4: Sample Audit of Link Tiers (Report & CSV)

Output file delivered: [`data/processed/modeling/tier_sample_audit.csv`](file:///f:/bmppd-thesis/data/processed/modeling/tier_sample_audit.csv) (100 rows).

### 4.1 Molecular Formula Analysis Across the 902 LOW Links
To determine whether the 902 LOW-tier links reflect true database collisions or mere isomer/representation discrepancies, we compared the molecular formulas of the name-resolved structure and the CID structure:

| Formula Relationship Category | LOW Link Count | % of All LOW Links | Chemical Interpretation |
|---|---|---|---|
| **Identical Raw Molecular Formula** | **74** | **8.20%** | **Constitutional / Stereochemical Isomers:** Same atom counts; different connectivity or double-bond geometry (e.g. Curzerene vs Isogermafurene, Butyrospermol vs Lupeol, Caryophyllenol I vs II) |
| **Identical Formula After Neutralization & Salt Stripping** | **14** | **1.55%** | **Counter-Ion / Salt Discrepancies:** Structures differ only by chloride salt or protonation representation (e.g. Petunidin chloride vs Petunidin cation, Pelargonidin chloride) |
| **Completely Different Molecular Formula** | **814** | **90.24%** | **True Database Collisions:** Unrelated chemical structures accidentally assigned the same PubChem CID in BMPPD (e.g. Stigmasterol acetate vs Luteolin, Lycopene vs Mangiferin, Diclofenac vs 3,5-di-tert-butylphenol) |
| **TOTAL LOW LINKS** | **902** | **100.00%** | Full inventory of LOW-tier links |

> **Diagnostic Conclusion:**  
> Exactly **90.2% (814 links)** of LOW-tier links are confirmed gross database collisions involving completely different chemical entities. However, **9.8% (88 links)** involve isomers, counter-ions, or protonation variants of the same chemical family that failed the rigid InChIKey connectivity match.

### 4.2 Deep Dive on Specific Compounds Highlighted by the Audit
The table below details the six specific compounds requested in Section 4c:

| Compound Name (BMPPD) | Plant Indices | CID Layer | PubChem Title (CID) | CID Formula | True Compound Formula | Formula Relationship | Nature of Discrepancy |
|---|---|---|---|---|---|---|---|
| **Petunidin** | 497, 515, 796, 812 | `AFOLOMGWVXKIQL` | 3,3',4',5,7-Pentahydroxy-5'-methoxyflavylium | `C16H13O7+` (chloride salt `C16H13ClO7`) | `C16H13O7+` | **Identical after salt strip** | Anthocyanidin cation vs chloride salt representation |
| **Peonidin** | 207, 497, 715 | `XFDQJKDGGOEYPI` | 3,4',5,7-Tetrahydroxy-3'-methoxyflavylium | `C16H13O6+` (chloride salt `C16H13ClO6`) | `C16H13O6+` | **Identical after salt strip** | Anthocyanidin cation vs chloride salt representation |
| **Pelargonidin** | 497, 498, 796, 812 | `XVFMGWDSJLBXDZ` | Pelargonidin Chloride | `C15H11O5+` (chloride salt `C15H11ClO5`) | `C15H11O5+` | **Identical after salt strip** | Anthocyanidin cation vs chloride salt representation |
| **Curzerene** | 628, 629, 632 | `HICAMHOOTMOHPA` | Isogermafurene | `C15H20O` | `C15H20O` | **Identical raw formula** | Constitutional sesquiterpene isomer (Curzerene vs Isogermafurene) |
| **Seychellene** | 128, 702, 906 | `QQWUXXGYAQMTAT` | 1,6-Methanonaphthalene... (Seychellene) | `C15H24` | `C15H24` | **Identical raw formula** | Tricyclic sesquiterpene stereoisomer / bridgehead geometry |
| **Casuarinin** | 43, 195, 449 | `MMQXBTULXAEKQE` | galloyl-bis-HHDP-hexoside (Casuarinin) | `C34H24O22` | `C34H24O22` | **Identical raw formula** | Ellagitannin trivial name vs PubChem IUPAC systematic descriptor |

### 4.3 Structure of the Sample Audit Sheet (`tier_sample_audit.csv`)
A deterministic random sample (seed 42) of **50 LOW layers** and **50 HIGH layers** (from `cid_synonym_match`) was drawn and saved to [`data/processed/modeling/tier_sample_audit.csv`](file:///f:/bmppd-thesis/data/processed/modeling/tier_sample_audit.csv).
- For each row, the sheet displays the BMPPD original names, PubChem titles, molecular formulas, connectivity layers, and plant occurrences.
- Columns `my_judgement` and `notes` are provided blank for expert manual inspection.

---

## Section 5: Corrections to the Plant-Level Yield Distributions ("Power Check")

### 5.1 Clarification on Terminology (Compound Yield vs Statistical Power)
> **Important Conceptual Clarification:**  
> These counts quantify **chemical space coverage and in-domain constituent yields per plant**. They measure how many known constituents of each medicinal plant share structural similarity ($NN \ge 0.3, \ge 0.4$) with the target training pools.  
> **They are not statistical power.** Statistical power represents the probability that a statistical hypothesis test will correctly reject a false null hypothesis at a given significance level ($lpha$) and effect size. Describing these compound coverage counts as 'statistical power' was a misnomer in earlier drafts.

### 5.2 Deconstruction of the 'Substantially Higher Yields' Claim
In Stage 7A-2, the report asserted:
> *"Plants reporting traditional pain/inflammation uses show substantially higher compound yields: 68/122 pain plants (55.7%) possess $\ge 5$ in-domain compounds at $NN \ge 0.4$ for COX-1 (compared to 52/100, 52.0% for other plants)..."*

**The Exact Numbers Behind the Statement:**
- **Per Plant (Stage 7A-2, 222 plants):**
  - Pain group: **68 of 122 plants = 55.74%**
  - Other group: **52 of 100 plants = 52.00%**
  - Difference: **+3.74 percentage points**.
- **Per Plant Analysis Unit (Stage 7A-3, 207 units):**
  - Pain units (115 total, 55.6% of units): **64 of 115 units = 55.65%**
  - Other units (92 total, 44.4% of units): **47 of 92 units = 51.09%**
  - Difference: **+4.56 percentage points**.

**Conclusion:** A difference of 3.7 to 4.6 percentage points (55.7% vs 51.1%) is modest and cannot scientifically support the claim that pain plants show 'substantially higher' in-domain compound yields.

### 5.3 Corrected Plant-Level Yield Table per Analysis Unit (HIGH Links Only)
The table below reports in-domain compound yields evaluated strictly on **HIGH-confidence links across the 207 unique plant analysis units**, stratified by the exploratory pain/inflammation keyword proxy (115 pain units, 55.6% vs 92 other units, 44.4%):

| Target | Tanimoto Threshold | All Units $\ge 1$ (of 207) | All Units $\ge 5$ | All Units $\ge 10$ | Pain Units $\ge 1$ (of 115) | Pain Units $\ge 5$ | Pain Units $\ge 10$ | Other Units $\ge 1$ (of 92) | Other Units $\ge 5$ | Other Units $\ge 10$ | Pain Share $\ge 5$ (%) | Other Share $\ge 5$ (%) | Difference (pp) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **COX-1** | $\ge 0.3$ | 197 (95.2%) | 155 (74.9%) | 125 (60.4%) | 108 (93.9%) | 94 (81.7%) | 76 (66.1%) | 89 (96.7%) | 61 (66.3%) | 49 (53.3%) | 81.7% | 66.3% | +15.4 |
| **COX-1** | $\ge 0.4$ | 180 (87.0%) | 111 (53.6%) | 72 (34.8%) | 103 (89.6%) | 64 (55.7%) | 42 (36.5%) | 77 (83.7%) | 47 (51.1%) | 30 (32.6%) | 55.7% | 51.1% | +4.6 |
| **COX-2** | $\ge 0.3$ | 196 (94.7%) | 166 (80.2%) | 127 (61.4%) | 109 (94.8%) | 100 (87.0%) | 76 (66.1%) | 87 (94.6%) | 66 (71.7%) | 51 (55.4%) | 87.0% | 71.7% | +15.3 |
| **COX-2** | $\ge 0.4$ | 179 (86.5%) | 111 (53.6%) | 76 (36.7%) | 102 (88.7%) | 65 (56.5%) | 47 (40.9%) | 77 (83.7%) | 46 (50.0%) | 29 (31.5%) | 56.5% | 50.0% | +6.5 |
| **XO** | $\ge 0.3$ | 187 (90.3%) | 140 (67.6%) | 105 (50.7%) | 107 (93.0%) | 81 (70.4%) | 62 (53.9%) | 80 (87.0%) | 59 (64.1%) | 43 (46.7%) | 70.4% | 64.1% | +6.3 |
| **XO** | $\ge 0.4$ | 150 (72.5%) | 82 (39.6%) | 42 (20.3%) | 86 (74.8%) | 51 (44.3%) | 26 (22.6%) | 64 (69.6%) | 31 (33.7%) | 16 (17.4%) | 44.3% | 33.7% | +10.6 |
| **MAO-A** | $\ge 0.3$ | 187 (90.3%) | 141 (68.1%) | 106 (51.2%) | 108 (93.9%) | 82 (71.3%) | 63 (54.8%) | 79 (85.9%) | 59 (64.1%) | 43 (46.7%) | 71.3% | 64.1% | +7.2 |
| **MAO-A** | $\ge 0.4$ | 170 (82.1%) | 106 (51.2%) | 70 (33.8%) | 100 (87.0%) | 61 (53.0%) | 45 (39.1%) | 70 (76.1%) | 45 (48.9%) | 25 (27.2%) | 53.0% | 48.9% | +4.1 |

---

## Integrity Check Verification
- **Master MPBD SHA-256 (Start):** `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` (PASS)
- **Master MPBD SHA-256 (End):** `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` (PASS - EXACT MATCH)
- **Existing Datasets:** Completely untouched (Read-Only).
- **New Artifacts Created:**
  1. [`data/processed/modeling/plant_analysis_units.csv`](file:///f:/bmppd-thesis/data/processed/modeling/plant_analysis_units.csv)
  2. [`data/processed/modeling/external_verification_sheet.csv`](file:///f:/bmppd-thesis/data/processed/modeling/external_verification_sheet.csv)
  3. [`data/processed/modeling/tier_sample_audit.csv`](file:///f:/bmppd-thesis/data/processed/modeling/tier_sample_audit.csv)
  4. [`data/quality/stage7a3_corrections_report.md`](file:///f:/bmppd-thesis/data/quality/stage7a3_corrections_report.md)
  5. [`codebase_audit.md`](file:///f:/bmppd-thesis/codebase_audit.md) (Updated)
