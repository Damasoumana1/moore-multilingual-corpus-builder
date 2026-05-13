"""
scrape_english.py
-----------------
Scrape the entire English Bible (NWT) from JW.org.
"""
import os
import sys
import pathlib

sys.path.append(os.path.dirname(__file__))
sys.stdout.reconfigure(encoding='utf-8')

from urls import URLS_ENGLISH
from jwsoup.text import scrape_multi_page

BASE_DIR = pathlib.Path(__file__).parent.parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "raw" / "parquet" / "english" / "bible_complete_english.parquet"

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("SCRAPING BIBLE COMPLÈTE — ANGLAIS")
    print("=" * 60)
    
    for book, url in URLS_ENGLISH.items():
        print(f"\n→ {book} : {url}")
        try:
            scrape_multi_page(
                url,
                output_dir=str(OUTPUT_DIR),
                max_pages=500,
                page_sep="books"
            )
            print(f"  ✓ Succès")
        except Exception as e:
            print(f"  ✗ Erreur : {e}")

    print("\n✅ Scraping Anglais terminé !")

if __name__ == "__main__":
    main()
