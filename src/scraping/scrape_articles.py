import os
import sys
import json
import pathlib
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = pathlib.Path(__file__).parent.parent.parent
PARALLEL_JSON_PATH = BASE_DIR / "scratch" / "parallel_articles.json"
TRANS_DIR = BASE_DIR / "data" / "translations"

def get_clean_elements(body):
    if not body:
        return []
    elements = body.find_all(['h1', 'h2', 'h3', 'p', 'li'])
    clean = []
    for el in elements:
        parent = el.parent
        is_nested = False
        while parent and parent != body:
            if parent.name in ['h1', 'h2', 'h3', 'p', 'li']:
                is_nested = True
                break
            parent = parent.parent
        if not is_nested:
            clean.append(el)
    return clean

def build_block_keys(elements):
    keys = []
    last_pid = "0"
    tag_counts = {}
    for el in elements:
        pid = el.get('data-pid')
        tag = el.name
        if pid is not None:
            last_pid = pid
            key = f"{tag}_{pid}"
            tag_counts = {}
        else:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
            idx = tag_counts[tag]
            key = f"{tag}_{last_pid}_{idx}"
        keys.append(key)
    return keys

def main():
    TRANS_DIR.mkdir(parents=True, exist_ok=True)
    
    if not PARALLEL_JSON_PATH.exists():
        print(f"Error: {PARALLEL_JSON_PATH} not found. Please crawl category pages first.")
        return

    with open(PARALLEL_JSON_PATH, "r", encoding="utf-8") as f:
        parallel_urls = json.load(f)

    print(f"Loaded {len(parallel_urls)} parallel articles to scrape.")
    
    moore_fr_records = []
    moore_en_records = []
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for idx, triplet in enumerate(parallel_urls):
        print(f"[{idx+1}/{len(parallel_urls)}] Scraping article: {triplet['fr']}")
        
        # Determine a clean slug/name for the article id
        slug = triplet['fr'].rstrip('/').split('/')[-1]
        
        try:
            # 1. Fetch French
            fr_r = requests.get(triplet['fr'], headers=headers, timeout=10)
            fr_soup = BeautifulSoup(fr_r.text, "html.parser")
            fr_body = fr_soup.find('div', class_='docSubContent')
            fr_els = get_clean_elements(fr_body)
            fr_keys = build_block_keys(fr_els)
            fr_blocks = {key: el.text.strip() for key, el in zip(fr_keys, fr_els)}
            
            # 2. Fetch English
            en_r = requests.get(triplet['en'], headers=headers, timeout=10)
            en_soup = BeautifulSoup(en_r.text, "html.parser")
            en_body = en_soup.find('div', class_='docSubContent')
            en_els = get_clean_elements(en_body)
            en_keys = build_block_keys(en_els)
            en_blocks = {key: el.text.strip() for key, el in zip(en_keys, en_els)}
            
            # 3. Fetch Mooré
            mos_r = requests.get(triplet['mos'], headers=headers, timeout=10)
            mos_soup = BeautifulSoup(mos_r.text, "html.parser")
            mos_body = mos_soup.find('div', class_='docSubContent')
            mos_els = get_clean_elements(mos_body)
            mos_keys = build_block_keys(mos_els)
            mos_blocks = {key: el.text.strip() for key, el in zip(mos_keys, mos_els)}
            
            # Align by key
            for key in mos_keys:
                moore_text = mos_blocks[key]
                
                # Check French alignment
                if key in fr_blocks:
                    moore_fr_records.append({
                        "verse_id": f"art_{slug}_{key}",
                        "moore_text": moore_text,
                        "french_text": fr_blocks[key]
                    })
                
                # Check English alignment
                if key in en_blocks:
                    moore_en_records.append({
                        "verse_id": f"art_{slug}_{key}",
                        "moore_text": moore_text,
                        "english_text": en_blocks[key]
                    })
                    
        except Exception as e:
            print(f"  ✗ Error processing article {slug}: {e}")
            
        time.sleep(0.1)
        
    # Write to CSV
    fr_df = pd.DataFrame(moore_fr_records)
    en_df = pd.DataFrame(moore_en_records)
    
    fr_out = TRANS_DIR / "articles_fr.csv"
    en_out = TRANS_DIR / "articles_en.csv"
    
    fr_df.to_csv(fr_out, index=False, encoding="utf-8")
    en_df.to_csv(en_out, index=False, encoding="utf-8")
    
    print(f"\n✅ Scraping and alignment of articles completed!")
    print(f"  - Mooré-French: {len(fr_df)} aligned blocks -> {fr_out}")
    print(f"  - Mooré-English: {len(en_df)} aligned blocks -> {en_out}")

if __name__ == "__main__":
    main()
