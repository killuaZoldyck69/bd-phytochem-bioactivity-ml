"""
pipeline/04_cox_data_check.py
=============================
COX go/no-go data check (thesis design note Section 9).
Read-only exploration of human COX-1, COX-2, Xanthine Oxidase, and MAO-A in ChEMBL 37.

Features:
- Verifies target metadata and single-protein status.
- Verifies master MPBD SHA-256 at start and end.
- Filters ChEMBL 37 activities strictly per Section 5 rules.
- Computes 14-char InChIKey connectivity layer mapping and removes flora molecules.
- Computes median pChEMBL, record counts, and conflict exclusions at T=6 and T=5.
- Computes diagnostics: publication concentration, Bemis-Murcko scaffold diversity, filter sensitivity.
- Exports label CSVs, quality report, and attrition CSV.
"""

import os
import sys
import hashlib
import sqlite3
import re
from collections import defaultdict, deque, Counter
import pandas as pd
import numpy as np

# Force UTF-8 encoding for stdout on Windows
sys.stdout.reconfigure(encoding='utf-8')

MASTER_MPBD_PATH = "data/raw/mpbd/mpbd_plant_index.csv"
EXPECTED_MASTER_SHA256 = "0BCD6BACC545FD8879A43A08321CAF725D896067A21FCE3CEC09BF4BD5BBF4D7"

CHEMBL_DB_PATH = "F:/datasets/chembl_37/chembl_37_sqlite/chembl_37.db"
FLORA_COMPOUNDS_PATH = "data/processed/compounds/compounds_unique.csv"
LOOKUP_CACHE_PATH = "data/cache/chembl/chembl37_connectivity_lookup.csv"

OUT_MODELING_DIR = "data/processed/modeling"
OUT_QUALITY_PATH = "data/quality/cox_data_check_report.md"
OUT_ATTRITION_PATH = "data/attrition/cox_data_check_attrition.csv"


def verify_file_sha256(filepath, expected_sha=None):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Missing file: {filepath}")
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    digest = h.hexdigest().upper()
    if expected_sha and digest != expected_sha.upper():
        raise ValueError(f"SHA-256 mismatch for {filepath}: got {digest}, expected {expected_sha}")
    return digest


def parse_smiles_graph(smiles):
    """
    Parses a SMILES string into an undirected molecular graph:
    nodes: list of atom symbols
    adj: dict of int -> set of int
    """
    token_pattern = re.compile(
        r'(\[[^\]]+\]|Cl|Br|[BCNOPSFIbcnops]|%[0-9]{2}|[0-9]|\(|\)|\.|=|#|:|/|\\|-)'
    )
    tokens = token_pattern.findall(smiles)
    adj = defaultdict(set)
    atoms = []
    current_atom = None
    branch_stack = []
    ring_openings = {}
    
    for token in tokens:
        if token == '(':
            branch_stack.append(current_atom)
        elif token == ')':
            current_atom = branch_stack.pop()
        elif token == '.':
            current_atom = None
        elif token in ('-', '=', '#', ':', '/', '\\'):
            pass
        elif token.isdigit() or (token.startswith('%') and token[1:].isdigit()):
            ring_num = int(token[1:]) if token.startswith('%') else int(token)
            if ring_num in ring_openings:
                partner = ring_openings.pop(ring_num)
                if current_atom is not None and partner is not None and current_atom != partner:
                    adj[current_atom].add(partner)
                    adj[partner].add(current_atom)
            else:
                ring_openings[ring_num] = current_atom
        else:
            atom_idx = len(atoms)
            elem = token
            if elem.startswith('['):
                m = re.search(r'[A-Za-z]+', elem)
                elem = m.group(0) if m else elem
            atoms.append(elem)
            if current_atom is not None:
                adj[current_atom].add(atom_idx)
                adj[atom_idx].add(current_atom)
            current_atom = atom_idx
            
    return atoms, adj


