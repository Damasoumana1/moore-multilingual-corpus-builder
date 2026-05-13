"""
scrape_missing.py
-----------------
Scrape uniquement les 8 livres manquants de la Bible (Mooré + Français).
Les 58 autres sont déjà en cache dans bible_complete_moore/french.parquet.
"""
import os
import sys
import pathlib

sys.path.append(os.path.dirname(__file__))
sys.stdout.reconfigure(encoding='utf-8')

from urls import URLS_MOORE_MISSING, URLS_FRENCH_MISSING
from jwsoup.text import scrape_multi_page

BASE_DIR = pathlib.Path(__file__).parent.parent.parent
OUTPUT_DIR_MOORE  = BASE_DIR / "data" / "raw" / "parquet" / "moore"  / "bible_complete_moore.parquet"
OUTPUT_DIR_FRENCH = BASE_DIR / "data" / "raw" / "parquet" / "french" / "bible_complete_french.parquet"

def main():
    OUTPUT_DIR_MOORE.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR_FRENCH.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("SCRAPING DES 8 LIVRES MANQUANTS — MOORÉ")
    print("=" * 60)
    for book, url in URLS_MOORE_MISSING.items():
        print(f"\n→ {book} : {url}")
        try:
            scrape_multi_page(
                url,
                output_dir=str(OUTPUT_DIR_MOORE),
                max_pages=500,
                page_sep="books"
            )
            print(f"  ✓ Succès")
        except Exception as e:
            print(f"  ✗ Erreur : {e}")

    print("\n" + "=" * 60)
    print("SCRAPING DES 8 LIVRES MANQUANTS — FRANÇAIS")
    print("=" * 60)
    for book, url in URLS_FRENCH_MISSING.items():
        print(f"\n→ {book} : {url}")
        try:
            scrape_multi_page(
                url,
                output_dir=str(OUTPUT_DIR_FRENCH),
                max_pages=500,
                page_sep="livres"
            )
            print(f"  ✓ Succès")
        except Exception as e:
            print(f"  ✗ Erreur : {e}")

    print("\n✅ Scraping des livres manquants terminé !")

if __name__ == "__main__":
    main()
