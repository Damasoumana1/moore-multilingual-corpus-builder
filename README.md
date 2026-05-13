# Moore Corpus Builder 🇧🇫

Un pipeline complet de collecte, d'alignement et de traitement de données pour la création d'un corpus trilingue (Mooré, Français, Anglais) destiné à l'intelligence artificielle (Traduction automatique, ASR, TTS).

## 🚀 Fonctionnalités

- **Scraping Multi-langues** : Téléchargement automatisé des textes bibliques depuis JW.org en Mooré, Français et Anglais.
- **Alignement Trilingue** : Alignement automatique des versets entre les trois langues pour créer des paires de traduction précises.
- **Traitement Audio** : 
    - Téléchargement automatisé de l'audio de la Bible en Mooré.
    - Rééchantillonnage automatique en **16kHz, mono, WAV (PCM 16-bit)**, format standard pour les modèles ASR (Whisper, Wav2Vec2).
- **Indexation Multimodale** : Création d'un index liant chaque chapitre audio à ses textes correspondants en 3 langues.
- **Exportation flexible** : Génération de fichiers CSV et JSONL prêts pour l'entraînement (HuggingFace, OpenNMT, etc.).
- **Analyse Lexicale** : Extraction automatique du vocabulaire unique pour chaque langue.

## 📊 Statistiques du Corpus

Basé sur la version complète de la Bible (66 livres) :
- **Versets alignés** : ~31 000 (Mooré-Français et Mooré-Anglais).
- **Données Audio** : 1 160 fichiers (environ 88 heures de parole).
- **Vocabulaire Mooré** : ~31 000 mots uniques.

## 📁 Structure du Projet

```text
moore_corpus_builder/
├── data/
│   ├── raw/               # Données brutes (Parquet, MP3)
│   ├── processed/         # Données nettoyées (WAV, JSONL)
│   ├── translations/      # Fichiers CSV alignés
│   └── vocabulary/        # Listes de mots uniques
├── src/
│   ├── scraping/          # Scripts de collecte (Texte & Audio)
│   ├── preprocessing/     # Alignement, Nettoyage, Vocabulaire
│   ├── audio/             # Traitement audio et Indexation
│   └── export/            # Conversion de formats
├── outputs/
│   └── reports/           # Rapports statistiques finaux
├── main.py                # Point d'entrée du pipeline
└── requirements.txt       # Dépendances Python
```

## 🛠️ Installation

1. Cloner le dépôt.
2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. (Optionnel) Installer FFmpeg sur votre système pour le traitement audio.

## 🚀 Utilisation

Le projet est piloté par un script central `main.py` qui orchestre toutes les étapes :

```bash
# Lancer le pipeline complet
python main.py --from scrape

# Lancer uniquement le traitement audio et l'indexation
python main.py --from audio

# Générer les statistiques finales
python main.py --from stats
```

## 📄 Formats de sortie

- **Texte** : `data/processed/finetune_french_to_moore.jsonl` (Format instruction pour LLM)
- **Audio** : `data/processed/audio/moore/` (Fichiers .wav)
- **Index** : `data/processed/audio_multilingual_index.jsonl` (Lien Audio <-> Texte 3 langues)

## ⚖️ Source des données
Toutes les données (textes et audios) utilisées dans ce projet proviennent du site **JW.ORG**. 
- **Textes** : *Traduction du monde nouveau* (New World Translation) en Mooré, Français et Anglais.
- **Audios** : Enregistrements audio officiels de la Bible en Mooré disponibles sur la même plateforme.

Ce projet est strictement destiné à un usage éducatif, linguistique et de recherche pour le développement d'outils d'intelligence artificielle pour la langue Mooré.

## 👨‍💻 Contributeur Principal

**Soumana Dama**  
Software Engineer | Fullstack Web & Mobile Developer | AI and Data Engineer 💻🚀  
- [LinkedIn](https://www.linkedin.com/in/soumana-dama-445096253/)
- [Portfolio](https://soumanadama.netlify.app/)
