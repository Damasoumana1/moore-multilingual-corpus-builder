import os
import sys
import pathlib
from jwsoup.audio.scraper import download_audios

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = pathlib.Path(__file__).parent.parent.parent
OUTPUT_DIR_MOORE = BASE_DIR / "data" / "raw" / "audio" / "moore" / "bible_complete"

def main():
    OUTPUT_DIR_MOORE.mkdir(parents=True, exist_ok=True)
    
    # URL de départ pour la Genèse (Sɩngre) en Mooré
    start_url = "https://www.jw.org/mos/d-s%E1%BA%BDn-yiisi/biible/nwt/books/S%C9%A9ngre/1/"
    
    print("=== Début du téléchargement des Audios (Mooré) ===")
    print(f"Dossier de destination : {OUTPUT_DIR_MOORE}")
    
    try:
        # La librairie jwsoup va gérer la pagination jusqu'à max_pages
        download_audios(start_url, output_dir=str(OUTPUT_DIR_MOORE), max_pages=1200)
        print("\n-> Téléchargement terminé avec succès !")
    except Exception as e:
        print(f"\nErreur lors du téléchargement : {e}")

if __name__ == "__main__":
    main()
