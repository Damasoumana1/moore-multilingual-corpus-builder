
import os
import pathlib
import pandas as pd
from tqdm import tqdm

BASE_DIR = pathlib.Path(__file__).parent.parent.parent
AUDIO_RAW_DIR = BASE_DIR / "data" / "raw" / "audio" / "moore"
REPORT_PATH = BASE_DIR / "outputs" / "reports" / "audio_verification_report.txt"

def verify_audio_files():
    print("=" * 60)
    print("VÉRIFICATION DE L'INTÉGRITÉ DES AUDIOS")
    print("=" * 60)

    if not AUDIO_RAW_DIR.exists():
        print(f"✗ Erreur : Le dossier {AUDIO_RAW_DIR} n'existe pas.")
        return

    results = []
    total_files = 0
    corrupted_files = 0
    empty_files = 0

    books = [d for d in AUDIO_RAW_DIR.iterdir() if d.is_dir()]
    
    for book in tqdm(books, desc="Vérification des livres"):
        # On cherche les fichiers mp3 récursivement
        mp3_files = list(book.rglob("*.mp3"))
        
        for mp3 in mp3_files:
            total_files += 1
            file_size = mp3.stat().st_size
            
            is_ok = True
            status = "OK"
            
            if file_size == 0:
                empty_files += 1
                is_ok = False
                status = "VIDE"
            elif file_size < 1000: # Trop petit pour être un chapitre audio
                empty_files += 1
                is_ok = False
                status = "TROP PETIT"
                
            # Optionnel : On pourrait vérifier le header MP3 ici
            
            if not is_ok:
                corrupted_files += 1
                results.append(f"[{status}] {mp3.relative_to(AUDIO_RAW_DIR)}")

    # Création du rapport
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("RAPPORT DE VÉRIFICATION AUDIO\n")
        f.write("=" * 30 + "\n")
        f.write(f"Nombre total de fichiers trouvés : {total_files}\n")
        f.write(f"Fichiers corrompus/vides : {corrupted_files}\n")
        f.write(f"Détails des erreurs :\n")
        if not results:
            f.write("Aucune erreur détectée. Tous les fichiers sont valides.\n")
        else:
            for res in results:
                f.write(f"- {res}\n")

    print(f"\n[FIN] Vérification terminée.")
    print(f"Total : {total_files} fichiers.")
    print(f"Erreurs : {corrupted_files}")
    print(f"Rapport généré dans : {REPORT_PATH}")

if __name__ == "__main__":
    verify_audio_files()
