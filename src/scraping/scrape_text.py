import os
import sys
import pathlib

# Assure that we can import urls.py properly
sys.path.append(os.path.dirname(__file__))

from urls import URLS_MOORE, URLS_FRENCH
from jwsoup.text import scrape_multi_page

BASE_DIR = pathlib.Path(__file__).parent.parent.parent
OUTPUT_DIR_MOORE = BASE_DIR / "data" / "raw" / "parquet" / "moore"
OUTPUT_DIR_FRENCH = BASE_DIR / "data" / "raw" / "parquet" / "french"

def main():
    OUTPUT_DIR_MOORE.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR_FRENCH.mkdir(parents=True, exist_ok=True)
    
    print("=== Début du scraping Mooré ===")
    for book, url in URLS_MOORE.items():
        output_file = OUTPUT_DIR_MOORE / f"bible_complete_moore.parquet"
        print(f"Scraping {book} (Mooré) depuis {url}...")
        try:
            # page_sep est 'books' d'après l'URL
            scrape_multi_page(url, output_dir=str(output_file), max_pages=1200, page_sep="books")
            print(f"-> Succès: {output_file}")
        except Exception as e:
            print(f"Erreur pour {book}: {e}")

    print("\n=== Début du scraping Français ===")
    for book, url in URLS_FRENCH.items():
        output_file = OUTPUT_DIR_FRENCH / f"bible_complete_french.parquet"
        print(f"Scraping {book} (Français) depuis {url}...")
        try:
            # page_sep est 'livres' d'après l'URL française
            scrape_multi_page(url, output_dir=str(output_file), max_pages=1200, page_sep="livres")
            print(f"-> Succès: {output_file}")
        except Exception as e:
            print(f"Erreur pour {book}: {e}")

if __name__ == "__main__":
    main()
