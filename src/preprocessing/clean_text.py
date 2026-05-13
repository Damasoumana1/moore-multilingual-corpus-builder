"""
clean_text.py
-------------
Nettoyage du corpus aligné :
  - Suppression des espaces superflus
  - Normalisation des guillemets (« » → standard)
  - Retrait des numéros de versets parasites
  - Filtrage des lignes trop courtes / trop longues
  - Déduplication

Usage:
    python src/preprocessing/clean_text.py [--input PATH] [--output PATH]
"""
import sys
import re
import pathlib
import argparse
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR    = pathlib.Path(__file__).parent.parent.parent
DEFAULT_IN  = BASE_DIR / "data" / "translations" / "parallel_corpus_full.csv"
DEFAULT_OUT = BASE_DIR / "data" / "processed" / "clean_text" / "parallel_corpus_clean.csv"

# ── Paramètres de filtrage ──────────────────────────────────────
MIN_WORDS = 2    # versets trop courts ignorés
MAX_WORDS = 300  # versets anormalement longs ignorés


def normalize(text: str) -> str:
    """Nettoyage d'un verset texte."""
    if not isinstance(text, str):
        return ""
    # Supprimer les espaces insécables et whitespace multiple
    text = text.replace('\u00a0', ' ').replace('\u202f', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    # Normaliser les guillemets typographiques → ASCII
    text = text.replace('«', '"').replace('»', '"')
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    # Supprimer des numéros de versets en début de ligne (ex: "1 Au commencement")
    # déjà gérés par le scraper, mais au cas où :
    text = re.sub(r'^\d+\s+', '', text)
    return text


def is_valid(moore: str, french: str) -> bool:
    """Filtre qualité : garde les paires valides."""
    mw = len(moore.split())
    fw = len(french.split())
    if mw < MIN_WORDS or fw < MIN_WORDS:
        return False
    if mw > MAX_WORDS or fw > MAX_WORDS:
        return False
    # Ratio longueur : on rejette les paires très déséquilibrées (>5:1)
    ratio = max(mw, fw) / max(min(mw, fw), 1)
    if ratio > 5:
        return False
    return True


def main(input_path=None, output_path=None):
    inp = pathlib.Path(input_path) if input_path else DEFAULT_IN
    out = pathlib.Path(output_path) if output_path else DEFAULT_OUT
    out.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("NETTOYAGE DU CORPUS ALIGNÉ")
    print("=" * 60)
    print(f"  Source  : {inp}")
    print(f"  Sortie  : {out}")

    df = pd.read_csv(inp, encoding='utf-8')
    n_raw = len(df)
    print(f"\n  Versets bruts        : {n_raw:,}")

    # Nettoyage textuel
    df['moore_text']  = df['moore_text'].apply(normalize)
    df['french_text'] = df['french_text'].apply(normalize)

    # Filtrage qualité
    mask = df.apply(lambda r: is_valid(r['moore_text'], r['french_text']), axis=1)
    df = df[mask].copy()
    n_filtered = len(df)
    print(f"  Après filtrage       : {n_filtered:,} ({n_raw - n_filtered} retirés)")

    # Déduplication
    df = df.drop_duplicates(subset=['verse_id']).copy()
    n_dedup = len(df)
    print(f"  Après déduplication  : {n_dedup:,} ({n_filtered - n_dedup} doublons retirés)")

    # Tri canonique
    df = df.sort_values('verse_id').reset_index(drop=True)

    df.to_csv(out, index=False, encoding='utf-8')
    print(f"\n✅ Corpus propre sauvegardé : {out}")
    print(f"   {n_dedup:,} paires Mooré–Français prêtes pour le fine-tuning")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input',  default=None)
    parser.add_argument('--output', default=None)
    args = parser.parse_args()
    main(args.input, args.output)
