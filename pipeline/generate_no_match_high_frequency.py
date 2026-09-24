import csv
from collections import defaultdict
from pathlib import Path
import re

resolved_file = Path("data/processed/compounds/compound_structures_resolved.csv")
out_file = Path("data/quality/no_match_high_frequency.csv")

with open(resolved_file, "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# Group no_match by compound_name_original
no_match_data = defaultdict(lambda: {"rows": 0, "plants": set(), "query_name": ""})

for r in rows:
    if r["match_type"] == "no_match":
        orig = r["compound_name_original"]
        no_match_data[orig]["rows"] += 1
        no_match_data[orig]["plants"].add(r["plant_index"])
        no_match_data[orig]["query_name"] = r["compound_name_query"]

def get_structural_category(name: str) -> str:
    if bool(re.match(r'^\([^\)]+\)-', name)):
        return "stereo_descriptor"
    elif ", " in name:
        return "cas_inverted"
    elif bool(re.search(r'\([A-Za-z0-9\s\-]{2,}\)|\[.+\]', name)):
        return "parenthetical_synonym"
    elif name.lower().endswith(('s', 'es')) or any(w in name.lower() for w in ['derivatives', 'fraction', 'extract', 'glycosides', 'alkaloids', 'phenols', 'flavonoids', 'tannins', 'saponins']):
        return "class_or_plural"
    else:
        return "other"

results = []
for orig, data in no_match_data.items():
    if data["rows"] >= 3:
        results.append({
            "compound_name_original": orig,
            "n_rows": data["rows"],
            "n_plants": len(data["plants"]),
            "structural_category": get_structural_category(orig)
        })

results.sort(key=lambda x: (x["n_plants"], x["n_rows"]), reverse=True)

with open(out_file, "w", newline="", encoding="utf-8") as f:
    fieldnames = ["compound_name_original", "n_rows", "n_plants", "structural_category"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"Generated {out_file} with {len(results)} high-frequency items (>= 3 rows).")
print(f"Top 40 items:")
for i, r in enumerate(results[:40], 1):
    print(f"{i:2d}. Name: '{r['compound_name_original']}' | Plants: {r['n_plants']} | Rows: {r['n_rows']} | Category: {r['structural_category']}")
