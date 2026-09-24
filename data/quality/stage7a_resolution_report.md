# Stage 7A: Chemical Structure Resolution Report

**Execution Timestamp**: 2026-09-24T10:46:05.486826+00:00  
**Master MPBD SHA-256 (Start & End)**: `0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7` (Integrity Verified)  
**Total Runtime**: 45.10 seconds (0.75 minutes)  
**Network Calls Made**: 28  
**Cache Hits**: 11713  

---

## 1. Unique Entities Processed

| Match Classification | Unique Count | % of Workload | Definition / Description |
| :--- | :---: | :---: | :--- |
| **`CID-based`** (Direct) | **7,082** | 66.53% | Directly resolved via numeric PubChem CID in BMPPD |
| **`exact_match`** (Name) | **2,283** | 21.45% | Name-based lookup returning exactly 1 CID |
| **`multiple_matches`** | **81** | 0.76% | Name-based lookup returning >1 CIDs (logged for review) |
| **`no_match`** | **970** | 9.11% | PubChem returned 404 (no compound found for string) |
| **`skipped_nonspecific`** | **8** | 0.08% | Mixture/extract terms skipped without API call |
| **`skipped_encoding_loss`**| **214** | 2.01% | Corrupted characters ('?', '\ufffd') skipped without API call |
| **`fetch_error`** | **7** | 0.07% | Transient network errors remaining after 3 retry passes |
| **Total Workload Entities** | **10,645** | **100.00%** | |
| **Total Resolved Entities** | **9,365** | **87.98%** | Structure resolved (`CID-based` + `exact_match`) |

---

## 2. Row-Level Dataset Coverage

- **Total Plant–Compound Rows**: **24,001**
- **Rows Successfully Resolved**: **22,505** (**93.77%**)
- **Rows Missing Structure**: **1,496** (**6.23%**)

---

## 3. Non-Specific Skipped Names (`skipped_nonspecific`)

Total Count: **8**

| # | Compound Name (Original) | Cleaned Query | Triggering Regex Pattern | Single Compound Assessment |
| :-: | :--- | :--- | :--- | :--- |
| 1 | `Oleoresin tumeric` | `Oleoresin tumeric` | `.*\boleoresin\b.*` | True mixture / extract |
| 2 | `Alkaloids` | `Alkaloids` | `^(?:total\s+)?(?:alkaloids|flavonoids|saponins|tannins|phenolics|terpenoids|glycosides)$` | True mixture / extract |
| 3 | `Tannins` | `Tannins` | `^(?:total\s+)?(?:alkaloids|flavonoids|saponins|tannins|phenolics|terpenoids|glycosides)$` | True mixture / extract |
| 4 | `Total phenolics` | `Total phenolics` | `^(?:total\s+)?(?:alkaloids|flavonoids|saponins|tannins|phenolics|terpenoids|glycosides)$` | True mixture / extract |
| 5 | `Gum` | `Gum` | `^(?:resin|gum|wax)$` | True mixture / extract |
| 6 | `Terpenoids` | `Terpenoids` | `^(?:total\s+)?(?:alkaloids|flavonoids|saponins|tannins|phenolics|terpenoids|glycosides)$` | True mixture / extract |
| 7 | `Saponins` | `Saponins` | `^(?:total\s+)?(?:alkaloids|flavonoids|saponins|tannins|phenolics|terpenoids|glycosides)$` | True mixture / extract |
| 8 | `polyunsaturated hydroxy fatty acid` | `polyunsaturated hydroxy fatty acid` | `.*\bfatty\s+acid(?:s)?\b.*` | POTENTIAL SINGLE COMPOUND (REVIEW) |

---

## 4. Encoding-Loss Skipped Names (`skipped_encoding_loss`)

Total Count: **214**

