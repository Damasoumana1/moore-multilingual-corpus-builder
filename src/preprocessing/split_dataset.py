import sys
import pathlib
import argparse
import pandas as pd
import json
from sklearn.model_selection import train_test_split

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR    = pathlib.Path(__file__).parent.parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

TRAIN_RATIO = 0.80
VAL_RATIO   = 0.10
TEST_RATIO  = 0.10
RANDOM_SEED = 42

def save_split(df: pd.DataFrame, name: str, split_root: pathlib.Path, pair_name: str):
    """Sauvegarde les splits en CSV et JSONL."""
    path = split_root / name
    path.mkdir(parents=True, exist_ok=True)
    
    csv_path  = path / f"{name}_{pair_name}.csv"
    jsonl_path = path / f"{name}_{pair_name}.jsonl"

    df.to_csv(csv_path, index=False, encoding='utf-8')

    # Colonnes dynamiques (verse_id + les autres)
    cols = [c for c in df.columns if c != 'verse_id']
    
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            entry = {"id": row['verse_id']}
            for col in cols:
                # Retirer le préfixe de langue pour le JSON (ex: moore_text -> moore)
                key = col.replace('_text', '')
                entry[key] = row[col]
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    print(f"  [{name.upper():>10}] {len(df):>6,} paires  →  {csv_path.name}")

def process_file(input_path: pathlib.Path, pair_name: str, ratios: list):
    t, v, te = ratios
    print(f"\n--- Traitement de {pair_name} ({input_path.name}) ---")
    
    if not input_path.exists():
        print(f"  [!] Fichier {input_path} introuvable. Passage.")
        return

    df = pd.read_csv(input_path, encoding='utf-8')
    n = len(df)
    
    # Split 1 : train vs (val + test)
    df_train, df_temp = train_test_split(
        df, test_size=(v + te),
        random_state=RANDOM_SEED, shuffle=True
    )

    # Split 2 : val vs test
    relative_test = te / (v + te)
    df_val, df_test = train_test_split(
        df_temp, test_size=relative_test,
        random_state=RANDOM_SEED
    )

    split_root = PROCESSED_DIR / pair_name
    save_split(df_train, "train",      split_root, pair_name)
    save_split(df_val,   "validation", split_root, pair_name)
    save_split(df_test,  "test",       split_root, pair_name)
    
    print(f"  ✓ {pair_name} terminé.")

def main(ratio=None):
    if ratio is None:
        ratio = [0.8, 0.1, 0.1]

    print("=" * 60)
    print("GÉNÉRATION DES SPLITS (Multi-langues)")
    print("=" * 60)

    # 1. Mooré-Français
    process_file(
        BASE_DIR / "data" / "translations" / "moore_fr.csv",
        "moore_fr",
        ratio
    )

    # 2. Mooré-Anglais
    process_file(
        BASE_DIR / "data" / "translations" / "moore_en.csv",
        "moore_en",
        ratio
    )

    print("\n✅ Tous les splits ont été générés dans data/processed/")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ratio', nargs=3, type=float, default=[0.8, 0.1, 0.1])
    args = parser.parse_args()
    main(args.ratio)
