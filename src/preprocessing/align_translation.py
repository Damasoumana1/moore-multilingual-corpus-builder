import sys
import os
import pathlib
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd

BASE_DIR = pathlib.Path(__file__).parent.parent.parent
RAW_DIR = BASE_DIR / "data" / "raw" / "parquet"
TRANS_DIR = BASE_DIR / "data" / "translations"

def main():
    moore_path = RAW_DIR / "moore" / "genese_moore.parquet"
    french_path = RAW_DIR / "french" / "genese_french.parquet"
    output_path = TRANS_DIR / "parallel_corpus.csv"

    print("Chargement des fichiers Parquet...")
    # Read the dataframes
    df_moore = pd.read_parquet(moore_path)
    df_french = pd.read_parquet(french_path)

    # Keep only verse_id and verse_text
    df_moore = df_moore[['verse_id', 'verse_text']].rename(columns={'verse_text': 'moore_text'})
    df_french = df_french[['verse_id', 'verse_text']].rename(columns={'verse_text': 'french_text'})

    print("Alignement en cours...")
    # Merge on verse_id using an inner join to only keep paired verses
    aligned_df = pd.merge(df_moore, df_french, on='verse_id', how='inner')
    
    # Sort by verse_id for chronological reading (v1001001, v1001002...)
    aligned_df = aligned_df.sort_values(by='verse_id')
    
    # Export to CSV
    TRANS_DIR.mkdir(parents=True, exist_ok=True)
    aligned_df.to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"Alignement terminé ! {len(aligned_df)} versets alignés avec succès.")
    print(f"Fichier exporté vers : {output_path}")

    # Display the first 3 rows as verification
    print("\nAperçu des 3 premiers versets :")
    for _, row in aligned_df.head(3).iterrows():
        print(f"[{row['verse_id']}]")
        print(f"Mooré   : {row['moore_text']}")
        print(f"Français: {row['french_text']}")
        print("-" * 50)

if __name__ == "__main__":
    main()
