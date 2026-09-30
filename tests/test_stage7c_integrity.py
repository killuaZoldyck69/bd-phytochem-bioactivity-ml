#!/usr/bin/env python3
"""
tests/test_stage7c_integrity.py
===============================
Stage 7C Automated Scope Lock & Integrity Verification Suite.

Validates that:
1. Master MPBD raw dataset hash matches the immutable verified hash.
2. Stage 7B frozen configuration hashes match exactly.
3. All 8 flora prediction CSVs exist, match their frozen SHA-256 hashes,
   contain exactly 7,315 rows with zero duplicate layers and zero missing values.
4. Applicability domain flags are strictly consistent with nearest-neighbor similarity.
5. Probability ranges are valid [0.0, 1.0].
"""

import hashlib
import json
from pathlib import Path
import unittest
import pandas as pd
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent

EXPECTED_HASHES = {
    "mpbd_plant_index.csv": "0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7",
    "stage7b_config_frozen_FULL.json": "ED5F00E529F0FE4D7CAE877DC53C88A589F5DF06C9EB6AFBB984DC33D9C81AB4",
    "stage7b_config_frozen.json": "ED5F00E529F0FE4D7CAE877DC53C88A589F5DF06C9EB6AFBB984DC33D9C81AB4",
    "flora_predictions_cox1_T6.csv": "234478E31FCE6CF0A8C738952ECCF9971C73205D797567EA4AE5C06185E5BC36",
    "flora_predictions_cox1_T5.csv": "958CF0ED73CC88722D09DE5FA1A37ED52F96F18C15F0EDEFBCAC11AA9147A34C",
    "flora_predictions_cox2_T6.csv": "D200E32FB72656D247F2FDCCE9A076AD9F25362EAB57A5F44C0B5B1E88137D05",
    "flora_predictions_cox2_T5.csv": "0B43A9428AA658D8993199607F5531278D39B71D11E37392603F24C2F6A0EBE2",
    "flora_predictions_xo_T6.csv": "BA8A53F44235F3AA5B6D4A17DF9D095AF6929D5B15A8786662D7CEB33B93F8F8",
    "flora_predictions_xo_T5.csv": "14D18F46F02446D93477994D8D3EBDE76FFCB8190A58D00F97CE4FA9F33FD6F1",
    "flora_predictions_maoa_T6.csv": "1DD23E625352C15454C9CEE83D2E36EFE22FF83F42A9DC179E987E1FBC6C7762",
    "flora_predictions_maoa_T5.csv": "C88058AC846C8F7155D610D2C8E37C5A9523CCCD8E6A2ADC7E6B79ADD2405577",
}

PREDICTION_FILES = [
    ("cox1", 6, "flora_predictions_cox1_T6.csv"),
    ("cox1", 5, "flora_predictions_cox1_T5.csv"),
    ("cox2", 6, "flora_predictions_cox2_T6.csv"),
    ("cox2", 5, "flora_predictions_cox2_T5.csv"),
    ("xo", 6, "flora_predictions_xo_T6.csv"),
    ("xo", 5, "flora_predictions_xo_T5.csv"),
    ("maoa", 6, "flora_predictions_maoa_T6.csv"),
    ("maoa", 5, "flora_predictions_maoa_T5.csv"),
]

def sha256_path(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()


class TestStage7CIntegrity(unittest.TestCase):

    def test_01_mpbd_master_hash(self):
        """Verify that MPBD plant index dataset remains byte-for-byte unchanged."""
        p = REPO_ROOT / "data/raw/mpbd/mpbd_plant_index.csv"
        self.assertTrue(p.exists(), f"Missing file: {p}")
        actual_hash = sha256_path(p)
        self.assertEqual(
            actual_hash,
            EXPECTED_HASHES["mpbd_plant_index.csv"],
            f"Master MPBD hash mismatch! Expected {EXPECTED_HASHES['mpbd_plant_index.csv']}, got {actual_hash}"
        )

    def test_02_frozen_config_hashes(self):
        """Verify that Stage 7B frozen configuration files are intact."""
        for cfg_name in ["stage7b_config_frozen_FULL.json", "stage7b_config_frozen.json"]:
            p = REPO_ROOT / "data/processed/modeling" / cfg_name
            self.assertTrue(p.exists(), f"Missing config: {p}")
            actual_hash = sha256_path(p)
            self.assertEqual(
                actual_hash,
                EXPECTED_HASHES[cfg_name],
                f"Config {cfg_name} hash mismatch! Expected {EXPECTED_HASHES[cfg_name]}, got {actual_hash}"
            )

    def test_03_frozen_config_model_family_lock(self):
        """Verify that frozen config restricts model families strictly to RF and 1-NN."""
        p = REPO_ROOT / "data/processed/modeling/stage7b_config_frozen_FULL.json"
        with open(p, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        self.assertIn("RandomForestClassifier", cfg["models"])
        self.assertIn("1-Nearest-Neighbour-Tanimoto", cfg["models"])
        self.assertEqual(len(cfg["models"]), 2, "Only 2 model families allowed in Stage 7B.")
        self.assertIn("Strictly RandomForest and 1-NN Tanimoto", cfg["model_family_restriction"])

    def test_04_prediction_files_integrity(self):
        """Verify all 8 prediction files: row count=7315, 0 duplicates, 0 missing, exact SHA-256."""
        for target, threshold, fname in PREDICTION_FILES:
            p = REPO_ROOT / "data/processed/modeling" / fname
            self.assertTrue(p.exists(), f"Missing prediction file: {p}")
            
            # Check SHA-256
            actual_hash = sha256_path(p)
            self.assertEqual(
                actual_hash,
                EXPECTED_HASHES[fname],
                f"Prediction file {fname} SHA-256 mismatch! Got {actual_hash}"
            )
            
            # Check contents
            df = pd.read_csv(p)
            self.assertEqual(len(df), 7315, f"{fname} must have exactly 7,315 rows.")
            self.assertEqual(df["layer"].nunique(), 7315, f"{fname} contains duplicate molecule layers.")
            self.assertEqual(df["predicted_probability"].isna().sum(), 0, f"{fname} contains missing probabilities.")
            self.assertEqual(df["nn_similarity"].isna().sum(), 0, f"{fname} contains missing similarities.")
            
            # Check probability bounds [0.0, 1.0]
            self.assertTrue((df["predicted_probability"] >= 0.0).all(), f"{fname} has prob < 0.0")
            self.assertTrue((df["predicted_probability"] <= 1.0).all(), f"{fname} has prob > 1.0")
            
            # Check applicability domain consistency
            self.assertTrue(
                np.all((df["nn_similarity"] >= 0.4) == df["in_domain_0.4"]),
                f"{fname} in_domain_0.4 boolean mismatch with nn_similarity >= 0.4"
            )
            self.assertTrue(
                np.all((df["nn_similarity"] >= 0.3) == df["in_domain_0.3"]),
                f"{fname} in_domain_0.3 boolean mismatch with nn_similarity >= 0.3"
            )


if __name__ == "__main__":
    unittest.main()