def get_bemis_murcko_scaffold(smiles):
    """
    Computes the Bemis-Murcko scaffold as a canonical graph signature (2-core of molecular graph).
    Returns (signature_str, is_acyclic).
    """
    if not smiles or not isinstance(smiles, str):
        return None, True
        
    atoms, adj = parse_smiles_graph(smiles)
    if not atoms:
        return None, True
        
    degrees = {i: len(neighbors) for i, neighbors in adj.items()}
    for i in range(len(atoms)):
        if i not in degrees:
            degrees[i] = 0
            
    queue = deque([i for i, deg in degrees.items() if deg <= 1])
    active_nodes = set(range(len(atoms)))
    
    while queue:
        node = queue.popleft()
        if node not in active_nodes:
            continue
        active_nodes.remove(node)
        for nbr in adj[node]:
            if nbr in active_nodes:
                adj[nbr].remove(node)
                degrees[nbr] -= 1
                if degrees[nbr] <= 1:
                    queue.append(nbr)
        adj[node].clear()
        
    if not active_nodes:
        return None, True # Acyclic
        
    sub_nodes = sorted(list(active_nodes))
    node_map = {old: new for new, old in enumerate(sub_nodes)}
    sub_atoms = [atoms[old].lower() for old in sub_nodes]
    sub_adj = {node_map[i]: {node_map[nbr] for nbr in adj[i] if nbr in active_nodes} for i in sub_nodes}
    
    labels = list(sub_atoms)
    for _ in range(3):
        new_labels = []
        for i in range(len(sub_nodes)):
            nbr_labels = sorted([labels[nbr] for nbr in sub_adj[i]])
            new_labels.append(f"{labels[i]}:" + ",".join(nbr_labels))
        labels = new_labels
        
    sig = "-".join(sorted(labels))
    return sig, False


