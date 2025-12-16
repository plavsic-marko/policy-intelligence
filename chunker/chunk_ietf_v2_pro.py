import json
import re
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

RAW_INPUT = Path("../data/processed/ietf_articles_enriched.jsonl")
OUTPUT_CHUNKS = Path("../data/processed/ietf_chunks.jsonl")
WARNINGS = Path("../data/processed/ietf_warnings.jsonl")
STATE_FILE = Path("../data/processed/ietf_state.json")


def load_jsonl(path):
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data.append(json.loads(line))
    return data


MONTHS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


def parse_ietf_date(date_str):
    """Convert '16 Apr 2025' → '2025-04-16T00:00:00'."""
    if not date_str:
        return None

    if "T" in date_str and "-" in date_str:
        return date_str

    parts = date_str.split()
    if len(parts) != 3:
        return date_str

    day_str, month_str, year_str = parts

    try:
        day = int(day_str)
        month = MONTHS.get(month_str)
        year = int(year_str)
        if month:
            dt = datetime(year, month, day)

            return dt.strftime("%Y-%m-%dT00:00:00")
    except Exception:
        pass

    return date_str


def derive_quarter(date_iso: str) -> str:
    """
    date_iso: očekujemo 'YYYY-MM-DD...' (npr. '2025-10-28T00:00:00')
    vraća: '2025-Q4' ili '' ako ne može da izračuna
    """
    if not date_iso:
        return ""
    try:
        year = int(date_iso[0:4])
        month = int(date_iso[5:7])
    except Exception:
        return ""

    if 1 <= month <= 3:
        q = "Q1"
    elif 4 <= month <= 6:
        q = "Q2"
    elif 7 <= month <= 9:
        q = "Q3"
    elif 10 <= month <= 12:
        q = "Q4"
    else:
        return ""

    return f"{year}-{q}"


def append_jsonl(path, obj):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def chunk_text(text, max_len=1200, fallback_threshold=1500):
    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    buffer = ""

    def split_sentences(long_text):
        sentences = re.split(r"(?<=[.!?])\s+", long_text)
        return [s.strip() for s in sentences if s.strip()]

    for p in paragraphs:

        if len(p) > fallback_threshold:
            sentences = split_sentences(p)

            if buffer.strip():
                chunks.append(buffer.strip())
                buffer = ""

            for s in sentences:
                if len(buffer) + len(s) + 1 <= max_len:
                    buffer += s + " "
                else:
                    if buffer.strip():
                        chunks.append(buffer.strip())
                    buffer = s + " "
            continue

        if len(buffer) + len(p) + 1 <= max_len:
            buffer = f"{buffer}\n{p}" if buffer else p
        else:
            if buffer.strip():
                chunks.append(buffer.strip())
            buffer = p

    if buffer.strip():
        chunks.append(buffer.strip())

    return chunks


def main():
    print("=== IETF CHUNKING START ===")

    data = load_jsonl(RAW_INPUT)

    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        start_index = state.get("last_processed", 0)
        print(f"[STATE] Continuing from index {start_index}")
    else:
        start_index = 0
        state = {"last_processed": 0}

    for i in tqdm(range(start_index, len(data)), desc="Chunking IETF"):
        item = data[i]

        doc_id = item.get("id")
        if not doc_id:
            doc_id = f"auto_{i}"
        doc_id = str(doc_id)

        text_content = item.get("text_content")
        if not text_content:
            append_jsonl(WARNINGS, {"id": doc_id, "issue": "Missing text_content"})
            continue

        raw_date = item.get("date")
        date_iso = parse_ietf_date(raw_date)
        if not date_iso:
            append_jsonl(WARNINGS, {"id": doc_id, "issue": "Invalid date"})

        quarter = item.get("quarter") or derive_quarter(date_iso)

        title = item.get("title", "")
        url = item.get("url", "")
        categories = item.get("categories", [])
        tags = item.get("tags", [])

        chunks = chunk_text(text_content)

        for idx, ch in enumerate(chunks, start=1):
            obj = {
                "id": f"ietf::{doc_id}::{idx:03}",
                "title": title,
                "url": url,
                "text": ch,
                "date": date_iso,
                "quarter": quarter,
                "categories": categories,
                "tags": tags,
                "origin_site": "ietf.org",
                "source": "ietf.org",
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
