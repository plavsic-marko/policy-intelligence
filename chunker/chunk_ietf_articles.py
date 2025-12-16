import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "ietf" / "ietf_articles_all.jsonl"
OUT_PATH = ROOT / "data" / "processed" / "ietf_paragraphs.jsonl"

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)


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


def parse_date(raw):
    """Pretvara '7 Apr 2025' → datetime ili vraća None."""
    if not raw:
        return None

    parts = raw.split()
    if len(parts) != 3:
        return None

    day, mon, year = parts
    if mon not in MONTHS:
        return None

    try:
        return datetime(int(year), MONTHS[mon], int(day))
    except:
        return None


def compute_quarter(dt):
    """Vraca string '2025-Q1' itd."""
    if not dt:
        return None
    q = (dt.month - 1) // 3 + 1
    return f"{dt.year}-Q{q}"


def clean_text(t):
    """Čisti višestruke razmake i \n."""
    return re.sub(r"\s+", " ", t).strip()


def detect_section_title(txt):
    """
    Detektuje naslove sekcija: H2 prepoznat kao veliki naslov:
    Pravila:
    - velika početna slova
    - ne završava tačkom
    - kraći od 10 reči
    """
    if not txt:
        return None

    if len(txt.split()) > 10:
        return None

    if txt.endswith("."):
        return None

    if txt[0].isupper():
        return txt.strip()

    return None


def detect_subsection(txt):
    """
    Detektuje podnaslove (H3 tip), kraći, ali nije sav tekst velik.
    """
    if not txt:
        return None

    if len(txt.split()) > 12:
        return None

    if txt.endswith("."):
        return None

    if txt[0].isupper():
        return txt.strip()

    return None


def chunk_article(article):
    """
    Prima jedan ceo JSON iz articla:
    {
      "url": "...",
      "title": "...",
      "date": "...",  # originalno
      "html_content": "...",
      "text_content": "....\n...."
    }
    Produkuje listu JSON objekata (paragraph + meta)
    """

    url = article.get("url")
    origin_site = "ietf.org"
    title = article.get("title") or ""
    raw_date = article.get("date")

    dt = parse_date(raw_date)
    quarter = compute_quarter(dt)

    final_paragraphs = []

    section = None
    subsection = None

    paras = (article.get("text_content") or "").split("\n")

    for p in paras:
        p = clean_text(p)
        if not p:
            continue

        new_section = detect_section_title(p)
        if new_section:
            section = new_section
            subsection = None
            continue

        new_sub = detect_subsection(p)
        if new_sub:
            subsection = new_sub
            continue

        final_paragraphs.append(
            {
                "source": origin_site,
                "origin_site": origin_site,
                "node_type": "paragraph",
                "url": url,
                "title": title,
                "date": raw_date,
                "quarter": quarter,
                "categories": [],
                "tags": [],
                "section_title": section,
                "subsection_title": subsection,
                "text": p,
            }
        )

    final_paragraphs.insert(
        0,
        {
            "source": origin_site,
            "origin_site": origin_site,
            "node_type": "article",
            "url": url,
            "title": title,
            "date": raw_date,
            "quarter": quarter,
            "categories": [],
            "tags": [],
        },
    )

    return final_paragraphs


def main():
    total_paragraphs = 0
    skipped = 0

    with OUT_PATH.open("w", encoding="utf-8") as out_f:
        with RAW_PATH.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    article = json.loads(line)
                except:
                    skipped += 1
                    continue

                chunks = chunk_article(article)

                for ch in chunks:
                    out_f.write(json.dumps(ch, ensure_ascii=False) + "\n")
                    total_paragraphs += 1

    print(f"IETF → {OUT_PATH} | zapisa: {total_paragraphs} | preskočeno: {skipped}")


if __name__ == "__main__":
    main()
