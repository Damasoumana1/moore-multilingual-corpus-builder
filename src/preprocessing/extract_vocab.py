"""
extract_vocab.py
----------------
Extrait le vocabulaire unique de chaque langue du corpus trilingue.
"""
import sys
import pandas as pd
import pathlib
import re
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = pathlib.Path(__file__).parent.parent.parent
TRANS_DIR = BASE_DIR / "data" / "translations"
VOCAB_DIR = BASE_DIR / "data" / "vocabulary"

def clean_and_tokenize(text):
    if not isinstance(text, str):
        return []
    # Retirer la ponctuation de base et mettre en minuscule
    text = text.lower()
    # On garde les caractères spéciaux du Mooré (ɩ, ʋ, ɛ, ɔ, etc.)
    tokens = re.findall(r'\b\w+\b', text, re.UNICODE)
    return tokens

def main():
    VOCAB_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("EXTRACTION DU VOCABULAIRE")
    print("=" * 60)

    # 1. Charger Mooré et Français depuis moore_fr.csv
    fr_path = TRANS_DIR / "moore_fr.csv"
    if fr_path.exists():
        print(f"\nTraitement de {fr_path.name}...")
        df_fr = pd.read_csv(fr_path)
        
        # Vocab Mooré
        moore_tokens = []
        for text in df_fr['moore_text']:
            moore_tokens.extend(clean_and_tokenize(text))
        moore_vocab = sorted(list(set(moore_tokens)))
        (VOCAB_DIR / "moore_vocab.txt").write_text('\n'.join(moore_vocab), encoding='utf-8')
        print(f"  ✓ Mooré : {len(moore_vocab):,} mots sauvés.")

        # Vocab Français
        fr_tokens = []
        for text in df_fr['french_text']:
            fr_tokens.extend(clean_and_tokenize(text))
        fr_vocab = sorted(list(set(fr_tokens)))
        (VOCAB_DIR / "french_vocab.txt").write_text('\n'.join(fr_vocab), encoding='utf-8')
        print(f"  ✓ Français : {len(fr_vocab):,} mots sauvés.")

    # 2. Charger Anglais depuis moore_en.csv
    en_path = TRANS_DIR / "moore_en.csv"
    if en_path.exists():
        print(f"\nTraitement de {en_path.name}...")
        df_en = pd.read_csv(en_path)
        
        # Vocab Anglais
        en_tokens = []
        for text in df_en['english_text']:
            en_tokens.extend(clean_and_tokenize(text))
        en_vocab = sorted(list(set(en_tokens)))
        (VOCAB_DIR / "english_vocab.txt").write_text('\n'.join(en_vocab), encoding='utf-8')
        print(f"  ✓ Anglais : {len(en_vocab):,} mots sauvés.")

    print("\n✅ Tous les fichiers de vocabulaire sont à jour dans data/vocabulary/")

if __name__ == "__main__":
    main()
