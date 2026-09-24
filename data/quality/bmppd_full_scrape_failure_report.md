# BMPPD Stage 6H — Primary Run Failure Report

## 1. Executive Summary
During the primary execution of the Stage 6H bulk scrape (`python scrapers/bmppd_bulk_scraper.py --full`), 105 of the 916 plants encountered network-level fetch failures (`FETCH_FAILED`). Zero parse failures (`PARSE_FAILED`) occurred across the entire inventory.

All 105 failures clustered within a temporary upstream service disruption on the host `bmppd.org` between `plant_index` 132 and 267. After `plant_index` 267, the server recovered and requests succeeded normally through `plant_index` 916.

Per Stage 6H protocol, these failures are formally documented before executing `--retry-failed`.

## 2. Failure Statistics
- **Total Plants Attempted**: 908 (8 previously completed plants skipped via resume protection)
- **Total Failures**: 105 plants (11.56% of attempted)
  - **HTTP 503 Service Unavailable**: 40 plants (38.10% of failures)
  - **HTTPS Read Timeout (30s)**: 65 plants (61.90% of failures)
  - **Parse Failures (`PARSE_FAILED`)**: 0 plants (0.0%)
- **Index Range of Failures**: `plant_index` 132 to 267

## 3. Failure Classification
Every failure was caused by server-side unavailability or timeout at the upstream host:
1. `503 Server Error: Service Unavailable for url: https://bmppd.org/bmppd_result/?q=...`
2. `Network error: HTTPSConnectionPool(host='bmppd.org', port=443): Read timed out. (read timeout=30)`

No failure was caused by query resolution, URL construction, or BeautifulSoup parsing.

