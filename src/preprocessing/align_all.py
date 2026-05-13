"""
align_all.py
------------
Consolide tous les fichiers Parquet (Bible complète, 66 livres)
et produit un CSV aligné Mooré–Français prêt pour le fine-tuning.

Usage:
    python src/preprocessing/align_all.py
"""
import sys
import pathlib
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR      = pathlib.Path(__file__).parent.parent.parent
MOORE_DIR     = BASE_DIR / "data" / "raw" / "parquet" / "moore"  / "bible_complete_moore.parquet"
FRENCH_DIR    = BASE_DIR / "data" / "raw" / "parquet" / "french" / "bible_complete_french.parquet"
ENGLISH_DIR   = BASE_DIR / "data" / "raw" / "parquet" / "english" / "bible_complete_english.parquet"
TRANS_DIR     = BASE_DIR / "data" / "translations"
OUTPUT_FR_PATH = TRANS_DIR / "moore_fr.csv"
OUTPUT_EN_PATH = TRANS_DIR / "moore_en.csv"

def load_all_parquets(parquet_root: pathlib.Path, lang: str) -> pd.DataFrame:
    """Charge et concatène tous les fichiers .parquet d'un dossier partitionné."""
    if not parquet_root.exists():
        print(f"  [!] Dossier {parquet_root} introuvable.")
        return pd.DataFrame(columns=['verse_id', 'verse_text'])

    files = list(parquet_root.rglob("*.parquet"))
    if not files:
        print(f"  [!] Aucun fichier parquet trouvé dans {parquet_root}")
        return pd.DataFrame(columns=['verse_id', 'verse_text'])

    print(f"  [{lang}] {len(files)} fichiers parquet trouvés...")
    dfs = []
    for f in files:
        try:
            df = pd.read_parquet(f)
            if 'verse_id' in df.columns and 'verse_text' in df.columns:
                dfs.append(df[['verse_id', 'verse_text']])
        except:
            continue

    if not dfs:
        return pd.DataFrame(columns=['verse_id', 'verse_text'])

    result = pd.concat(dfs, ignore_index=True)
    result = result.drop_duplicates(subset='verse_id', keep='first')
    print(f"  [{lang}] {len(result)} versets uniques chargés.")
    return result


def main():
    TRANS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("ALIGNEMENT TRILINGUE — Bible entière")
    print("=" * 60)

    print("\n[1/5] Chargement des versets Mooré...")
    df_moore = load_all_parquets(MOORE_DIR, "Mooré")
    df_moore = df_moore.rename(columns={'verse_text': 'moore_text'})

    print("\n[2/5] Chargement des versets Français...")
    df_french = load_all_parquets(FRENCH_DIR, "Français")
    df_french = df_french.rename(columns={'verse_text': 'french_text'})

    print("\n[3/5] Chargement des versets Anglais...")
    df_english = load_all_parquets(ENGLISH_DIR, "Anglais")
    df_english = df_english.rename(columns={'verse_text': 'english_text'})

    # --- Alignement Mooré-Français ---
    print("\n[4/5] Alignement Mooré-Français...")
    aligned_fr = pd.merge(df_moore, df_french, on='verse_id', how='inner')
    aligned_fr = aligned_fr.sort_values('verse_id').reset_index(drop=True)
    aligned_fr.to_csv(OUTPUT_FR_PATH, index=False, encoding='utf-8')
    print(f"  ✓ Sauvegardé : {OUTPUT_FR_PATH} ({len(aligned_fr)} paires)")

    # --- Alignement Mooré-Anglais ---
    print("\n[5/5] Alignement Mooré-Anglais...")
    if not df_english.empty:
        aligned_en = pd.merge(df_moore, df_english, on='verse_id', how='inner')
        aligned_en = aligned_en.sort_values('verse_id').reset_index(drop=True)
        aligned_en.to_csv(OUTPUT_EN_PATH, index=False, encoding='utf-8')
        print(f"  ✓ Sauvegardé : {OUTPUT_EN_PATH} ({len(aligned_en)} paires)")
    else:
        print("  ⚠ Données Anglais manquantes, moore_en.csv non généré.")

    print("\n✅ Alignement terminé !")
    return True


if __name__ == "__main__":
    main()
