import json
import re
from datetime import datetime

INPUT_FILE = "un_ode_news_clean.jsonl"
OUTPUT_FILE = "un_ode_news_chunks.jsonl"

MAX_CHARS = 1500


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def calculate_quarter(date_iso):
    """
    date_iso je već 'YYYY-MM-DD'.
    """
    try:
        dt = datetime.strptime(date_iso, "%Y-%m-%d")
        q = (dt.month - 1) // 3 + 1
        return f"{dt.year}-Q{q}"
    except:
        return None


def build_categories(title, text):
    cats = {"UN ODET"}
    t = (title + " " + text).lower()

    if "global digital compact" in t or "gdc" in t:
        cats.add("Global Digital Compact")

    if "digital public infrastructure" in t or "dpi" in t:
        cats.add("Digital Public Infrastructure")

    if "ai" in t or "artificial intelligence" in t:
        cats.add("AI Governance")

    if "cooperation" in t or "digital cooperation" in t:
        cats.add("Digital Cooperation")

    if "press release" in title.lower():
        cats.add("Press Release")

    if "event" in title.lower():
        cats.add("UN Events")

    return sorted(list(cats))


def build_tags(text):
    tags = set()
    t = text.lower()

    acronym_map = {
        "ai": "AI",
        "gdc": "GDC",
        "dpi": "DPI",
        "sti": "STI",
        "ecosoc": "ECOSOC",
        "unga": "UNGA",
        "hlab": "HLAB",
        "oset": "OSET",
        "odet": "ODET",
    }

    for key, tag in acronym_map.items():
        if key in t:
            tags.add(tag)

    return sorted(list(tags))


def smart_chunk(text):
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    current = ""

    for p in paragraphs:
        if len(current) + len(p) + 2 <= MAX_CHARS:
            current += p + "\n\n"
        else:
            if current.strip():
                chunks.append(current.strip())
            current = p + "\n\n"

    if current.strip():
        chunks.append(current.strip())

    final_chunks = []
    for ch in chunks:
        if len(ch) <= MAX_CHARS:
            final_chunks.append(ch)
        else:
            sentences = re.split(r"(?<=[.!?])\s+", ch)
            buf = ""
            for s in sentences:
                if len(buf) + len(s) + 1 <= MAX_CHARS:
                    buf += s + " "
                else:
                    final_chunks.append(buf.strip())
                    buf = s + " "
            if buf.strip():
                final_chunks.append(buf.strip())

    return final_chunks


def main():
    print("🔧 Generating UN ODET chunks...")

    with open(INPUT_FILE, "r", encoding="utf-8") as f_in, open(
        OUTPUT_FILE, "w", encoding="utf-8"
    ) as f_out:
        for line in f_in:
            item = json.loads(line)

            title = item["title"]
            text = item["text"]
            url = item["url"]
            date_iso = item["date"]
            date_full = f"{date_iso}T00:00:00Z"

            quarter = calculate_quarter(date_iso)
            slug = slugify(title)

            categories = build_categories(title, text)
            tags = build_tags(text)

            chunks = smart_chunk(text)

            for idx, chunk_text in enumerate(chunks):
                out = {
                    "id": f"un-ode::{slug}::{idx}",
                    "title": title,
                    "url": url,
                    "date": date_full,
                    "quarter": quarter,
                    "origin_site": "un-ode",
                    "source": "un-ode-news",
                    "categories": categories,
                    "tags": tags,
                    "text": chunk_text,
                }
                f_out.write(json.dumps(out, ensure_ascii=False) + "\n")

    print(f"\nSaved chunks → {OUTPUT_FILE}")
    print("Chunking complete!")


if __name__ == "__main__":
    main()
