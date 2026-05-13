"""
main.py — Pipeline complet Moore Corpus Builder (Trilingue)
==========================================================
Orchestre toutes les étapes pour Mooré, Français et Anglais.
"""
import sys
import time
import argparse
import pathlib

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = pathlib.Path(__file__).parent
STEPS = ["scrape", "align", "split", "vocab", "audio", "stats"]

def step_vocab():
    banner("ÉTAPE 4/6 — Extraction du Vocabulaire")
    from src.preprocessing.extract_vocab import main as extract_vocab
    extract_vocab()

def step_audio():
    banner("ÉTAPE 5/6 — Traitement Audio (Rééchantillonnage)")
    from src.audio.resample_audio import main as resample
    resample()
    banner("ÉTAPE 5b — Création de l'index Multimodal")
    from src.audio.create_multimodal_index import main as create_index
    create_index()

def banner(title: str):
    print("\n" + "═" * 60)
    print(f"  {title}")
    print("═" * 60)

def step_scrape():
    banner("ÉTAPE 1/4 — Scraping complet (Mooré, FR, EN)")
    from src.scraping.scrape_missing import main as scrape_missing
    scrape_missing()
    from src.scraping.scrape_english import main as scrape_en
    scrape_en()

def step_align():
    banner("ÉTAPE 2/4 — Alignement Trilingue (66 livres)")
    from src.preprocessing.align_all import main as align
    return align()

def step_split():
    banner("ÉTAPE 3/4 — Split multi-langues (Train/Val/Test)")
    from src.preprocessing.split_dataset import main as split
    split()

def step_stats():
    banner("RAPPORT FINAL DU PROJET")
    import pandas as pd
    import json
    
    report_lines = ["RAPPORT FINAL DU PROJET : MOORE CORPUS BUILDER", "=" * 48, ""]
    
    # 1. Stats Textuelles
    pairs = [
        ("moore_fr", "data/translations/moore_fr.csv"),
        ("moore_en", "data/translations/moore_en.csv")
    ]
    report_lines += ["--- SECTION 1 : CORPUS PARALLÈLE ---"]
    for name, path_rel in pairs:
        path = BASE_DIR / path_rel
        if path.exists():
            df = pd.read_csv(path)
            lang2 = name.split('_')[1]
            lang2_col = 'french_text' if lang2 == 'fr' else 'english_text'
            report_lines += [
                f"Paire : {name.upper()}",
                f"  Versets alignés           : {len(df):,}",
                f"  Mots uniques Mooré        : {len(set(' '.join(df['moore_text'].astype(str)).split())):,}",
                f"  Mots uniques cible ({lang2.upper()}) : {len(set(' '.join(df[lang2_col].astype(str)).split())):,}",
                ""
            ]
            
    # 2. Stats Audio
    report_lines += ["--- SECTION 2 : CORPUS MULTIMODAL ---"]
    index_path = BASE_DIR / "data" / "processed" / "audio_multilingual_index.jsonl"
    if index_path.exists():
        entries = []
        with open(index_path, 'r', encoding='utf-8') as f:
            for line in f:
                entries.append(json.loads(line))
        
        total_chapters = len(entries)
        # On pourrait calculer la durée ici si on l'avait stockée dans l'index
        report_lines += [
            f"Chapitres avec audio et texte trilingue : {total_chapters:,}",
            f"Dossier audio traité : data/processed/audio/moore",
            f"Fichier d'index      : data/processed/audio_multilingual_index.jsonl",
            ""
        ]
    
    report = '\n'.join(report_lines)
    print(report)
    report_path = BASE_DIR / "outputs" / "reports" / "final_report.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding='utf-8')
    print(f"\n  ✓ Rapport final sauvegardé : {report_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scrape', action='store_true')
    parser.add_argument('--from', dest='from_step', default='align', choices=STEPS)
    args = parser.parse_args()

    start = time.time()
    from_idx = STEPS.index(args.from_step)

    if args.scrape or from_idx <= STEPS.index("scrape"):
        step_scrape()
    if from_idx <= STEPS.index("align"):
        step_align()
    if from_idx <= STEPS.index("split"):
        step_split()
    if from_idx <= STEPS.index("vocab"):
        step_vocab()
    if from_idx <= STEPS.index("audio"):
        step_audio()
    step_stats()

    print(f"\nPipeline terminé en {time.time() - start:.1f}s")

if __name__ == "__main__":
    main()