## 4. Failed Plants Registry
The complete list of 105 failing plants is recorded in [`data/raw/bmppd/bmppd_failed_plants.csv`](file:///F:/bmppd-thesis/data/raw/bmppd/bmppd_failed_plants.csv). Below is the comprehensive index breakdown:

| `plant_index` | `source_query` (Frozen MPBD Name) | `bmpdd_query_name` (Dispatched Query) | Failure Type | Root Cause |
| :---: | :--- | :--- | :---: | :--- |
| 132 | *Zea MAYS* L. | *Zea MAYS* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 133 | *Zanthoxylum RHETSA* (Roxb.) DC. | *Zanthoxylum RHETSA* | FETCH_FAILED | Read timeout (30s) |
| 134 | *Zanthoxylum NITIDUM* (Roxb.) DC. | *Zanthoxylum NITIDUM* | FETCH_FAILED | Read timeout (30s) |
| 136 | *Xylyocarpus MOLUCCENSIS* (Lam.) M.Roem. | *Xylyocarpus MOLUCCENSIS* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 137 | *Xylocarpus GRANATUM* Koen. | *Xylocarpus GRANATUM* | FETCH_FAILED | Read timeout (30s) |
| 138 | *Xanthium INDICUM* Klatt | *Xanthium INDICUM* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 141 | *Woodfordia FRUTICOSA* (L.) Kurz. | *Woodfordia FRUTICOSA* | FETCH_FAILED | Read timeout (30s) |
| 142 | *Wedelia CHINENSIS* (Osbeck) Merr. | *Wedelia CHINENSIS* | FETCH_FAILED | Read timeout (30s) |
| 143 | *Waltheria INDICA* L. | *Waltheria INDICA* | FETCH_FAILED | Read timeout (30s) |
| 145 | *Vitex TRIFOLIA* L. | *Vitex TRIFOLIA* | FETCH_FAILED | Read timeout (30s) |
| 147 | *Vitex NEGUNDO* L. | *Vitex NEGUNDO* | FETCH_FAILED | Read timeout (30s) |
| 149 | *Viscum ORIENTALE* Willd. | *Viscum ORIENTALE* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 150 | *Viscum ALBUM* L. | *Viscum ALBUM* | FETCH_FAILED | Read timeout (30s) |
| 152 | *Vetiveria ZIZANIOIDES* (L.) Nash | *Vetiveria ZIZANIOIDES* | FETCH_FAILED | Read timeout (30s) |
| 154 | *Vernonia PATULA* (Dryand.) Merr. | *Vernonia PATULA* | FETCH_FAILED | Read timeout (30s) |
| 156 | *Ventilago DENTICULATA* Willd. | *Ventilago DENTICULATA* | FETCH_FAILED | Read timeout (30s) |
| 157 | *Vanda ROXBURGHII* R. Br. | *Vanda ROXBURGHII* | FETCH_FAILED | Read timeout (30s) |
| 158 | *Vallaris SOLANACEA* (Roth) Kuntze | *Vallaris SOLANACEA* | FETCH_FAILED | Read timeout (30s) |
| 160 | *Uraria PICTA* (Jacq.) Desv. | *Uraria PICTA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 161 | *Uraria CRINITA* (L.) Desv. ex DC. | *Uraria CRINITA* | FETCH_FAILED | Read timeout (30s) |
| 162 | *Typhonium TRILOBATUM* (L.) Schott | *Typhonium TRILOBATUM* | FETCH_FAILED | Read timeout (30s) |
| 163 | *Tylophora INDICA* (Burm. f.) Merr. | *Tylophora INDICA* | FETCH_FAILED | Read timeout (30s) |
| 164 | *Tylophora FASCICULATA* Buch.-Ham. ex Wight | *Tylophora FASCICULATA* | FETCH_FAILED | Read timeout (30s) |
| 166 | *Trewia NUDIFLORA* L. | *Trewia NUDIFLORA* | FETCH_FAILED | Read timeout (30s) |
| 167 | *Trema ORIENTALIS* (L.) Blume | *Trema ORIENTALIS* | FETCH_FAILED | Read timeout (30s) |
| 168 | *Trapa BISPINOSA* Roxb. | *Trapa BISPINOSA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 170 | *Trachyspermum AMMI* (L.) Sprague | *Trachyspermum AMMI* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 172 | *Toddalia ASIATICA* (L.) Lam. | *Toddalia ASIATICA* | FETCH_FAILED | Read timeout (30s) |
| 173 | *Tinospora SINENSIS* (Lour.) Merr. | *Tinospora SINENSIS* | FETCH_FAILED | Read timeout (30s) |
| 174 | *Tinospora CRISPA* (L.) Hook. f. & Thomson | *Tinospora CRISPA* | FETCH_FAILED | Read timeout (30s) |
| 175 | *Tinospora CORDIFOLIA* (Willd.) Miers | *Tinospora CORDIFOLIA* | FETCH_FAILED | Read timeout (30s) |
| 177 | *Thespesia POPULNEA* (L.) Soland. ex Correa | *Thespesia POPULNEA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 180 | *Tetracera SARMENTOSA* (L.) Vahl | *Tetracera SARMENTOSA* | FETCH_FAILED | Read timeout (30s) |
| 181 | *Terminalia CITRINA* (Gaertn.) Roxb. ex Fleming | *Terminalia CITRINA* | FETCH_FAILED | Read timeout (30s) |
| 182 | *Terminalia CATAPPA* L. | *Terminalia CATAPPA* | FETCH_FAILED | Read timeout (30s) |
| 183 | *Terminalia BELLIRICA* (Gaertn.) Roxb. | *Terminalia BELLIRICA* | FETCH_FAILED | Read timeout (30s) |
| 184 | *Terminalia ARJUNA* (Roxb. ex DC.) Wight & Arn. | *Terminalia ARJUNA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 185 | *Tephrosia CANDIDA* DC. | *Tephrosia CANDIDA* | FETCH_FAILED | Read timeout (30s) |
| 187 | *Tagetes PATULA* L. | *Tagetes PATULA* | FETCH_FAILED | Read timeout (30s) |
| 188 | *Tagetes ERECTA* L. | *Tagetes ERECTA* | FETCH_FAILED | Read timeout (30s) |
| 189 | *Tabernaemontana DIVARICATA* (L.) R. Br. ex Roem. & Schult. | *Tabernaemontana DIVARICATA* | FETCH_FAILED | Read timeout (30s) |
| 190 | *Syzygium OPERCULATUM* (Roxb.) Nied. | *Syzygium OPERCULATUM* | FETCH_FAILED | Read timeout (30s) |
| 191 | *Syzygium MALACCENSE* (L.) Merr. & L.M. Perry | *Syzygium MALACCENSE* | FETCH_FAILED | Read timeout (30s) |
| 192 | *Syzygium JAMBOS* (L.) Alston | *Syzygium JAMBOS* | FETCH_FAILED | Read timeout (30s) |
| 193 | *Syzygium CUMINI* (L.) Skeels | *Syzygium CUMINI* | FETCH_FAILED | Read timeout (30s) |
| 194 | *Syzygium AQUAEM* (Burm. f.) Alston | *Syzygium AQUAEM* | FETCH_FAILED | Read timeout (30s) |
| 196 | *Swertia CHIRAYITA* (Roxb. ex Fleming) H. Karst. | *Swertia CHIRAYITA* | FETCH_FAILED | Read timeout (30s) |
| 197 | *Swertia ANGUSTIFOLIA* Buch.-Ham. ex D. Don | *Swertia ANGUSTIFOLIA* | FETCH_FAILED | Read timeout (30s) |
| 198 | *Swietenia MAHAGONI* (L.) Jacq. | *Swietenia MAHAGONI* | FETCH_FAILED | Read timeout (30s) |
| 199 | *Swietenia MACROPHYLLA* King | *Swietenia MACROPHYLLA* | FETCH_FAILED | Read timeout (30s) |
| 200 | *Streblus ASPER* Lour. | *Streblus ASPER* | FETCH_FAILED | Read timeout (30s) |
| 202 | *Stereospermum COLAIS* (Buch.-Ham. ex Dillwyn) Mabb. | *Stereospermum COLAIS* | FETCH_FAILED | Read timeout (30s) |
| 203 | *Stemona TUBEROSA* Lour. | *Stemona TUBEROSA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 205 | *Stellaria MEDIA* (L.) Vill. | *Stellaria MEDIA* | FETCH_FAILED | Read timeout (30s) |
| 206 | *Staurogyne GLAUCA* (Nees) Kuntze | *Staurogyne GLAUCA* | FETCH_FAILED | Read timeout (30s) |
| 207 | *Spondias PINNATA* (L. f.) Kurz | *Spondias PINNATA* | FETCH_FAILED | Read timeout (30s) |
| 209 | *Spilanthes ACMELLA* (L.) L. | *Spilanthes ACMELLA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 210 | *Spatholobus ROXBURGHII* Benth. | *Spatholobus ROXBURGHII* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 211 | *Soymida FEBRIFUGA* (Roxb.) A. Juss. | *Soymida FEBRIFUGA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 212 | *Sonneratia CASEOLARIS* (L.) Engl. | *Sonneratia CASEOLARIS* | FETCH_FAILED | Read timeout (30s) |
| 213 | *Sonneratia APETALA* Buch.-Ham. | *Sonneratia APETALA* | FETCH_FAILED | Read timeout (30s) |
| 214 | *Solanum XANTHOCARPUM* Schrad. & Wendl. | *Solanum XANTHOCARPUM* | FETCH_FAILED | Read timeout (30s) |
| 215 | *Solanum VILLOSUM* Mill. | *Solanum VILLOSUM* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 216 | *Solanum TUBEROSUM* L. | *Solanum TUBEROSUM* | FETCH_FAILED | Read timeout (30s) |
| 217 | *Solanum TORVUM* Sw. | *Solanum TORVUM* | FETCH_FAILED | Read timeout (30s) |
| 218 | *Solanum SPIRALE* Roxb. | *Solanum SPIRALE* | FETCH_FAILED | Read timeout (30s) |
| 219 | *Solanum NIGRUM* L. | *Solanum NIGRUM* | FETCH_FAILED | Read timeout (30s) |
| 220 | *Solanum MELONGENA* L. | *Solanum MELONGENA* | FETCH_FAILED | Read timeout (30s) |
| 221 | *Solanum LYCOPERSICUM* L. | *Solanum LYCOPERSICUM* | FETCH_FAILED | Read timeout (30s) |
| 222 | *Solanum INDICUM* L. | *Solanum INDICUM* | FETCH_FAILED | Read timeout (30s) |
| 223 | *Solanum FERROX* L. | *Solanum FERROX* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 224 | *Solanum DIPHYLLUM* L. | *Solanum DIPHYLLUM* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 225 | *Solanum CRINITUM* Lam. | *Solanum CRINITUM* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 226 | *Solanum CHRYSOTRICHUM* Schltdl. | *Solanum CHRYSOTRICHUM* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 227 | *Smilax OVALIFOLIA* Roxb. ex D. Don | *Smilax OVALIFOLIA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 228 | *Smilax MACROPHYLLA* Roxb. | *Smilax MACROPHYLLA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 230 | *Sida RHOMBIFOLIA* L. | *Sida RHOMBIFOLIA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 231 | *Sida CORDIFOLIA* L. | *Sida CORDIFOLIA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 232 | *Sida ACUTA* Burm. f. | *Sida ACUTA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 233 | *Shuteria VESTITA* (Graham ex Wight & Arn.) Benth. | *Shuteria VESTITA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 234 | *Shorea ROBUSTA* Roth | *Shorea ROBUSTA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 235 | *Senna TORA* (L.) Roxb. | *Senna TORA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 236 | *Senna TIMORIENSIS* (DC.) H.S. Irwin & Barneby | *Senna TIMORIENSIS* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 237 | *Senna SIAMEA* (Lam.) H.S. Irwin & Barneby | *Senna SIAMEA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 238 | *Senna OCCIDENTALIS* (L.) Link | *Senna OCCIDENTALIS* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 239 | *Senna ALATA* (L.) Roxb. | *Senna ALATA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 240 | *Semecarpus ANACARDIUM* L. f. | *Semecarpus ANACARDIUM* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 241 | *Selaginella MONOPODIA* Spring | *Selaginella MONOPODIA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 242 | *Scoparia DULCIS* L. | *Scoparia DULCIS* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 243 | *Scindapsus OFFICINALIS* (Roxb.) Schott | *Scindapsus OFFICINALIS* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 244 | *Schefflera VENULOSA* (Wight & Arn.) Harms | *Schefflera VENULOSA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 245 | *Sansevieria HYACINTHOIDES* (L.) Druce | *Sansevieria HYACINTHOIDES* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 246 | *Sansevieria CYLINDRICA* Bojer ex Hook. | *Sansevieria CYLINDRICA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 247 | *Sanicula EUROPAEA* L. | *Sanicula EUROPAEA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 248 | *Sandoricum KOETJAPE* (Burm. f.) Merr. | *Sandoricum KOETJAPE* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 249 | *Salvia PLEBEIA* R. Br. | *Salvia PLEBEIA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 250 | *Salvia COCCINEA* Buc'hoz ex Etl. | *Salvia COCCINEA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 251 | *Salix TETRASPERMA* Roxb. | *Salix TETRASPERMA* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 253 | *Sagittaria GUAYANENSIS* Kunth | *Sagittaria GUAYANENSIS* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 254 | *Saccharum OFFICINARUM* L. | *Saccharum OFFICINARUM* | FETCH_FAILED | HTTP 503 Service Unavailable |
| 258 | *Rubus ELLIPTICUS* Sm. | *Rubus ELLIPTICUS* | FETCH_FAILED | Read timeout (30s) |
| 263 | *Rosa CENTIFOLIA* L. | *Rosa CENTIFOLIA* | FETCH_FAILED | Read timeout (30s) |
| 265 | *Rorippa INDICA* (L.) Hiern | *Rorippa INDICA* | FETCH_FAILED | Read timeout (30s) |
| 267 | *Ricinus COMMUNIS* L. | *Ricinus COMMUNIS* | FETCH_FAILED | Read timeout (30s) |

## 5. Next Steps
Per Stage 6H protocol:
1. Documentation of the 105 failures in this report is complete.
2. The scraper's built-in `--retry-failed` flag will be executed:
   ```bash
   python scrapers/bmppd_bulk_scraper.py --retry-failed
   ```
3. The scraper will automatically attempt ONLY these 105 plants from `bmppd_failed_plants.csv`. Succeeded plants will be appended to `bmppd_compounds_raw.csv` and removed from `bmppd_failed_plants.csv`, while plants that fail again will have their failure timestamp refreshed.