| # | Compound Name (Original) | Cleaned Query | Notes |
| :-: | :--- | :--- | :--- |
| 1 | `(3? -sulfo)Galbeta-Cer(d18:1/18:0(2OH))` | `(3? -sulfo)Galbeta-Cer(d18:1/18:0(2OH))` | Contains destroyed character (`?` or replacement) |
| 2 | `1-Nitro-.?.-d-arabinofuranose, tetraacetate` | `1-Nitro-.?.-d-arabinofuranose, tetraacetate` | Contains destroyed character (`?` or replacement) |
| 3 | `1?Norvaline, N?ethoxycarbonyl?, nonyl ester` | `1?Norvaline, N?ethoxycarbonyl?, nonyl ester` | Contains destroyed character (`?` or replacement) |
| 4 | `2,4 (1H ,3 H}?Pyrimidinedione, 6?iodo?5?methyl?` | `2,4 (1H ,3 H}?Pyrimidinedione, 6?iodo?5?methyl?` | Contains destroyed character (`?` or replacement) |
| 5 | `2?Fluoro?6?trifluora methyl benzoic acid, 4?nitraphenyl ester` | `2?Fluoro?6?trifluora methyl benzoic acid, 4?nitraphenyl ester` | Contains destroyed character (`?` or replacement) |
| 6 | `2?Pyrrolidinone (5?(cyclo hexyl methyl)?` | `2?Pyrrolidinone (5?(cyclo hexyl methyl)?` | Contains destroyed character (`?` or replacement) |
| 7 | `4?Methyl?2,4?bis (4?trimethylsilyloxyphenyl} pentene?l` | `4?Methyl?2,4?bis (4?trimethylsilyloxyphenyl} pentene?l` | Contains destroyed character (`?` or replacement) |
| 8 | `5?-androstane-3,17-dione 17monooxime` | `5?-androstane-3,17-dione 17monooxime` | Contains destroyed character (`?` or replacement) |
| 9 | `Propane, 2?methoxy?2?rnethyl?` | `Propane, 2?methoxy?2?rnethyl?` | Contains destroyed character (`?` or replacement) |
| 10 | `Silane, [{1,1?dimethy1?2?propenyl) oxy] dimethyl?` | `Silane, [{1,1?dimethy1?2?propenyl) oxy] dimethyl?` | Contains destroyed character (`?` or replacement) |
| 11 | `beta?1?Arabinopyranoside, methyl` | `beta?1?Arabinopyranoside, methyl` | Contains destroyed character (`?` or replacement) |
| 12 | `(24S)-stigmast-5-ene7?-ethoxy-3?-ol` | `(24S)-stigmast-5-ene7?-ethoxy-3?-ol` | Contains destroyed character (`?` or replacement) |
| 13 | `2,3-(S)-hexahydroxydiphenoyl-?/ ? ?? ? ?-d-glucose` | `2,3-(S)-hexahydroxydiphenoyl-?/ ? ?? ? ?-d-glucose` | Contains destroyed character (`?` or replacement) |
| 14 | `2?,3?,24-trihydroxylup-20(29)-ene-28-oic acid` | `2?,3?,24-trihydroxylup-20(29)-ene-28-oic acid` | Contains destroyed character (`?` or replacement) |
| 15 | `2?,3?,24-trihydroxyolean-18-ene-28-oic acid` | `2?,3?,24-trihydroxyolean-18-ene-28-oic acid` | Contains destroyed character (`?` or replacement) |
| 16 | `3?-hydroxy1-oxo-olean-12-en-28-oic acid` | `3?-hydroxy1-oxo-olean-12-en-28-oic acid` | Contains destroyed character (`?` or replacement) |
| 17 | `5?,6?-epoxy3?-hydroxyergosta-22-ene-7-one` | `5?,6?-epoxy3?-hydroxyergosta-22-ene-7-one` | Contains destroyed character (`?` or replacement) |
| 18 | `6?-methoxyergosta- 7,9(11),22-triene-3?,5?-diol` | `6?-methoxyergosta- 7,9(11),22-triene-3?,5?-diol` | Contains destroyed character (`?` or replacement) |
| 19 | `7?-methoxy 5?,6?-epoxyergosta-8(14),22-diene-3?-ol` | `7?-methoxy 5?,6?-epoxyergosta-8(14),22-diene-3?-ol` | Contains destroyed character (`?` or replacement) |
| 20 | `7?-methoxy-stigmast-5-ene-3?-ol` | `7?-methoxy-stigmast-5-ene-3?-ol` | Contains destroyed character (`?` or replacement) |
| 21 | `ergosta8(14),22-diene-3?,5?,6?,7?-tetraol` | `ergosta8(14),22-diene-3?,5?,6?,7?-tetraol` | Contains destroyed character (`?` or replacement) |
| 22 | `stigmast-4-ene-6?-ol-3-one` | `stigmast-4-ene-6?-ol-3-one` | Contains destroyed character (`?` or replacement) |
| 23 | `(E)-?-Farnesene` | `(E)-?-Farnesene` | Contains destroyed character (`?` or replacement) |
| 24 | `?-Bisabolene` | `?-Bisabolene` | Contains destroyed character (`?` or replacement) |
| 25 | `?-Bisabolol` | `?-Bisabolol` | Contains destroyed character (`?` or replacement) |
| 26 | `?-Elemene` | `?-Elemene` | Contains destroyed character (`?` or replacement) |
| 27 | `?-Santalene` | `?-Santalene` | Contains destroyed character (`?` or replacement) |
| 28 | `?-Thujene` | `?-Thujene` | Contains destroyed character (`?` or replacement) |
| 29 | `?-bergamotene` | `?-bergamotene` | Contains destroyed character (`?` or replacement) |
| 30 | `?-bisabolene` | `?-bisabolene` | Contains destroyed character (`?` or replacement) |
| 31 | `?-humulene` | `?-humulene` | Contains destroyed character (`?` or replacement) |
| 32 | `?-myrcene` | `?-myrcene` | Contains destroyed character (`?` or replacement) |
| 33 | `?-phellandrene` | `?-phellandrene` | Contains destroyed character (`?` or replacement) |
| 34 | `?-pinene5.278` | `?-pinene5.278` | Contains destroyed character (`?` or replacement) |
| 35 | `?-pinene6.607` | `?-pinene6.607` | Contains destroyed character (`?` or replacement) |
| 36 | `?-terpinene` | `?-terpinene` | Contains destroyed character (`?` or replacement) |
| 37 | `?-thujone` | `?-thujone` | Contains destroyed character (`?` or replacement) |
| 38 | `Cis-?-Ocimene` | `Cis-?-Ocimene` | Contains destroyed character (`?` or replacement) |
| 39 | `cis-?-Bergamotene` | `cis-?-Bergamotene` | Contains destroyed character (`?` or replacement) |
| 40 | `cis-?-Bisabolene 1` | `cis-?-Bisabolene 1` | Contains destroyed character (`?` or replacement) |
| 41 | `trans-?-Bergamotene` | `trans-?-Bergamotene` | Contains destroyed character (`?` or replacement) |
| 42 | `trans-?-Ocimene` | `trans-?-Ocimene` | Contains destroyed character (`?` or replacement) |
| 43 | `(E)- ? -Ocimene` | `(E)- ? -Ocimene` | Contains destroyed character (`?` or replacement) |
| 44 | `(E)-?-Ocimene` | `(E)-?-Ocimene` | Contains destroyed character (`?` or replacement) |
| 45 | `(Z)- ? -Ocimene` | `(Z)- ? -Ocimene` | Contains destroyed character (`?` or replacement) |
| 46 | `? -Cadinene` | `? -Cadinene` | Contains destroyed character (`?` or replacement) |
| 47 | `? -Phellandrene` | `? -Phellandrene` | Contains destroyed character (`?` or replacement) |
| 48 | `? -Terpinene` | `? -Terpinene` | Contains destroyed character (`?` or replacement) |
| 49 | `? -Terpineol` | `? -Terpineol` | Contains destroyed character (`?` or replacement) |
| 50 | `?-Bourbonene` | `?-Bourbonene` | Contains destroyed character (`?` or replacement) |
| 51 | `?-Cadinene` | `?-Cadinene` | Contains destroyed character (`?` or replacement) |
| 52 | `?-Caryophyllene` | `?-Caryophyllene` | Contains destroyed character (`?` or replacement) |
| 53 | `?-Copaene` | `?-Copaene` | Contains destroyed character (`?` or replacement) |
| 54 | `?-Cubebene` | `?-Cubebene` | Contains destroyed character (`?` or replacement) |
| 55 | `?-Duprezianene` | `?-Duprezianene` | Contains destroyed character (`?` or replacement) |
| 56 | `?-Farnesene` | `?-Farnesene` | Contains destroyed character (`?` or replacement) |
| 57 | `?-Guaiene` | `?-Guaiene` | Contains destroyed character (`?` or replacement) |
| 58 | `?-Muurolene` | `?-Muurolene` | Contains destroyed character (`?` or replacement) |
| 59 | `?-Myrcene` | `?-Myrcene` | Contains destroyed character (`?` or replacement) |
| 60 | `?-Phellandrene` | `?-Phellandrene` | Contains destroyed character (`?` or replacement) |
| 61 | `?-Pinene` | `?-Pinene` | Contains destroyed character (`?` or replacement) |
| 62 | `?-Selinene` | `?-Selinene` | Contains destroyed character (`?` or replacement) |
| 63 | `?-Terpinolene` | `?-Terpinolene` | Contains destroyed character (`?` or replacement) |
| 64 | `?-Thujaplicin` | `?-Thujaplicin` | Contains destroyed character (`?` or replacement) |
| 65 | `?-terpinen -7- al` | `?-terpinen -7- al` | Contains destroyed character (`?` or replacement) |
| 66 | `?-terpinen-7-al` | `?-terpinen-7-al` | Contains destroyed character (`?` or replacement) |
| 67 | `?-cineole` | `?-cineole` | Contains destroyed character (`?` or replacement) |
| 68 | `??glucopyranoside` | `??glucopyranoside` | Contains destroyed character (`?` or replacement) |
| 69 | `Quercetin-3?O??-rhamnopyranosyl` | `Quercetin-3?O??-rhamnopyranosyl` | Contains destroyed character (`?` or replacement) |
| 70 | `p???D-glucosycoxybenozoic acid` | `p???D-glucosycoxybenozoic acid` | Contains destroyed character (`?` or replacement) |
| 71 | `?-spinasterone` | `?-spinasterone` | Contains destroyed character (`?` or replacement) |
| 72 | `( Z)-?-Ocimene` | `( Z)-?-Ocimene` | Contains destroyed character (`?` or replacement) |
| 73 | `(Z)-?-Ocimene` | `(Z)-?-Ocimene` | Contains destroyed character (`?` or replacement) |
| 74 | `?-Humulene` | `?-Humulene` | Contains destroyed character (`?` or replacement) |
| 75 | `?-Ionone` | `?-Ionone` | Contains destroyed character (`?` or replacement) |
| 76 | `?-Terpinene` | `?-Terpinene` | Contains destroyed character (`?` or replacement) |
| 77 | `?-Terpineol` | `?-Terpineol` | Contains destroyed character (`?` or replacement) |
| 78 | `?-Terpinyl isobutyrate` | `?-Terpinyl isobutyrate` | Contains destroyed character (`?` or replacement) |
| 79 | `1,2,3,4,6-Penta-Ogalloyl-?-D-glucose` | `1,2,3,4,6-Penta-Ogalloyl-?-D-glucose` | Contains destroyed character (`?` or replacement) |
| 80 | `3' -O-Methyl-4-O-(3'',4''-di-O-galloyl-?-L-rhamnopyranosyl)ellagic acid` | `3' -O-Methyl-4-O-(3'',4''-di-O-galloyl-?-L-rhamnopyranosyl)ellagic acid` | Contains destroyed character (`?` or replacement) |
| 81 | `3'-O-Methyl-4-0-(n"-O-galloyl-?-D-xylopyranosyl)ellagic acid (n=2, 3, or 4)` | `3'-O-Methyl-4-0-(n"-O-galloyl-?-D-xylopyranosyl)ellagic acid (n=2, 3, or 4)` | Contains destroyed character (`?` or replacement) |
| 82 | `3,4,6-tri-O-galloyl-?-d-Glc` | `3,4,6-tri-O-galloyl-?-d-Glc` | Contains destroyed character (`?` or replacement) |
| 83 | `4-O-(3'',4''-Di-O-galloyl-?-L-rhamnopyranosyl)ellagic acid` | `4-O-(3'',4''-Di-O-galloyl-?-L-rhamnopyranosyl)ellagic acid` | Contains destroyed character (`?` or replacement) |
| 84 | `4-O-(4''-O-Galloyl- ?-L-rhamnopyranosyl)ellagic acid` | `4-O-(4''-O-Galloyl- ?-L-rhamnopyranosyl)ellagic acid` | Contains destroyed character (`?` or replacement) |
| 85 | `?,4-Dimethyl-3-cyclohexene-1-aldehyde` | `?,4-Dimethyl-3-cyclohexene-1-aldehyde` | Contains destroyed character (`?` or replacement) |
| 86 | `?-Butyrolactone` | `?-Butyrolactone` | Contains destroyed character (`?` or replacement) |
| 87 | `?-Damascenone` | `?-Damascenone` | Contains destroyed character (`?` or replacement) |
| 88 | `?-sitosterol` | `?-sitosterol` | Contains destroyed character (`?` or replacement) |
| 89 | `?-Aminobutyric acid (GABA)` | `?-Aminobutyric acid (GABA)` | Contains destroyed character (`?` or replacement) |
| 90 | `?-cadinol` | `?-cadinol` | Contains destroyed character (`?` or replacement) |
| 91 | `?-farnesene` | `?-farnesene` | Contains destroyed character (`?` or replacement) |
| 92 | `?-terpinenol` | `?-terpinenol` | Contains destroyed character (`?` or replacement) |
| 93 | `Cis-?-Terpineol` | `Cis-?-Terpineol` | Contains destroyed character (`?` or replacement) |
| 94 | `??digentibioside` | `??digentibioside` | Contains destroyed character (`?` or replacement) |
| 95 | `2?, 3?, 19?, 23-tetrahydroxyurs-12-en-28-oic acid` | `2?, 3?, 19?, 23-tetrahydroxyurs-12-en-28-oic acid` | Contains destroyed character (`?` or replacement) |
| 96 | `?-sitosterol glucoside` | `?-sitosterol glucoside` | Contains destroyed character (`?` or replacement) |
| 97 | `3?, 6?, 19?, 23-tetrahydroxyurs-12-en-28-oic acid` | `3?, 6?, 19?, 23-tetrahydroxyurs-12-en-28-oic acid` | Contains destroyed character (`?` or replacement) |
| 98 | `?-,?-amyrin` | `?-,?-amyrin` | Contains destroyed character (`?` or replacement) |
| 99 | `?-spinosterol` | `?-spinosterol` | Contains destroyed character (`?` or replacement) |
| 100 | `myricetin 3-O-rahmnopyranoside (1 ? 6) glucopyranoside` | `myricetin 3-O-rahmnopyranoside (1 ? 6) glucopyranoside` | Contains destroyed character (`?` or replacement) |
| 101 | `spinasterol ?-D glucopyranoside` | `spinasterol ?-D glucopyranoside` | Contains destroyed character (`?` or replacement) |
| 102 | `(E)-iso-?-Bisabolene` | `(E)-iso-?-Bisabolene` | Contains destroyed character (`?` or replacement) |
| 103 | `(Z)-?-Farnesene` | `(Z)-?-Farnesene` | Contains destroyed character (`?` or replacement) |
| 104 | `1-(?-D-Ribofuranosyl)-1,4-dihydronicotinamide` | `1-(?-D-Ribofuranosyl)-1,4-dihydronicotinamide` | Contains destroyed character (`?` or replacement) |
| 105 | `10-epi-?-Eudesmol` | `10-epi-?-Eudesmol` | Contains destroyed character (`?` or replacement) |
| 106 | `14-Hydroxy-?-cadinene` | `14-Hydroxy-?-cadinene` | Contains destroyed character (`?` or replacement) |
| 107 | `14-Hydroxy-?-muurolene` | `14-Hydroxy-?-muurolene` | Contains destroyed character (`?` or replacement) |
| 108 | `3,6-Dimethoxyestra-1,3,5(10),6,8-pentaene-17?-carboxylic acid methyl ester` | `3,6-Dimethoxyestra-1,3,5(10),6,8-pentaene-17?-carboxylic acid methyl ester` | Contains destroyed character (`?` or replacement) |
| 109 | `?-Amorphene` | `?-Amorphene` | Contains destroyed character (`?` or replacement) |
| 110 | `?-Bergamotene` | `?-Bergamotene` | Contains destroyed character (`?` or replacement) |
| 111 | `?-Cadinol` | `?-Cadinol` | Contains destroyed character (`?` or replacement) |
| 112 | `?-Linalool` | `?-Linalool` | Contains destroyed character (`?` or replacement) |
| 113 | `?-Sitosterol` | `?-Sitosterol` | Contains destroyed character (`?` or replacement) |
| 114 | `?-Tocopherol(Vitamin E)` | `?-Tocopherol(Vitamin E)` | Contains destroyed character (`?` or replacement) |
| 115 | `?-Ylangene` | `?-Ylangene` | Contains destroyed character (`?` or replacement) |
| 116 | `Isorhamnetin 3-O-[?-D-glucopyranosyl-(1?2)-?-L-rhamnopyranoside]` | `Isorhamnetin 3-O-[?-D-glucopyranosyl-(1?2)-?-L-rhamnopyranoside]` | Contains destroyed character (`?` or replacement) |
| 117 | `?-caryophyllene alcohol` | `?-caryophyllene alcohol` | Contains destroyed character (`?` or replacement) |
| 118 | `(+)-pinoresinol-di-O-?-D-glucopyranoside` | `(+)-pinoresinol-di-O-?-D-glucopyranoside` | Contains destroyed character (`?` or replacement) |
| 119 | `(+)-syringaresinol-O-?-D-glucopyranoside` | `(+)-syringaresinol-O-?-D-glucopyranoside` | Contains destroyed character (`?` or replacement) |
| 120 | `(20 S)-3?,30-dihydroxylupane` | `(20 S)-3?,30-dihydroxylupane` | Contains destroyed character (`?` or replacement) |
| 121 | `1,2,4-trihydroxynaphthalene-1-O-?-D-glucopyranoside` | `1,2,4-trihydroxynaphthalene-1-O-?-D-glucopyranoside` | Contains destroyed character (`?` or replacement) |
| 122 | `2,4,6-trihydroxyacetophenone-2-O-?-D-glucopyranoside` | `2,4,6-trihydroxyacetophenone-2-O-?-D-glucopyranoside` | Contains destroyed character (`?` or replacement) |
| 123 | `30-norlupan-3?-ol-20-one` | `30-norlupan-3?-ol-20-one` | Contains destroyed character (`?` or replacement) |
| 124 | `3?,4?-dihydroxy-?-tetralone` | `3?,4?-dihydroxy-?-tetralone` | Contains destroyed character (`?` or replacement) |
| 125 | `4S-4-hydroxy-?-tetralone` | `4S-4-hydroxy-?-tetralone` | Contains destroyed character (`?` or replacement) |
| 126 | `?-Isomethyl ionone` | `?-Isomethyl ionone` | Contains destroyed character (`?` or replacement) |
| 127 | `Apigenin-4'-O-?-D-glucopyranoside` | `Apigenin-4'-O-?-D-glucopyranoside` | Contains destroyed character (`?` or replacement) |
| 128 | `Lawnermis acid (3?,28?-dihydroxy-ursa-12,20-dien-23?-oic acid)` | `Lawnermis acid (3?,28?-dihydroxy-ursa-12,20-dien-23?-oic acid)` | Contains destroyed character (`?` or replacement) |
| 129 | `Lawsochrysinin (5-hydroxy-7-(4?-pentenyloxy-flavone)` | `Lawsochrysinin (5-hydroxy-7-(4?-pentenyloxy-flavone)` | Contains destroyed character (`?` or replacement) |
| 130 | `Lawsonaringenin (4',5-dihydroxy-7-(4?-pentenyloxy)-flavanone)` | `Lawsonaringenin (4',5-dihydroxy-7-(4?-pentenyloxy)-flavanone)` | Contains destroyed character (`?` or replacement) |
| 131 | `Lawsoniaside A (1-butanoyl-3,5-dimethylphloroglucinyl-6-O-?-D-glucopyronoside)` | `Lawsoniaside A (1-butanoyl-3,5-dimethylphloroglucinyl-6-O-?-D-glucopyronoside)` | Contains destroyed character (`?` or replacement) |
| 132 | `Lawsoniaside B (3-(4-O-?-D-glucopyranosyl-3,5-dimethoxy)phenyl-2E-propenol)` | `Lawsoniaside B (3-(4-O-?-D-glucopyranosyl-3,5-dimethoxy)phenyl-2E-propenol)` | Contains destroyed character (`?` or replacement) |
| 133 | `Lawsonic acid (3?-E-ferulyloxy-lup-20(29)-en-28-oic acid)` | `Lawsonic acid (3?-E-ferulyloxy-lup-20(29)-en-28-oic acid)` | Contains destroyed character (`?` or replacement) |
| 134 | `Luteolin-4'-O-?-D-glucopyranoside` | `Luteolin-4'-O-?-D-glucopyranoside` | Contains destroyed character (`?` or replacement) |
| 135 | `Syringaresinol-di-O-?-D-glucopyranoside` | `Syringaresinol-di-O-?-D-glucopyranoside` | Contains destroyed character (`?` or replacement) |
| 136 | `Syringinosinol di-?-D-glucopyranoside` | `Syringinosinol di-?-D-glucopyranoside` | Contains destroyed character (`?` or replacement) |
| 137 | `p,?-Dimethylstyrene` | `p,?-Dimethylstyrene` | Contains destroyed character (`?` or replacement) |
| 138 | `epi-?-Bisabolol` | `epi-?-Bisabolol` | Contains destroyed character (`?` or replacement) |
| 139 | `Scutellarein-6-O-?-L-rhamnopyranoside-8-C-?-D-glucopyra noside` | `Scutellarein-6-O-?-L-rhamnopyranoside-8-C-?-D-glucopyra noside` | Contains destroyed character (`?` or replacement) |
| 140 | `kaempferol-7-O-[6-O-p-hydroxybenzoyl-?-D-glucosyl-(1-6)-? D-glucopyranoside]` | `kaempferol-7-O-[6-O-p-hydroxybenzoyl-?-D-glucosyl-(1-6)-? D-glucopyranoside]` | Contains destroyed character (`?` or replacement) |
| 141 | `3-O-L-rhamnopyranosyl(1?2)-?-D-glucopyranosylkaempferol (kaempferol 3-O-?-neohesperidoside or Kaempferol-3-O-?-D-glucorhamnoside)` | `3-O-L-rhamnopyranosyl(1?2)-?-D-glucopyranosylkaempferol (kaempferol 3-O-?-neohesperidoside or Kaempferol-3-O-?-D-glucorhamnoside)` | Contains destroyed character (`?` or replacement) |
| 142 | `Pelargonidin 3-O-(6?'-malonyl-glucoside)` | `Pelargonidin 3-O-(6?'-malonyl-glucoside)` | Contains destroyed character (`?` or replacement) |
| 143 | `oxo-?-ylangene` | `oxo-?-ylangene` | Contains destroyed character (`?` or replacement) |
| 144 | `6-Hydroxymusizin 6-O-?-D-glucopyranoside` | `6-Hydroxymusizin 6-O-?-D-glucopyranoside` | Contains destroyed character (`?` or replacement) |
| 145 | `7-Hydroxyflavanone 7-?-D-glucopyranoside` | `7-Hydroxyflavanone 7-?-D-glucopyranoside` | Contains destroyed character (`?` or replacement) |
| 146 | `(?)-nortrachelogenin` | `(?)-nortrachelogenin` | Contains destroyed character (`?` or replacement) |
| 147 | `24-Ethylcholesta-5,22-dien-3?-ol` | `24-Ethylcholesta-5,22-dien-3?-ol` | Contains destroyed character (`?` or replacement) |
| 148 | `4/-O-?-L-rhamnopyranosyl-(1?6)-?-d glucopyranoside` | `4/-O-?-L-rhamnopyranosyl-(1?6)-?-d glucopyranoside` | Contains destroyed character (`?` or replacement) |
| 149 | `?- Amyrone` | `?- Amyrone` | Contains destroyed character (`?` or replacement) |
| 150 | `?-lactone` | `?-lactone` | Contains destroyed character (`?` or replacement) |
| 151 | `Kaempferol 7-O-?-d-glucopyranoside` | `Kaempferol 7-O-?-d-glucopyranoside` | Contains destroyed character (`?` or replacement) |
| 152 | `Quercetin-4?-O-?-D glucopyranoside` | `Quercetin-4?-O-?-D glucopyranoside` | Contains destroyed character (`?` or replacement) |
| 153 | `?-toxicarol` | `?-toxicarol` | Contains destroyed character (`?` or replacement) |
| 154 | `(Z)-epi-?-Santalol` | `(Z)-epi-?-Santalol` | Contains destroyed character (`?` or replacement) |
| 155 | `(Z)-epi-?-Santalol acetate` | `(Z)-epi-?-Santalol acetate` | Contains destroyed character (`?` or replacement) |
| 156 | `14-hydroxy-?-Cadinene` | `14-hydroxy-?-Cadinene` | Contains destroyed character (`?` or replacement) |
| 157 | `14-hydroxy-?-Muurolene` | `14-hydroxy-?-Muurolene` | Contains destroyed character (`?` or replacement) |
| 158 | `7-epi-?-Eudesmol` | `7-epi-?-Eudesmol` | Contains destroyed character (`?` or replacement) |
| 159 | `?- guariene` | `?- guariene` | Contains destroyed character (`?` or replacement) |
| 160 | `?-(Z)-Curcumen-12-ol` | `?-(Z)-Curcumen-12-ol` | Contains destroyed character (`?` or replacement) |
| 161 | `?-2-Carene` | `?-2-Carene` | Contains destroyed character (`?` or replacement) |
| 162 | `?-Eudesmol acetate` | `?-Eudesmol acetate` | Contains destroyed character (`?` or replacement) |
| 163 | `1H-Cycloprop[e]azulen-4-ol,decahydro-1,1,4,7-tetramethyl-, [1aR-(1a?,4?,4a?,7?,7a?,7b?)]-` | `1H-Cycloprop[e]azulen-4-ol,decahydro-1,1,4,7-tetramethyl-, [1aR-(1a?,4?,4a?,7?,7a?,7b?)]-` | Contains destroyed character (`?` or replacement) |
| 164 | `1H-Cycloprop[e]azulene,1a,2,3,5,6,7,7a,7b-octahydro-1,1,4,7-tetramethyl-, [1aR-(1a?,7?,7a?,7b?)]-` | `1H-Cycloprop[e]azulene,1a,2,3,5,6,7,7a,7b-octahydro-1,1,4,7-tetramethyl-, [1aR-(1a?,7?,7a?,7b?)]-` | Contains destroyed character (`?` or replacement) |
| 165 | `5-Azulenemethanol, 1,2,3,3a,4,5,6,7-octahydro-?,?,3,8-tetramethyl-, [3S-(3?,3a?,5?)]-` | `5-Azulenemethanol, 1,2,3,3a,4,5,6,7-octahydro-?,?,3,8-tetramethyl-, [3S-(3?,3a?,5?)]-` | Contains destroyed character (`?` or replacement) |
| 166 | `5-[(6?,7?-Dihydroxy-3?,7?-dimethyl-2-octenyl)oxy] psoralen` | `5-[(6?,7?-Dihydroxy-3?,7?-dimethyl-2-octenyl)oxy] psoralen` | Contains destroyed character (`?` or replacement) |
| 167 | `5-[(7?,8?-Dihydroxy-3?,8?-dimethyl-2-nonadienyl)oxy] psoralen` | `5-[(7?,8?-Dihydroxy-3?,8?-dimethyl-2-nonadienyl)oxy] psoralen` | Contains destroyed character (`?` or replacement) |
| 168 | `E-?-Ocimene` | `E-?-Ocimene` | Contains destroyed character (`?` or replacement) |
| 169 | `(?)-?-atlantone` | `(?)-?-atlantone` | Contains destroyed character (`?` or replacement) |
| 170 | `(?)-?-bisabolene` | `(?)-?-bisabolene` | Contains destroyed character (`?` or replacement) |
| 171 | `16?-hydro-19-al-ent-kauran-17-oic acid` | `16?-hydro-19-al-ent-kauran-17-oic acid` | Contains destroyed character (`?` or replacement) |
| 172 | `6?-hydroxystigmast-4-en-3-one` | `6?-hydroxystigmast-4-en-3-one` | Contains destroyed character (`?` or replacement) |
| 173 | `?-cadinene` | `?-cadinene` | Contains destroyed character (`?` or replacement) |
| 174 | `?-caryophyllene` | `?-caryophyllene` | Contains destroyed character (`?` or replacement) |
| 175 | `?-cedrene` | `?-cedrene` | Contains destroyed character (`?` or replacement) |
| 176 | `?-elemene` | `?-elemene` | Contains destroyed character (`?` or replacement) |
| 177 | `?-pinene` | `?-pinene` | Contains destroyed character (`?` or replacement) |
| 178 | `?-sesquiphellandrene` | `?-sesquiphellandrene` | Contains destroyed character (`?` or replacement) |
| 179 | `?-terpineol` | `?-terpineol` | Contains destroyed character (`?` or replacement) |
| 180 | `(E)-?-Farnesene(7,11-dimethyl-3-methylene-1,6,10-dodecatriene)` | `(E)-?-Farnesene(7,11-dimethyl-3-methylene-1,6,10-dodecatriene)` | Contains destroyed character (`?` or replacement) |
| 181 | `3-oxo-9-O-?-d-glucosyloxy-4,6E-megastigmadien` | `3-oxo-9-O-?-d-glucosyloxy-4,6E-megastigmadien` | Contains destroyed character (`?` or replacement) |
| 182 | `3-oxo-?-ionol 9-O-?-d-glucoside` | `3-oxo-?-ionol 9-O-?-d-glucoside` | Contains destroyed character (`?` or replacement) |
| 183 | `4-oxo-?-ionol 9-O-?-d-glucoside` | `4-oxo-?-ionol 9-O-?-d-glucoside` | Contains destroyed character (`?` or replacement) |
| 184 | `9E-abscisic alcohol ?-d-glucoside` | `9E-abscisic alcohol ?-d-glucoside` | Contains destroyed character (`?` or replacement) |
| 185 | `9E-abscisyl ?-d-glucoside` | `9E-abscisyl ?-d-glucoside` | Contains destroyed character (`?` or replacement) |
| 186 | `?-Bisabolene ((S)-1-Methyl-4-(6-methylhepta-1,5-diene-2-yl) cyclohexa-1-ene)` | `?-Bisabolene ((S)-1-Methyl-4-(6-methylhepta-1,5-diene-2-yl) cyclohexa-1-ene)` | Contains destroyed character (`?` or replacement) |
| 187 | `?-Caryophyllene ([1R-(1R,4Z,9S)]-4,11,11 -trimethyl-8-methylene-Bicyclo [7.2.0] undec-4-ene)` | `?-Caryophyllene ([1R-(1R,4Z,9S)]-4,11,11 -trimethyl-8-methylene-Bicyclo [7.2.0] undec-4-ene)` | Contains destroyed character (`?` or replacement) |
| 188 | `?-Curcumenene ((R)-1-Methyl-4-(6-methylhept-5-en-2-yl) cyclohexa-1,4-diene)` | `?-Curcumenene ((R)-1-Methyl-4-(6-methylhept-5-en-2-yl) cyclohexa-1,4-diene)` | Contains destroyed character (`?` or replacement) |
| 189 | `?-Dodecalatone` | `?-Dodecalatone` | Contains destroyed character (`?` or replacement) |
| 190 | `?-Ocimene(3,7-dimethyl-1,3,7-Octatriene)` | `?-Ocimene(3,7-dimethyl-1,3,7-Octatriene)` | Contains destroyed character (`?` or replacement) |
| 191 | `?-Sesquiphellandrene ([S-(R*,S*)]-3-(1,5-dimethyl-4-enyl)-6-methylene-cyclohexene)` | `?-Sesquiphellandrene ([S-(R*,S*)]-3-(1,5-dimethyl-4-enyl)-6-methylene-cyclohexene)` | Contains destroyed character (`?` or replacement) |
| 192 | `?-Tocopherol, O-TMS` | `?-Tocopherol, O-TMS` | Contains destroyed character (`?` or replacement) |
| 193 | `Arabinonic acid, 3TMS ?-lactone` | `Arabinonic acid, 3TMS ?-lactone` | Contains destroyed character (`?` or replacement) |
| 194 | `Erythronic acid ?-lactone, 2 TMS-ether` | `Erythronic acid ?-lactone, 2 TMS-ether` | Contains destroyed character (`?` or replacement) |
| 195 | `O-?-Galactopyranosyl-d-mannopyranose 8TMS` | `O-?-Galactopyranosyl-d-mannopyranose 8TMS` | Contains destroyed character (`?` or replacement) |
| 196 | `Pentonic acid, 5-deoxy-3 TMS, ?-lactone` | `Pentonic acid, 5-deoxy-3 TMS, ?-lactone` | Contains destroyed character (`?` or replacement) |
| 197 | `Thymol-?-glucopyranoside-O-TMS` | `Thymol-?-glucopyranoside-O-TMS` | Contains destroyed character (`?` or replacement) |
| 198 | `Trans-?-Bergamotene(2,6-dimethyl-6-(4-methyl-3-pentenyl)-Bicyclo [3.1.1]hept-2-ene)` | `Trans-?-Bergamotene(2,6-dimethyl-6-(4-methyl-3-pentenyl)-Bicyclo [3.1.1]hept-2-ene)` | Contains destroyed character (`?` or replacement) |
| 199 | `abscisyl ?-d-glucoside` | `abscisyl ?-d-glucoside` | Contains destroyed character (`?` or replacement) |
| 200 | `trans-?-Bisabolene (Cyclohexene, 4-[(1E)-1,5-dimethyl-1,4-hexadien-1-yl]-1-methyl-)` | `trans-?-Bisabolene (Cyclohexene, 4-[(1E)-1,5-dimethyl-1,4-hexadien-1-yl]-1-methyl-)` | Contains destroyed character (`?` or replacement) |
| 201 | `(?) epicatech` | `(?) epicatech` | Contains destroyed character (`?` or replacement) |
| 202 | `7,4?-dihydroxy-3,11-dehydrohomoisoflavanone` | `7,4?-dihydroxy-3,11-dehydrohomoisoflavanone` | Contains destroyed character (`?` or replacement) |
| 203 | `7-hydroxy-4?-methoxy-3,11-dehydrohomoisoflavanone` | `7-hydroxy-4?-methoxy-3,11-dehydrohomoisoflavanone` | Contains destroyed character (`?` or replacement) |
| 204 | `Kaempferol-3-O-?-Lrhamnopyranosyl-(1?2)-b-D-xylopyranoside` | `Kaempferol-3-O-?-Lrhamnopyranosyl-(1?2)-b-D-xylopyranoside` | Contains destroyed character (`?` or replacement) |
| 205 | `(?)- delta7-trans-(1R, 3R, 6R)-isotetrahydrocannabinol-C5 (` | `(?)- delta7-trans-(1R, 3R, 6R)-isotetrahydrocannabinol-C5 (` | Contains destroyed character (`?` or replacement) |
| 206 | `(?)-delta 7-trans-(1R, 3R, 6R)-isotetrahydrocannabivarin-C3 (` | `(?)-delta 7-trans-(1R, 3R, 6R)-isotetrahydrocannabivarin-C3 (` | Contains destroyed character (`?` or replacement) |
| 207 | `?-Limonene` | `?-Limonene` | Contains destroyed character (`?` or replacement) |
| 208 | `?9-tetrahydrocannabinol` | `?9-tetrahydrocannabinol` | Contains destroyed character (`?` or replacement) |
| 209 | `2,2?-methylenebis[6(1,1-dimethylethyl)4-ethyl-]phenol` | `2,2?-methylenebis[6(1,1-dimethylethyl)4-ethyl-]phenol` | Contains destroyed character (`?` or replacement) |
| 210 | `Ergosta-5,22-dien-3-ol acetate (3beta, 22?)` | `Ergosta-5,22-dien-3-ol acetate (3beta, 22?)` | Contains destroyed character (`?` or replacement) |
| 211 | `3 ?-D-Glucopyranoside, O-?-D-glucopyranosyl-(1.fwdarw.3)-ß-d-fru` | `3 ?-D-Glucopyranoside, O-?-D-glucopyranosyl-(1.fwdarw.3)-ß-d-fru` | Contains destroyed character (`?` or replacement) |
| 212 | `3-O-?- D-glucopyranoside` | `3-O-?- D-glucopyranoside` | Contains destroyed character (`?` or replacement) |
| 213 | `3-O-?- L -rhamnopyranoside` | `3-O-?- L -rhamnopyranoside` | Contains destroyed character (`?` or replacement) |
| 214 | `4-O-?- L -2-acetylrhamnopyranoside` | `4-O-?- L -2-acetylrhamnopyranoside` | Contains destroyed character (`?` or replacement) |

