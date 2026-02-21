import argparse
import json
import re
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = REPO_ROOT / "data/interim/patch_notes/diablo_iv_patches_structured.json"
DEFAULT_OUTPUT = REPO_ROOT / "data/interim/patch_notes/diablo_iv_chunks.csv"


def simple_sentence_split(text: str) -> list[str]:
    return re.split(r"(?<=[.!?])\s+", text)


def chunk_patches(patches: list[dict], max_words: int = 400) -> pd.DataFrame:
    chunks = []
    chunk_id = 0

    for patch in patches:
        sentences = simple_sentence_split(str(patch.get("content", "")))
        current_chunk = []
        current_word_count = 0

        for sentence in sentences:
            word_count = len(sentence.split())
            if current_word_count + word_count > max_words and current_chunk:
                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "version": patch.get("version"),
                        "build": patch.get("build"),
                        "date": patch.get("date"),
                        "chunk_text": " ".join(current_chunk),
                        "word_count": current_word_count,
                    }
                )
                chunk_id += 1
                current_chunk = []
                current_word_count = 0

            current_chunk.append(sentence)
            current_word_count += word_count

        if current_chunk:
            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "version": patch.get("version"),
                    "build": patch.get("build"),
                    "date": patch.get("date"),
                    "chunk_text": " ".join(current_chunk),
                    "word_count": current_word_count,
                }
            )
            chunk_id += 1

    return pd.DataFrame(chunks)


def main() -> None:
    parser = argparse.ArgumentParser(description="Chunk structured patch notes text.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--max-words", type=int, default=400)
    args = parser.parse_args()

    patches = json.loads(args.input.read_text(encoding="utf-8"))
    chunks_df = chunk_patches(patches, max_words=args.max_words)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    chunks_df.to_csv(args.output, index=False)

    print(f"Wrote: {args.output}")
    print(f"Chunks: {len(chunks_df)}")


if __name__ == "__main__":
    main()
