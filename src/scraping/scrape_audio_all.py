
import os
import sys
import pathlib
import time
import re
from urllib.parse import unquote

# Assure l'importation de urls.py
sys.path.append(os.path.dirname(__file__))
sys.stdout.reconfigure(encoding='utf-8')

from urls import URLS_MOORE
from jwsoup.audio import extract_mp3_link, download_audio

BASE_DIR = pathlib.Path(__file__).parent.parent.parent
AUDIO_RAW_DIR = BASE_DIR / "data" / "raw" / "audio" / "moore"

def get_info_from_url(url):
    """
    Extrait le slug du livre et le numéro du chapitre depuis l'URL JW.org.
    """
    decoded_url = unquote(url)
    # Cherche books/[slug]/[chapter]/
    match = re.search(r'books/([^/]+)/(\d+)/', decoded_url)
    if match:
        return match.group(1), match.group(2)
    return None, None

def scrape_book(book_name, start_url):
    """
    Scrape un livre entier en suivant les liens 'next_page'
    mais s'arrête si on change de livre (slug différent).
    """
    print(f"\n>>> DÉBUT DU LIVRE : {book_name.upper()}")
    current_url = start_url
    
    # Récupérer le slug attendu pour ce livre
    expected_slug, _ = get_info_from_url(start_url)
    if not expected_slug:
        print(f"    ⚠ Impossible de déterminer le slug pour {book_name}")
        return

    while current_url:
        slug, chapter_num = get_info_from_url(current_url)
        
        # Si on a changé de livre, on s'arrête
        if slug != expected_slug:
            print(f"    --- Fin du livre {book_name} (prochain slug: {slug})")
            break
            
        # Dossier de destination
        book_dir = AUDIO_RAW_DIR / book_name
        # On vérifie si le fichier existe déjà (format jwsoup: page_id.mp3 dans folder chapter_id)
        # Mais ici on vérifie juste le dossier du chapitre pour simplifier
        chap_dir = book_dir / str(chapter_num)
        if chap_dir.exists() and any(chap_dir.glob("*.mp3")):
            print(f"    - Chapitre {chapter_num} : Déjà présent.")
            # On doit quand même récupérer le lien suivant
            try:
                _, next_page = extract_mp3_link(current_url)
                current_url = next_page
                continue
            except:
                break

        print(f"    > Chapitre {chapter_num} : Téléchargement...")
        try:
            mp3_link, next_page = extract_mp3_link(current_url)
            
            if mp3_link:
                book_dir.mkdir(parents=True, exist_ok=True)
                download_audio(
                    mp3_link, 
                    output_dir=str(book_dir), 
                    chapter_id=str(chapter_num), 
                    page_id=book_name
                )
                print(f"      ✓ Succès")
            else:
                print(f"      ⚠ Pas d'audio.")

            current_url = next_page
            time.sleep(0.5)
            
        except Exception as e:
            print(f"      ✗ Erreur : {e}")
            break

def main():
    AUDIO_RAW_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("SCRAPER AUDIO BIBLE MOORÉ - VERSION ROBUSTE")
    print("=" * 60)

    for book_name, start_url in URLS_MOORE.items():
        # Optionnel : sauter ce qui est déjà fait (Genèse par exemple)
        # Mais scrape_book gère déjà les doublons.
        scrape_book(book_name, start_url)

    print("\n[FIN] Processus terminé.")

if __name__ == "__main__":
    main()