---

## 5. Multiple-Matches Analysis (`multiple_matches`)

- **Total Multiple-Match Names**: **81**
- **Names where ALL candidates share the SAME 14-char InChIKey connectivity layer**: **79** (97.5%)
- **Interpretation**: 79 of the 81 multiple-match names represent stereoisomers or salt variants of the exact same 2D molecular graph.

---

## 6. No-Match Structural Breakdown (`no_match`)

Total Unresolved Names: **970**

| Category Pattern | Count | % of No-Match | Example Pattern |
| :--- | :---: | :---: | :--- |
| **Parenthetical or bracketed synonym** | **123** | 12.7% | `Compound Name (Synonym)` or `Name[Synonym]` |
| **CAS-style inverted name** | **125** | 12.9% | `Silane, cyclohexyl dimethoxy methyl` |
| **Parenthesized stereo descriptor prefix** | **61** | 6.3% | `(1R,2S)-...` or `(+)-...` |
| **Class or plural names** | **40** | 4.1% | `Flavonones`, `...derivatives` |
| **Other / Misspelling / Obscure** | **621** | 64.0% | `Andrachcine` (misspelling), obscure metabolites |

---

## 7. Distinct Resolved Structures & Plant Co-Occurrence

- **Distinct Standard InChIKeys**: **8,130**
- **Distinct Flat Connectivity Layers (First 14 chars)**: **7,332**
- **Compounds found in ONLY 1 plant**: **5,618** (69.1%)
- **Compounds found in 2 OR MORE plants**: **2,512** (30.9%)

---

## 8. Provenance & Artifact Checklist

- Resolved dataset: [`data/processed/compounds/compound_structures_resolved.csv`](file:///f:/bmppd-thesis/data/processed/compounds/compound_structures_resolved.csv)
- Multiple-match review table: [`data/processed/compounds/name_multiple_matches_review.csv`](file:///f:/bmppd-thesis/data/processed/compounds/name_multiple_matches_review.csv)
- Attrition ledger: [`data/attrition/compound_resolution_attrition.csv`](file:///f:/bmppd-thesis/data/attrition/compound_resolution_attrition.csv)
- Execution log: [`data/quality/compound_resolution.log`](file:///f:/bmppd-thesis/data/quality/compound_resolution.log)
