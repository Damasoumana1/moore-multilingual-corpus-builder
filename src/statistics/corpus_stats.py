import os
import sys
import pathlib
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = pathlib.Path(__file__).parent.parent.parent
INPUT_PATH = BASE_DIR / "data" / "processed" / "clean_text" / "parallel_corpus_clean.csv"
REPORT_PATH = BASE_DIR / "outputs" / "reports" / "dataset_report.txt"
PLOT_PATH = BASE_DIR / "outputs" / "plots" / "word_frequency.png"

def get_word_stats(texts):
    all_words = []
    for text in texts:
        if isinstance(text, str):
            # Split by whitespace and remove simple punctuation
            words = [w.strip('.,!?;:"\'()[]{}') for w in text.lower().split()]
            all_words.extend([w for w in words if w])
    
    word_count = len(all_words)
    vocab_size = len(set(all_words))
    most_common = Counter(all_words).most_common(10)
    
    return word_count, vocab_size, most_common

def main():
    print("Chargement des données...")
    df = pd.read_csv(INPUT_PATH)
    
    total_verses = len(df)
    
    print("Calcul des statistiques Mooré...")
    moore_words, moore_vocab, moore_common = get_word_stats(df['moore_text'])
    moore_avg_length = moore_words / total_verses if total_verses > 0 else 0
    
    print("Calcul des statistiques Français...")
    french_words, french_vocab, french_common = get_word_stats(df['french_text'])
    french_avg_length = french_words / total_verses if total_verses > 0 else 0
    
    # 1. Génération du Rapport Texte
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = f"""RAPPORT STATISTIQUE DU CORPUS (Genèse)
========================================

1. INFORMATIONS GÉNÉRALES
-------------------------
Nombre total de versets alignés : {total_verses}

2. STATISTIQUES MOORÉ
---------------------
Nombre total de mots        : {moore_words}
Taille du vocabulaire unique: {moore_vocab}
Longueur moyenne par verset : {moore_avg_length:.1f} mots
Mots les plus fréquents     :
"""
    for word, count in moore_common:
        report += f"  - {word}: {count}\n"
        
    report += f"""
3. STATISTIQUES FRANÇAIS
------------------------
Nombre total de mots        : {french_words}
Taille du vocabulaire unique: {french_vocab}
Longueur moyenne par verset : {french_avg_length:.1f} mots
Mots les plus fréquents     :
"""
    for word, count in french_common:
        report += f"  - {word}: {count}\n"

    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Rapport sauvegardé : {REPORT_PATH}")

    # 2. Génération du Graphique (Fréquence Mooré)
    PLOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    words = [w[0] for w in moore_common]
    counts = [w[1] for w in moore_common]
    
    plt.figure(figsize=(10, 6))
    plt.bar(words, counts, color='skyblue')
    plt.title('Top 10 des mots les plus fréquents en Mooré (Livre de la Genèse)')
    plt.xlabel('Mots')
    plt.ylabel('Fréquence')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(PLOT_PATH)
    print(f"Graphique sauvegardé : {PLOT_PATH}")

if __name__ == "__main__":
    main()
