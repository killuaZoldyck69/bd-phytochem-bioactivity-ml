"""Quick integrity verification for Stage 9 outputs."""
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
manifest = json.loads((REPO / "data/validation/stage9_docking_integrity_manifest.json").read_text())

print("=== Stage 9 Output Artifact Integrity Check ===")
all_ok = True
for relpath, expected_hash in manifest["output_artifacts"].items():
    fullpath = REPO / relpath
    if fullpath.exists():
        actual = hashlib.sha256(fullpath.read_bytes()).hexdigest().upper()
        ok = actual == expected_hash
        if not ok:
            all_ok = False
        status = "OK" if ok else "MISMATCH"
        print(f"  [{status}] {relpath}")
    else:
        print(f"  [MISSING] {relpath}")
        all_ok = False

print()
print(f"Overall: {'ALL OK' if all_ok else 'ISSUES DETECTED'}")
