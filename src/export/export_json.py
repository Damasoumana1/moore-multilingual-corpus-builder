"""
export_json.py
--------------
Exporte le corpus Mooré–Français en formats prêts pour le fine-tuning :
  1. JSON Lines (format HuggingFace datasets)
  2. JSON structuré complet
  3. Format instruction (pour LLM fine-tuning)

Usage:
    python src/export/export_json.py [--input PATH] [--output-dir DIR]
"""
import sys
import json
import pathlib
import argparse
import pandas as pd
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR     = pathlib.Path(__file__).parent.parent.parent
DEFAULT_IN   = BASE_DIR / "data" / "processed" / "clean_text" / "parallel_corpus_clean.csv"
DEFAULT_OUT  = BASE_DIR / "data" / "processed"

# ── Templates d'instructions pour LLM fine-tuning ──────────────
INSTRUCTION_TEMPLATES = [
    {
        "instruction": "Traduis ce texte Mooré en français.",
        "input_key": "moore_text",
        "output_key": "french_text",
        "name": "moore_to_french"
    },
    {
        "instruction": "Traduis ce texte français en Mooré.",
        "input_key": "french_text",
        "output_key": "moore_text",
        "name": "french_to_moore"
    },
]


def to_jsonl(df: pd.DataFrame, path: pathlib.Path):
    """Format HuggingFace : un JSON par ligne."""
    with open(path, 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            record = {
                "id":          row['verse_id'],
                "moore":       row['moore_text'],
                "french":      row['french_text'],
                "source":      "JW.org / Bible NWT",
                "language_pair": "mos-fr"
            }
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    print(f"  ✓ JSONL             : {path} ({len(df):,} lignes)")


def to_instruction_jsonl(df: pd.DataFrame, out_dir: pathlib.Path):
    """Format instruction/output pour Alpaca-style fine-tuning."""
    for tmpl in INSTRUCTION_TEMPLATES:
        path = out_dir / f"finetune_{tmpl['name']}.jsonl"
        with open(path, 'w', encoding='utf-8') as f:
            for _, row in df.iterrows():
                record = {
                    "instruction": tmpl['instruction'],
                    "input":       row[tmpl['input_key']],
                    "output":      row[tmpl['output_key']],
                    "id":          row['verse_id']
                }
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        print(f"  ✓ Fine-tune JSONL   : {path} ({len(df):,} exemples)")


def to_json_full(df: pd.DataFrame, path: pathlib.Path):
    """JSON structuré complet avec métadonnées."""
    metadata = {
        "name":            "moore-french-bible-corpus",
        "description":     "Corpus parallèle Mooré–Français extrait de la Bible NWT (JW.org)",
        "language_source": "mos",   # ISO 639-3 Mooré
        "language_target": "fr",
        "source":          "JW.org",
        "license":         "Educational use only",
        "created_at":      datetime.utcnow().isoformat() + "Z",
        "total_pairs":     len(df),
        "books_covered":   df['verse_id'].str[1:4].nunique(),
    }
    output = {
        "metadata": metadata,
        "data": df[['verse_id', 'moore_text', 'french_text']].to_dict(orient='records')
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"  ✓ JSON complet      : {path} ({len(df):,} entrées)")


def main(input_path=None, output_dir=None):
    inp = pathlib.Path(input_path) if input_path else DEFAULT_IN
    out = pathlib.Path(output_dir) if output_dir else DEFAULT_OUT
    out.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("EXPORT DU CORPUS — Formats HuggingFace & Fine-tuning")
    print("=" * 60)

    df = pd.read_csv(inp, encoding='utf-8')
    print(f"  Corpus chargé : {len(df):,} paires Mooré–Français\n")

    # 1. JSONL brut (HuggingFace)
    to_jsonl(df, out / "parallel_corpus.jsonl")

    # 2. JSON complet avec métadonnées
    to_json_full(df, out / "parallel_corpus_full.json")

    # 3. Format instruction (bidirectionnel)
    to_instruction_jsonl(df, out)

    print(f"\n✅ Export terminé ! Fichiers dans : {out}")
    print(f"\n   Prochaine étape → python src/preprocessing/split_dataset.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input',      default=None)
    parser.add_argument('--output-dir', default=None)
    args = parser.parse_args()
    main(args.input, args.output_dir)
