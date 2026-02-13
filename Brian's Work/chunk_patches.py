import re
import json
import pandas as pd
import os

# Get the folder where this script lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build full path to JSON file
json_path = os.path.join(BASE_DIR, "diablo_iv_patches_structured.json")

with open(json_path, "r", encoding="utf-8") as f:
    patches = json.load(f)

def simple_sentence_split(text):
    return re.split(r'(?<=[.!?])\s+', text)

chunks = []
chunk_id = 0
MAX_WORDS = 400

for patch in patches:
    sentences = simple_sentence_split(patch["content"])
    
    current_chunk = []
    current_word_count = 0
    
    for sentence in sentences:
        word_count = len(sentence.split())
        
        if current_word_count + word_count > MAX_WORDS:
            chunks.append({
                "chunk_id": chunk_id,
                "version": patch["version"],
                "build": patch["build"],
                "date": patch["date"],
                "chunk_text": " ".join(current_chunk),
                "word_count": current_word_count
            })
            
            chunk_id += 1
            current_chunk = []
            current_word_count = 0
        
        current_chunk.append(sentence)
        current_word_count += word_count
    
    if current_chunk:
        chunks.append({
            "chunk_id": chunk_id,
            "version": patch["version"],
            "build": patch["build"],
            "date": patch["date"],
            "chunk_text": " ".join(current_chunk),
            "word_count": current_word_count
        })
        chunk_id += 1

chunks_df = pd.DataFrame(chunks)
chunks_df.to_csv("diablo_iv_chunks.csv", index=False)

print("✅ Chunks created:", len(chunks_df))