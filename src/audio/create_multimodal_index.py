import pandas as pd
import pathlib
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Configuration des chemins
BASE_DIR = pathlib.Path(__file__).parent.parent.parent
TRANS_DIR = BASE_DIR / "data" / "translations"
AUDIO_DIR = BASE_DIR / "data" / "processed" / "audio" / "moore"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "audio_multilingual_index.jsonl"

# Mapping des livres (Ordre standard de la Bible)
BIBLE_BOOKS = [
    "genese", "exode", "levitique", "nombres", "deuteronome", "josue", "juges", "rut",
    "1-samuel", "2-samuel", "1-rois", "2-rois", "1-chroniques", "2-chroniques", "esdras",
    "nehemie", "esther", "job", "psaumes", "proverbes", "ecclesiaste", "cantique",
    "isaie", "jeremie", "lamentations", "ezechiel", "daniel", "osee", "joel", "amos",
    "abdias", "jonas", "michee", "nahum", "habacuc", "sophonie", "aggee", "zacharie", "malachie",
    "matthieu", "marc", "luc", "jean", "actes", "romains", "1-corinthiens", "2-corinthiens",
    "galates", "ephesiens", "philippiens", "colossiens", "1-thessaloniciens", "2-thessaloniciens",
    "1-timothee", "2-timothee", "tite", "philemon", "hebreux", "jacques", "1-pierre", "2-pierre",
    "1-jean", "2-jean", "3-jean", "jude", "apocalypse"
]

BOOK_TO_ID = {name: i+1 for i, name in enumerate(BIBLE_BOOKS)}

def parse_id(verse_id):
    """
    Parse vBCCVVV id format.
    Example: v10001001 -> book 10, chapter 1, verse 1
    """
    try:
        # On enlève le 'v'
        num = verse_id[1:]
        # Les 2 premiers chiffres: livre
        # Les 3 suivants: chapitre
        # Les 3 suivants: verset
        # Note: si le livre a un seul chiffre (1-9), il est sur 2 positions (01-09)
        book_id = int(num[:-6])
        chapter_id = int(num[-6:-3])
        verse_id_num = int(num[-3:])
        return book_id, chapter_id, verse_id_num
    except:
        return None, None, None

def main():
    print("🚀 Création de l'index multimodal (Audio + Trilingue)...")
    
    # 1. Charger les données textuelles
    fr_path = TRANS_DIR / "moore_fr.csv"
    en_path = TRANS_DIR / "moore_en.csv"
    
    if not fr_path.exists():
        print(f"❌ Erreur: {fr_path} introuvable.")
        return

    df_fr = pd.read_csv(fr_path)
    df_en = pd.read_csv(en_path) if en_path.exists() else pd.DataFrame()

    # Fusionner pour avoir les 3 langues (Moore, Fr, En)
    if not df_en.empty:
        df_all = pd.merge(df_fr, df_en[['verse_id', 'english_text']], on='verse_id', how='left')
    else:
        df_all = df_fr
        df_all['english_text'] = ""

    # 2. Extraire livre et chapitre de verse_id
    print("📦 Groupement des versets par chapitre...")
    df_all['book_id'], df_all['chapter_id'], df_all['verse_num'] = zip(*df_all['verse_id'].apply(parse_id))
    
    # 3. Grouper par chapitre
    chapters = df_all.groupby(['book_id', 'chapter_id'])
    
    # 4. Faire correspondre avec les fichiers audio
    index_data = []
    
    # On crée un mapping inverse ID -> Nom du livre pour chercher l'audio
    ID_TO_BOOK = {v: k for k, v in BOOK_TO_ID.items()}

    for (b_id, c_id), group in chapters:
        book_name = ID_TO_BOOK.get(b_id)
        if not book_name: continue
        
        # Chemin potentiel de l'audio
        # Structure: data/raw/audio/moore/[book]/[chapter]/page_[book].mp3
        audio_subpath = pathlib.Path(book_name) / str(c_id) / f"page_{book_name}.wav"
        audio_full_path = AUDIO_DIR / audio_subpath
        
        if audio_full_path.exists():
            # Trier les versets pour reconstruire le texte dans l'ordre
            group = group.sort_values('verse_num')
            
            chapter_text_moore = " ".join(group['moore_text'].fillna("").astype(str))
            chapter_text_french = " ".join(group['french_text'].fillna("").astype(str))
            chapter_text_english = " ".join(group['english_text'].fillna("").astype(str))
            
            entry = {
                "id": f"b{b_id:02d}_c{c_id:03d}",
                "book": book_name,
                "chapter": int(c_id),
                "audio_path": str(audio_full_path.relative_to(BASE_DIR)).replace("\\", "/"),
                "text_moore": chapter_text_moore.strip(),
                "text_french": chapter_text_french.strip(),
                "text_english": chapter_text_english.strip()
            }
            index_data.append(entry)

    # 5. Sauvegarder
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for entry in index_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            
    print(f"✅ Index créé avec succès : {len(index_data)} chapitres indexés.")
    print(f"📂 Fichier : {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
