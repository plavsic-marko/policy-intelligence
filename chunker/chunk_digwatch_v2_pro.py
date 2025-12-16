import json
import re
from pathlib import Path

from tqdm import tqdm

RAW_INPUT = Path("../data/processed/digwatch_clean_full.json")
OUTPUT_CHUNKS = Path("../data/processed/digwatch_chunks.jsonl")
WARNINGS = Path("../data/processed/digwatch_warnings.jsonl")
STATE_FILE = Path("../data/processed/digwatch_state.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def append_jsonl(path, obj):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def chunk_text(text, max_len=1200, fallback_threshold=1500):
    """
    Split by paragraphs first.
    If a paragraph is longer than fallback_threshold,
    split it into sentences.
    """
    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

    chunks = []
    buffer = ""

    def split_by_sentences(long_text):
        """Simple sentence splitter for fallback."""
        sentences = re.split(r"(?<=[.!?])\s+", long_text)
        return [s.strip() for s in sentences if s.strip()]

    for p in paragraphs:

        if len(p) > fallback_threshold:
            sentences = split_by_sentences(p)

            if buffer.strip():
                chunks.append(buffer.strip())
                buffer = ""

            for sentence in sentences:
                if not sentence:
                    continue

                if len(buffer) + len(sentence) + 1 <= max_len:
                    buffer += sentence + " "
                else:
                    if buffer.strip():
                        chunks.append(buffer.strip())
                    buffer = sentence + " "

            continue

        if len(buffer) + len(p) + 1 <= max_len:
            buffer += p + "\n"
        else:
            if buffer.strip():
                chunks.append(buffer.strip())
            buffer = p + "\n"

    if buffer.strip():
        chunks.append(buffer.strip())

    return chunks


def main():
    print("=== DIGWATCH CHUNKING START ===")

    data = load_json(RAW_INPUT)

    if STATE_FILE.exists():
        state = load_json(STATE_FILE)
        start_index = state.get("last_processed", 0)
        print(f"[STATE] Continuing from index {start_index}")
    else:
        start_index = 0
        state = {"last_processed": 0}

    for i in tqdm(range(start_index, len(data)), desc="Chunking DigWatch"):
        item = data[i]
        doc_id = str(item.get("id", ""))

        if not item.get("text"):
            append_jsonl(WARNINGS, {"id": doc_id, "issue": "Missing text"})
            continue

        if not item.get("date"):
            append_jsonl(WARNINGS, {"id": doc_id, "issue": "Missing date"})

        categories = item.get("category_names", [])
        tags = item.get("tag_names", [])

        chunks = chunk_text(item["text"], max_len=1200, fallback_threshold=1500)

        for idx, ch in enumerate(chunks, start=1):
            obj = {
                "id": f"digwatch::{doc_id}::{idx:03}",
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "text": ch,
                "date": item.get("date"),
                "quarter": item.get("quarter", ""),
                "categories": categories,
                "tags": tags,
                "origin_site": "digwatch",
                "source": "digwatch",
            }
            append_jsonl(OUTPUT_CHUNKS, obj)

        state["last_processed"] = i + 1
        save_json(STATE_FILE, state)

    print("=== DONE ===")
    print(f"Chunks saved to: {OUTPUT_CHUNKS}")
    print(f"Warnings saved to: {WARNINGS}")
    print(f"State saved to: {STATE_FILE}")


if __name__ == "__main__":
    main()