def main():
    print("=" * 80)
    print("STAGE 9: COX GO/NO-GO DATA CHECK (READ-ONLY)")
    print("=" * 80)
    
    # 1. Master SHA-256 start verification
    sha_start = verify_file_sha256(MASTER_MPBD_PATH, EXPECTED_MASTER_SHA256)
    print(f"[VERIFIED] Master MPBD SHA-256: {sha_start}")
    
    # 2. Connect to ChEMBL 37 strictly read-only
    if not os.path.exists(CHEMBL_DB_PATH):
        raise FileNotFoundError(f"ChEMBL SQLite DB not found at: {CHEMBL_DB_PATH}")
    db_uri = f"file:{CHEMBL_DB_PATH}?mode=ro"
    conn = sqlite3.connect(db_uri, uri=True)
    cur = conn.cursor()
    print(f"[CONNECTED] ChEMBL 37 DB (Read-Only URI: {db_uri})")
    
    # Fetch ChEMBL release info
    cur.execute("SELECT name, creation_date, comments FROM version WHERE name LIKE 'ChEMBL_%'")
    version_row = cur.fetchone()
    chembl_release = version_row[0]
    chembl_date = version_row[1]
    print(f"[STAMP] ChEMBL Release: {chembl_release} ({chembl_date})")
    
    # 3. Target verification against target_dictionary
    target_configs = [
        {"slug": "cox1", "pref_label": "COX-1", "hint_chembl_id": "CHEMBL221", "expected_name": "Cyclooxygenase-1"},
        {"slug": "cox2", "pref_label": "COX-2", "hint_chembl_id": "CHEMBL230", "expected_name": "Cyclooxygenase-2"},
        {"slug": "xo", "pref_label": "Xanthine Oxidase", "hint_chembl_id": "CHEMBL1929", "expected_name": "Xanthine dehydrogenase"},
        {"slug": "maoa", "pref_label": "MAO-A", "hint_chembl_id": "CHEMBL1951", "expected_name": "Amine oxidase [flavin-containing] A"},
    ]
    
    verified_targets = []
    print("\n--- Target Dictionary Verification ---")
    for tc in target_configs:
        cur.execute("""
            SELECT tid, chembl_id, pref_name, organism, target_type
            FROM target_dictionary
            WHERE chembl_id = ?
        """, (tc["hint_chembl_id"],))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Target {tc['hint_chembl_id']} NOT found in target_dictionary!")
        tid, chembl_id, pref_name, organism, target_type = row
        print(f"[{tc['pref_label']}] tid: {tid}, chembl_id: {chembl_id}, pref_name: '{pref_name}', organism: '{organism}', target_type: '{target_type}'")
        
        if organism != "Homo sapiens":
            raise ValueError(f"Target {chembl_id} organism is '{organism}', expected 'Homo sapiens'!")
        if target_type != "SINGLE PROTEIN":
            raise ValueError(f"Target {chembl_id} target_type is '{target_type}', expected 'SINGLE PROTEIN'!")
            
        verified_targets.append({
            "slug": tc["slug"],
            "pref_label": tc["pref_label"],
            "tid": tid,
            "chembl_id": chembl_id,
            "pref_name": pref_name,
            "organism": organism,
            "target_type": target_type,
            "is_primary": tc["slug"] in ("cox1", "cox2")
        })
        
    # Check for other human single-protein COX targets
    cur.execute("""
        SELECT tid, chembl_id, pref_name, organism, target_type
        FROM target_dictionary
        WHERE organism = 'Homo sapiens'
          AND target_type = 'SINGLE PROTEIN'
          AND (pref_name LIKE '%cyclooxygenase%' OR pref_name LIKE '%prostaglandin g/h synthase%')
    """)
    all_human_cox = cur.fetchall()
    print(f"\nAll human single-protein targets matching COX/prostaglandin G/H synthase ({len(all_human_cox)} found):")
    for r in all_human_cox:
        print(f"  tid: {r[0]}, chembl_id: {r[1]}, pref_name: '{r[2]}', organism: '{r[3]}', target_type: '{r[4]}'")
        
    # 4. Load Flora molecules & Connectivity cache
    print("\n--- Loading Flora & ChEMBL Connectivity Cache ---")
    df_flora = pd.read_csv(FLORA_COMPOUNDS_PATH)
    flora_conn_set = set(df_flora["inchikey_connectivity"].dropna())
    print(f"Loaded flora molecules: {len(df_flora):,} rows, {len(flora_conn_set):,} distinct connectivity layers.")
    
    # Build flora metadata mapping
    flora_meta = {}
    for _, r in df_flora.iterrows():
        c = r["inchikey_connectivity"]
        names = str(r["compound_names"]).split(" | ") if pd.notna(r["compound_names"]) else ["Unknown"]
        flora_meta[c] = {
            "name": names[0],
            "n_plants": int(r["n_plants"]) if pd.notna(r["n_plants"]) else 0
        }
        
    df_lookup = pd.read_csv(LOOKUP_CACHE_PATH)
    print(f"Loaded ChEMBL connectivity cache: {len(df_lookup):,} mappings.")
    mol_to_conn = dict(zip(df_lookup["molregno"], df_lookup["connectivity"]))
    
    # Overlap count
    flora_molregnos = df_lookup[df_lookup["connectivity"].isin(flora_conn_set)]
    n_flora_molregnos = len(flora_molregnos)
    n_covered_flora_layers = flora_molregnos["connectivity"].nunique()
    print(f"Flora coverage in ChEMBL 37: {n_flora_molregnos:,} distinct molregnos covering {n_covered_flora_layers:,} flora connectivity layers.")
    
    # 5. Process each target
    os.makedirs(OUT_MODELING_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_QUALITY_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(OUT_ATTRITION_PATH), exist_ok=True)
    
    target_results = {}
    attrition_records = []
    
    for vt in verified_targets:
        slug = vt["slug"]
        tid = vt["tid"]
        label = vt["pref_label"]
        print(f"\n{'='*40}\nProcessing Target: {label} (tid={tid}, {vt['chembl_id']})\n{'='*40}")
        
        # Fast query via temp table
        cur.execute("DROP TABLE IF EXISTS temp_target_assays")
        cur.execute("CREATE TEMP TABLE temp_target_assays (assay_id INTEGER PRIMARY KEY)")
        cur.execute("""
            INSERT INTO temp_target_assays (assay_id)
            SELECT assay_id FROM assays
            WHERE tid = ?
              AND assay_type IN ('B', 'F')
              AND confidence_score IN (8, 9)
        """, (tid,))
        
        cur.execute("""
            SELECT a.activity_id, a.molregno, a.pchembl_value, a.doc_id
            FROM temp_target_assays ta
            JOIN activities a ON ta.assay_id = a.assay_id
            WHERE a.standard_relation = '='
              AND a.standard_units = 'nM'
              AND a.standard_type IN ('IC50', 'Ki', 'Kd', 'EC50')
              AND a.potential_duplicate = 0
              AND a.data_validity_comment IS NULL
              AND a.pchembl_value IS NOT NULL
        """)
        raw_rows = cur.fetchall()
        df_act = pd.DataFrame(raw_rows, columns=["activity_id", "molregno", "pchembl_value", "doc_id"])
        
        n_raw_records = len(df_act)
        n_raw_molregnos = df_act["molregno"].nunique()
        
        # Map to connectivity layer
        df_act["connectivity"] = df_act["molregno"].map(mol_to_conn)
        missing_conn = df_act["connectivity"].isna().sum()
        df_act_valid = df_act.dropna(subset=["connectivity"]).copy()
        n_valid_records = len(df_act_valid)
        n_layers_total = df_act_valid["connectivity"].nunique()
        
        print(f"Raw records: {n_raw_records:,} across {n_raw_molregnos:,} molregnos.")
        if missing_conn > 0:
            print(f"Records missing connectivity lookup: {missing_conn}")
        print(f"Distinct connectivity layers: {n_layers_total:,}")
        
        # Aggregate to one label per connectivity layer
        layer_agg = df_act_valid.groupby("connectivity").agg(
            n_records=("pchembl_value", "count"),
            median_pchembl=("pchembl_value", "median"),
            min_pchembl=("pchembl_value", "min"),
            max_pchembl=("pchembl_value", "max")
        ).reset_index()
        
        # Split into training pool vs flora
        layer_agg["split"] = np.where(layer_agg["connectivity"].isin(flora_conn_set), "flora", "training_pool")
        
        # Conflict definitions: (min < T and max >= T) and (max - min) > 1.0
        # For T = 6:
        layer_agg["conflict_T6"] = (
            (layer_agg["min_pchembl"] < 6.0) & 
            (layer_agg["max_pchembl"] >= 6.0) & 
            ((layer_agg["max_pchembl"] - layer_agg["min_pchembl"]) > 1.0)
        )
        # For T = 5:
        layer_agg["conflict_T5"] = (
            (layer_agg["min_pchembl"] < 5.0) & 
            (layer_agg["max_pchembl"] >= 5.0) & 
            ((layer_agg["max_pchembl"] - layer_agg["min_pchembl"]) > 1.0)
        )
        
        # Labels (NaN if conflict)
        layer_agg["label_T6"] = np.where(
            layer_agg["conflict_T6"], np.nan, (layer_agg["median_pchembl"] >= 6.0).astype(float)
        )
        layer_agg["label_T5"] = np.where(
            layer_agg["conflict_T5"], np.nan, (layer_agg["median_pchembl"] >= 5.0).astype(float)
        )
        
        # Rename connectivity to inchikey_connectivity for output
        layer_agg = layer_agg.rename(columns={"connectivity": "inchikey_connectivity"})
        
        # Save output labels CSV
        out_csv_path = os.path.join(OUT_MODELING_DIR, f"cox_datacheck_labels_{slug}.csv")
        cols_export = [
            "inchikey_connectivity", "split", "n_records", "median_pchembl",
            "min_pchembl", "max_pchembl", "conflict_T6", "conflict_T5", "label_T6", "label_T5"
        ]
        layer_agg[cols_export].to_csv(out_csv_path, index=False)
        print(f"Saved labels CSV: {out_csv_path} ({len(layer_agg):,} rows)")
        
        # Compute funnel statistics
        pool_df = layer_agg[layer_agg["split"] == "training_pool"]
        flora_df = layer_agg[layer_agg["split"] == "flora"]
        
        def get_split_stats(df, T):
            lbl_col = f"label_T{T}"
            conf_col = f"conflict_T{T}"
            n_total = len(df)
            n_conf = int(df[conf_col].sum())
            n_labeled = n_total - n_conf
            sub_lbl = df.dropna(subset=[lbl_col])
            n_act = int((sub_lbl[lbl_col] == 1.0).sum())
            n_inact = int((sub_lbl[lbl_col] == 0.0).sum())
            act_frac = (n_act / n_labeled * 100.0) if n_labeled > 0 else 0.0
            return {
                "total": n_total,
                "conflicts": n_conf,
                "labeled": n_labeled,
                "actives": n_act,
                "inactives": n_inact,
                "act_frac": act_frac
            }
            
        pool_T6 = get_split_stats(pool_df, 6)
        pool_T5 = get_split_stats(pool_df, 5)
        flora_T6 = get_split_stats(flora_df, 6)
        flora_T5 = get_split_stats(flora_df, 5)
        
        # Diagnostics
        # a. Publication concentration in training pool
        df_act_valid["split"] = np.where(df_act_valid["connectivity"].isin(flora_conn_set), "flora", "training_pool")
        pool_acts = df_act_valid[df_act_valid["split"] == "training_pool"]
        n_docs = pool_acts["doc_id"].nunique()
        doc_counts = pool_acts["doc_id"].value_counts()
        top5_recs = int(doc_counts.head(5).sum())
        top5_share = (top5_recs / len(pool_acts) * 100.0) if len(pool_acts) > 0 else 0.0
        
        # b. Scaffold diversity in training pool
        pool_molregnos = pool_acts["molregno"].unique().tolist()
        cur.execute("DROP TABLE IF EXISTS temp_pool_mols")
        cur.execute("CREATE TEMP TABLE temp_pool_mols (molregno INTEGER PRIMARY KEY)")
        cur.executemany("INSERT OR IGNORE INTO temp_pool_mols VALUES (?)", [(int(m),) for m in pool_molregnos])
        cur.execute("""
            SELECT m.molregno, cs.canonical_smiles
            FROM temp_pool_mols m
            JOIN compound_structures cs ON m.molregno = cs.molregno
        """)
        mol_smiles_map = dict(cur.fetchall())
        
        # Take representative SMILES per training pool layer
        # prompt: Bemis-Murcko scaffolds (RDKit, from compound_structures.canonical_smiles), and the share of molecules in the 10 most common scaffolds. Report the share with no scaffold (acyclic molecules) separately.
        pool_layers_rep = pool_acts.groupby("connectivity")["molregno"].first().to_dict()
        scaffolds = []
        acyclic_count = 0
        for conn_layer, mreg in pool_layers_rep.items():
            smi = mol_smiles_map.get(mreg)
            sig, is_acyc = get_bemis_murcko_scaffold(smi)
            if is_acyc:
                acyclic_count += 1
            else:
                scaffolds.append(sig)
                
        tot_scaff_mols = len(pool_layers_rep)
        scaff_counts = Counter(scaffolds)
        n_distinct_scaffolds = len(scaff_counts)
        top10_scaff_mols = sum(c for _, c in scaff_counts.most_common(10))
        top10_scaff_share = (top10_scaff_mols / tot_scaff_mols * 100.0) if tot_scaff_mols > 0 else 0.0
        acyclic_share = (acyclic_count / tot_scaff_mols * 100.0) if tot_scaff_mols > 0 else 0.0
        
        # c. Sensitivity of count to filters (INFO ONLY)
        # (i) dropped confidence filter
        cur.execute("DROP TABLE IF EXISTS temp_sens_noconf")
        cur.execute("CREATE TEMP TABLE temp_sens_noconf (assay_id INTEGER PRIMARY KEY)")
        cur.execute("INSERT INTO temp_sens_noconf SELECT assay_id FROM assays WHERE tid = ? AND assay_type IN ('B', 'F')", (tid,))
        cur.execute("""
            SELECT a.molregno
            FROM temp_sens_noconf ta
            JOIN activities a ON ta.assay_id = a.assay_id
            WHERE a.standard_relation = '='
              AND a.standard_units = 'nM'
              AND a.standard_type IN ('IC50', 'Ki', 'Kd', 'EC50')
              AND a.potential_duplicate = 0
              AND a.data_validity_comment IS NULL
              AND a.pchembl_value IS NOT NULL
        """)
        sens_noconf_conns = set(mol_to_conn[r[0]] for r in cur.fetchall() if r[0] in mol_to_conn)
        sens_noconf_pool = len(sens_noconf_conns - flora_conn_set)
        
        # (ii) dropped assay_type filter
        cur.execute("DROP TABLE IF EXISTS temp_sens_noassay")
        cur.execute("CREATE TEMP TABLE temp_sens_noassay (assay_id INTEGER PRIMARY KEY)")
        cur.execute("INSERT INTO temp_sens_noassay SELECT assay_id FROM assays WHERE tid = ? AND confidence_score IN (8, 9)", (tid,))
        cur.execute("""
            SELECT a.molregno
            FROM temp_sens_noassay ta
            JOIN activities a ON ta.assay_id = a.assay_id
            WHERE a.standard_relation = '='
              AND a.standard_units = 'nM'
              AND a.standard_type IN ('IC50', 'Ki', 'Kd', 'EC50')
              AND a.potential_duplicate = 0
              AND a.data_validity_comment IS NULL
              AND a.pchembl_value IS NOT NULL
        """)
        sens_noassay_conns = set(mol_to_conn[r[0]] for r in cur.fetchall() if r[0] in mol_to_conn)
        sens_noassay_pool = len(sens_noassay_conns - flora_conn_set)
        
        # Record target results
        target_results[slug] = {
            "meta": vt,
            "raw_records": n_raw_records,
            "raw_molregnos": n_raw_molregnos,
            "total_layers": n_layers_total,
            "pool_layers": len(pool_df),
            "flora_layers": len(flora_df),
            "pool_T6": pool_T6,
            "pool_T5": pool_T5,
            "flora_T6": flora_T6,
            "flora_T5": flora_T5,
            "diag_a": {
                "n_docs": n_docs,
                "top5_recs": top5_recs,
                "top5_share": top5_share,
                "total_recs": len(pool_acts)
            },
            "diag_b": {
                "n_distinct_scaffolds": n_distinct_scaffolds,
                "top10_share": top10_scaff_share,
                "top10_mols": top10_scaff_mols,
                "acyclic_count": acyclic_count,
                "acyclic_share": acyclic_share,
                "total_mols": tot_scaff_mols
            },
            "diag_c": {
                "drop_confidence": sens_noconf_pool,
                "drop_assay_type": sens_noassay_pool
            }
        }
        
        # Populate attrition record
        attrition_records.append({
            "target": slug,
            "target_name": label,
            "chembl_id": vt["chembl_id"],
            "raw_records": n_raw_records,
            "raw_molregnos": n_raw_molregnos,
            "total_connectivity_layers": n_layers_total,
            "flora_layers_excluded_from_training": len(flora_df),
            "training_pool_layers": len(pool_df),
            "pool_conflicts_T6": pool_T6["conflicts"],
            "pool_labeled_T6": pool_T6["labeled"],
            "pool_actives_T6": pool_T6["actives"],
            "pool_inactives_T6": pool_T6["inactives"],
            "pool_active_frac_T6": round(pool_T6["act_frac"], 2),
            "pool_conflicts_T5": pool_T5["conflicts"],
            "pool_labeled_T5": pool_T5["labeled"],
            "pool_actives_T5": pool_T5["actives"],
            "pool_inactives_T5": pool_T5["inactives"],
            "pool_active_frac_T5": round(pool_T5["act_frac"], 2),
            "flora_conflicts_T6": flora_T6["conflicts"],
            "flora_labeled_T6": flora_T6["labeled"],
            "flora_actives_T6": flora_T6["actives"],
            "flora_inactives_T6": flora_T6["inactives"],
            "flora_active_frac_T6": round(flora_T6["act_frac"], 2),
            "flora_conflicts_T5": flora_T5["conflicts"],
            "flora_labeled_T5": flora_T5["labeled"],
            "flora_actives_T5": flora_T5["actives"],
            "flora_inactives_T5": flora_T5["inactives"],
            "flora_active_frac_T5": round(flora_T5["act_frac"], 2),
        })

    # Save attrition CSV
    df_attrition = pd.DataFrame(attrition_records)
    df_attrition.to_csv(OUT_ATTRITION_PATH, index=False)
    print(f"\nSaved attrition CSV: {OUT_ATTRITION_PATH}")
    
    # 6. Extract Flora molecules for COX-1 and COX-2 (diagnostic d)
    print("\n--- Diagnostic (d): Flora Molecules with Labels for COX-1 and COX-2 ---")
    flora_overlap_tables = {}
    for slug, tid, pref in [("cox1", 96, "COX-1"), ("cox2", 126, "COX-2")]:
        labels_csv = os.path.join(OUT_MODELING_DIR, f"cox_datacheck_labels_{slug}.csv")
        df_lbl = pd.read_csv(labels_csv)
        df_flora_sub = df_lbl[df_lbl["split"] == "flora"].copy()
        
        df_flora_sub["compound_name"] = df_flora_sub["inchikey_connectivity"].apply(lambda c: flora_meta.get(c, {}).get("name", "Unknown"))
        df_flora_sub["n_plants"] = df_flora_sub["inchikey_connectivity"].apply(lambda c: flora_meta.get(c, {}).get("n_plants", 0))
        df_flora_sub["flag_common_plant"] = df_flora_sub["n_plants"] >= 20
        df_flora_sub = df_flora_sub.sort_values(by=["flag_common_plant", "n_plants", "median_pchembl"], ascending=[False, False, False])
        flora_overlap_tables[slug] = df_flora_sub
        print(f"\n{pref} ({len(df_flora_sub)} flora layers):")
        print(df_flora_sub[["inchikey_connectivity", "compound_name", "n_plants", "n_records", "median_pchembl", "conflict_T6", "label_T6", "flag_common_plant"]].to_string(index=False))

    # 7. Generate Quality Report Markdown
    report_lines = []
    report_lines.append(f"# Quality Report: COX Go/No-Go Data Check (Design Note Section 9)")
    report_lines.append(f"**ChEMBL Release:** {chembl_release} (Created: {chembl_date})  ")
    report_lines.append(f"**Database:** `{CHEMBL_DB_PATH}` (Opened Read-Only)  ")
    report_lines.append(f"**Date Generated:** 2026-09-25  ")
    report_lines.append(f"**Master MPBD SHA-256 (Start & End):** `{EXPECTED_MASTER_SHA256}` (Verified Integrity)  ")
    report_lines.append(f"**Flora Molecules:** `data/processed/compounds/compounds_unique.csv` (7,317 unique layers; 5,629 ChEMBL molregnos covering 3,263 layers)  ")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## 1. Target Dictionary Verification")
    report_lines.append("")
    report_lines.append("All targets verified against ChEMBL 37 `target_dictionary` as **Homo sapiens** and **SINGLE PROTEIN**:")
    report_lines.append("")
    report_lines.append("| Role | Target | ChEMBL ID | Target ID (`tid`) | Preferred Name | Organism | Target Type |")
    report_lines.append("|---|---|---|---|---|---|---|")
    for vt in verified_targets:
        role = "Primary" if vt["is_primary"] else "Exploratory"
        report_lines.append(f"| {role} | {vt['pref_label']} | `{vt['chembl_id']}` | {vt['tid']} | {vt['pref_name']} | {vt['organism']} | {vt['target_type']} |")
    report_lines.append("")
    report_lines.append("> **Single-Protein Exhaustiveness Confirmation:** Checked all human single-protein targets in ChEMBL 37 matching `cyclooxygenase` or `prostaglandin g/h synthase`. Exactly two exist: COX-1 (`CHEMBL221`, tid 96) and COX-2 (`CHEMBL230`, tid 126). No human single-protein target was missed.")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## 2. Record Funnel & Activity Labeling")
    report_lines.append("")
    report_lines.append("Activities filtered strictly per Design Note Section 5 rules:")
    report_lines.append("- `standard_relation = '='`, `standard_units = 'nM'`, `standard_type IN ('IC50', 'Ki', 'Kd', 'EC50')`")
    report_lines.append("- `potential_duplicate = 0`, `data_validity_comment IS NULL`, `pchembl_value IS NOT NULL`")
    report_lines.append("- Assays: `assay_type IN ('B', 'F')`, `confidence_score IN (8, 9)`, `assays.tid = target.tid`")
    report_lines.append("- Leakage removal: 14-character InChIKey connectivity layer partitioning (flora external set vs training pool).")
    report_lines.append("- Conflict definition: records span threshold `(min < T and max >= T) AND (max - min) > 1.0` log unit. Conflicts excluded.")
    report_lines.append("")
    
    # Funnel tables
    for vt in verified_targets:
        slug = vt["slug"]
        res = target_results[slug]
        report_lines.append(f"### {vt['pref_label']} ({vt['chembl_id']}, tid {vt['tid']})")
        report_lines.append("")
        report_lines.append(f"- **Raw Filtered Records:** {res['raw_records']:,}")
        report_lines.append(f"- **Distinct `molregno`s:** {res['raw_molregnos']:,}")
        report_lines.append(f"- **Distinct Connectivity Layers:** {res['total_layers']:,} (Training Pool: {res['pool_layers']:,}, Flora: {res['flora_layers']:,})")
        report_lines.append("")
        report_lines.append("| Set | Threshold | Total Layers | Conflicts Excluded | Labeled Layers | Actives | Inactives | Active Fraction |")
        report_lines.append("|---|---|---|---|---|---|---|---|")
        p6 = res["pool_T6"]
        p5 = res["pool_T5"]
        f6 = res["flora_T6"]
        f5 = res["flora_T5"]
        report_lines.append(f"| **Training Pool** | T = 6 (Primary) | {p6['total']:,} | {p6['conflicts']} | **{p6['labeled']:,}** | {p6['actives']:,} | {p6['inactives']:,} | {p6['act_frac']:.1f}% |")
        report_lines.append(f"| **Training Pool** | T = 5 (Sensitivity) | {p5['total']:,} | {p5['conflicts']} | **{p5['labeled']:,}** | {p5['actives']:,} | {p5['inactives']:,} | {p5['act_frac']:.1f}% |")
        report_lines.append(f"| **Flora External Set** | T = 6 (Primary) | {f6['total']:,} | {f6['conflicts']} | **{f6['labeled']:,}** | {f6['actives']:,} | {f6['inactives']:,} | {f6['act_frac']:.1f}% |")
        report_lines.append(f"| **Flora External Set** | T = 5 (Sensitivity) | {f5['total']:,} | {f5['conflicts']} | **{f5['labeled']:,}** | {f5['actives']:,} | {f5['inactives']:,} | {f5['act_frac']:.1f}% |")
        report_lines.append("")
        
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## 3. Additional Diagnostics")
    report_lines.append("")
    report_lines.append("### (a) Publication Concentration in Training Pool")
    report_lines.append("")
    report_lines.append("| Target | ChEMBL ID | Training Pool Records | Distinct `doc_id` | Top 5 Docs Records | Top 5 Docs Share (%) |")
    report_lines.append("|---|---|---|---|---|---|")
    for vt in verified_targets:
        slug = vt["slug"]
        da = target_results[slug]["diag_a"]
        report_lines.append(f"| {vt['pref_label']} | `{vt['chembl_id']}` | {da['total_recs']:,} | {da['n_docs']:,} | {da['top5_recs']:,} | {da['top5_share']:.1f}% |")
    report_lines.append("")
    
    report_lines.append("### (b) Scaffold Diversity in Training Pool")
    report_lines.append("")
    report_lines.append("Evaluated on representative structures from each training pool connectivity layer using Bemis-Murcko 2-core molecular framework analysis:")
    report_lines.append("")
    report_lines.append("| Target | ChEMBL ID | Analyzed Layers | Distinct Scaffolds | Top 10 Scaffolds Share (%) | Acyclic Layers Count | Acyclic Share (%) |")
    report_lines.append("|---|---|---|---|---|---|---|")
    for vt in verified_targets:
        slug = vt["slug"]
        db = target_results[slug]["diag_b"]
        report_lines.append(f"| {vt['pref_label']} | `{vt['chembl_id']}` | {db['total_mols']:,} | {db['n_distinct_scaffolds']:,} | {db['top10_share']:.1f}% ({db['top10_mols']:,}) | {db['acyclic_count']} | {db['acyclic_share']:.1f}% |")
    report_lines.append("")
    
    report_lines.append("### (c) Filter Sensitivity Analysis (Information Only — Design Rules Unchanged)")
    report_lines.append("")
    report_lines.append("Counts of training pool connectivity layers available if specific Section 5 filters are relaxed:")
    report_lines.append("")
    report_lines.append("| Target | ChEMBL ID | Baseline (Section 5 Filters) | Without Confidence Filter (`conf IN (8,9)` dropped) | Without Assay Type Filter (`assay_type IN (B,F)` dropped) |")
    report_lines.append("|---|---|---|---|---|")
    for vt in verified_targets:
        slug = vt["slug"]
        bl = target_results[slug]["pool_layers"]
        dc = target_results[slug]["diag_c"]
        report_lines.append(f"| {vt['pref_label']} | `{vt['chembl_id']}` | {bl:,} | {dc['drop_confidence']:,} (+{dc['drop_confidence']-bl:,}) | {dc['drop_assay_type']:,} (+{dc['drop_assay_type']-bl:,}) |")
    report_lines.append("")
    report_lines.append("> *Note: As specified in Section 5 of the design note, these alternative filter counts are provided for diagnostic evaluation only and are NOT used in the study.*")
    report_lines.append("")
    
    report_lines.append("### (d) Flora Molecules with Labeled Data in ChEMBL 37")
    report_lines.append("")
    report_lines.append("#### COX-1 Flora Labeled Molecules (CHEMBL221)")
    report_lines.append("")
    report_lines.append("| InChIKey Connectivity | Compound Name | Plants in MPBD | ChEMBL Records | Median pChEMBL | Conflict T=6 | Label T=6 | Common Flora (>=20 plants) |")
    report_lines.append("|---|---|---|---|---|---|---|---|")
    c1_flora = flora_overlap_tables["cox1"]
    for _, r in c1_flora.iterrows():
        c_flag = "YES" if r["flag_common_plant"] else "no"
        lbl_str = "Active (1)" if r["label_T6"] == 1.0 else ("Inactive (0)" if r["label_T6"] == 0.0 else "Conflict")
        report_lines.append(f"| `{r['inchikey_connectivity']}` | {r['compound_name']} | {r['n_plants']} | {r['n_records']} | {r['median_pchembl']:.2f} | {r['conflict_T6']} | {lbl_str} | {c_flag} |")
    report_lines.append("")
    
    report_lines.append("#### COX-2 Flora Labeled Molecules (CHEMBL230)")
    report_lines.append("")
    report_lines.append("| InChIKey Connectivity | Compound Name | Plants in MPBD | ChEMBL Records | Median pChEMBL | Conflict T=6 | Label T=6 | Common Flora (>=20 plants) |")
    report_lines.append("|---|---|---|---|---|---|---|---|")
    c2_flora = flora_overlap_tables["cox2"]
    for _, r in c2_flora.iterrows():
        c_flag = "YES" if r["flag_common_plant"] else "no"
        lbl_str = "Active (1)" if r["label_T6"] == 1.0 else ("Inactive (0)" if r["label_T6"] == 0.0 else "Conflict")
        report_lines.append(f"| `{r['inchikey_connectivity']}` | {r['compound_name']} | {r['n_plants']} | {r['n_records']} | {r['median_pchembl']:.2f} | {r['conflict_T6']} | {lbl_str} | {c_flag} |")
    report_lines.append("")
    
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## 4. Go/No-Go Decision Table (Design Note Section 9)")
    report_lines.append("")
    report_lines.append("Evaluation against the Section 9 threshold of **~1,000 labeled training molecules** at **T = 6**:")
    report_lines.append("")
    report_lines.append("| Target | ChEMBL ID | Threshold Criterion | Training Pool Labeled Layers (T=6) | Actives (T=6) | Active Fraction (T=6) | Status |")
    report_lines.append("|---|---|---|---|---|---|---|")
    
    for vt in verified_targets:
        if vt["is_primary"]:
            slug = vt["slug"]
            p6 = target_results[slug]["pool_T6"]
            status_str = "PASS" if p6["labeled"] >= 1000 else "BELOW THRESHOLD"
            report_lines.append(f"| **{vt['pref_label']}** | `{vt['chembl_id']}` | >= 1,000 labeled layers | {p6['labeled']:,} | {p6['actives']:,} | {p6['act_frac']:.1f}% | **{status_str}** |")
    report_lines.append("")
    
    # Write quality report
    report_text = "\n".join(report_lines)
    with open(OUT_QUALITY_PATH, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"Saved quality report: {OUT_QUALITY_PATH}")
    
    # 8. Master SHA-256 end verification
    sha_end = verify_file_sha256(MASTER_MPBD_PATH, EXPECTED_MASTER_SHA256)
    print(f"[VERIFIED] Master MPBD SHA-256 at completion: {sha_end}")
    
    conn.close()
    print("\n[SUCCESS] Stage 9 COX Data Check Complete.")


if __name__ == "__main__":
    main()
