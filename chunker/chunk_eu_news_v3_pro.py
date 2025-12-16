import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

INPUT_FILE = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "eu_digital_strategy"
    / "eu_news_FULL_REBUILT.jsonl"
)

OUTPUT_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "processed"
    / "eu_news_paragraphs_v3_pro.jsonl"
)

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

MAX_CHARS = 1200
HARD_MAX_CHARS = 2000


def clean_whitespace(text: str) -> str:
    """Normalizuj whitespace: trim, ukloni višak praznih redova, duple razmake."""
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    lines = [ln.strip() for ln in text.split("\n")]

    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()

    cleaned_lines = []
    empty_streak = 0
    for ln in lines:
        if not ln:
            empty_streak += 1
            if empty_streak > 1:
                continue
        else:
            empty_streak = 0
        cleaned_lines.append(ln)
    text = "\n".join(cleaned_lines)

    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def parse_date_and_quarter(date_published: str, date_updated: str) -> Tuple[str, str]:
    """
    Pretvori '17 November 2025' u ISO '2025-11-17T00:00:00Z' i '2025-Q4'.
    Ako nema datuma → vrati ("", "").
    """
    raw = (date_published or "").strip() or (date_updated or "").strip()
    if not raw:
        return "", ""

    raw = raw.replace("Publication", "").replace("Updated", "").strip()

    try:
        dt = datetime.strptime(raw, "%d %B %Y")
    except Exception:
        return "", ""

    iso = dt.strftime("%Y-%m-%dT00:00:00Z")
    q = (dt.month - 1) // 3 + 1
    quarter = f"{dt.year}-Q{q}"
    return iso, quarter


def split_into_paragraphs(content: str) -> List[str]:
    """Split po praznim redovima u paragraf blokove."""
    if not content:
        return []
    content = clean_whitespace(content)
    if not content:
        return []
    paras = re.split(r"\n\s*\n+", content)

    paras = [p.strip() for p in paras if p.strip()]
    return paras


def split_into_sentences(text: str) -> List[str]:
    """
    Veoma jednostavan sentence splitter – dovoljan za fallback.
    Ne pokušavamo da budemo savršeni, samo da razbijemo ogromne blokove.
    """
    text = clean_whitespace(text)
    if not text:
        return []

    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9“])", text)
    return [p.strip() for p in parts if p.strip()]


def build_chunk_blocks(content: str) -> List[str]:
    """
    Glavna logika chunkovanja:
      - prvo idemo po paragrafima
      - ako je paragraf > HARD_MAX_CHARS → razbij ga na rečenice
      - chunkujemo u blokove do MAX_CHARS, spajajući paragrafe/rečenice
    """
    paragraphs = split_into_paragraphs(content)
    blocks: List[str] = []

    atoms: List[str] = []
    for para in paragraphs:
        if len(para) <= HARD_MAX_CHARS:
            atoms.append(para)
        else:

            sentences = split_into_sentences(para)
            if not sentences:
                atoms.append(para)
            else:
                atoms.extend(sentences)

    current: List[str] = []
    current_len = 0

    for atom in atoms:
        atom = atom.strip()
        if not atom:
            continue

        if len(atom) > MAX_CHARS:
            if current:
                blocks.append("\n\n".join(current))
                current = []
                current_len = 0
            start = 0
            while start < len(atom):
                piece = atom[start : start + MAX_CHARS]
                blocks.append(piece.strip())
                start += MAX_CHARS
            continue

        if not current:
            current.append(atom)
            current_len = len(atom)
        else:

            if current_len + 2 + len(atom) <= MAX_CHARS:
                current.append(atom)
                current_len += 2 + len(atom)
            else:
                blocks.append("\n\n".join(current))
                current = [atom]
                current_len = len(atom)

    if current:
        blocks.append("\n\n".join(current))

    return blocks


ACRONYM_WHITELIST = [
    "AI",
    "HPC",
    "ENISA",
    "NIS2",
    "GDPR",
    "TSMC",
    "DMA",
    "DSA",
    "EuroHPC",
    "5G",
    "6G",
    "CEF",
    "DNS4EU",
    "EDIC",
    "EDIH",
    "SME",
    "SMEs",
    "eIDAS",
]


def infer_thematic_categories(text: str, title: str) -> List[str]:
    """Vrati listu tematskih kategorija na osnovu ključnih reči."""
    hay = f"{title}\n{text}".lower()

    cats: List[str] = []

    def add(label: str):
        if label not in cats:
            cats.append(label)

    # AI
    if any(
        kw in hay
        for kw in [
            "artificial intelligence",
            " ai ",
            " ai,",
            " ai.",
            "ai-",
            "foundation model",
            "machine learning",
        ]
    ):
        add("AI")

    if any(
        kw in hay
        for kw in [
            "cybersecurity",
            "cyber security",
            "cyber-attack",
            "cyber attack",
            "ransomware",
            "malware",
            "enisa",
            "nis2",
            "cyber crime",
            "cybercrime",
        ]
    ):
        add("Cybersecurity")

    if any(
        kw in hay
        for kw in [
            "semiconductor",
            "microchip",
            "chip ",
            "chips act",
            "wafer",
            "tsmc",
            "eurohpc",
        ]
    ):
        add("Semiconductors")

    if any(
        kw in hay
        for kw in [
            "submarine cable",
            "submarine cables",
            "undersea cable",
            "cable security",
            "digital connectivity",
            "5g",
            "6g",
            "broadband",
            "backbone network",
        ]
    ):
        add("Connectivity / Cables")

    if any(
        kw in hay
        for kw in [
            "call for proposals",
            "call for proposal",
            "grant",
            "funding",
            "million",
            "billion",
            "digital europe programme",
            "horizon europe",
            "connecting europe facility",
            "cef digital",
        ]
    ):
        add("Funding / Programmes")

    if any(
        kw in hay
        for kw in [
            "media freedom",
            "journalist",
            "journalists",
            "audiovisual",
            "creative europe",
            "press freedom",
            "news media",
        ]
    ):
        add("Media & Journalism")

    if "ukraine" in hay:
        add("Ukraine")

    if any(
        kw in hay
        for kw in [
            "digital skills",
            "reskilling",
            "upskilling",
            "training programme",
            "education",
            "schools",
            "teachers",
            "students",
        ]
    ):
        add("Digital skills & Education")

    if any(
        kw in hay
        for kw in [
            "eidas",
            "electronic identification",
            "digital identity",
            "eu id wallet",
            "eu digital identity wallet",
        ]
    ):
        add("Digital identity & Trust services")

    return cats


def infer_tags(text: str, title: str) -> List[str]:
    """Vrati listu tagova: tematski tagovi + akronimi."""
    tags: List[str] = []
    hay_full = f"{title}\n{text}"

    for cat in infer_thematic_categories(text, title):
        tag = cat.lower().replace(" ", "-").replace("/", "-")
        if tag not in tags:
            tags.append(tag)

    for ac in ACRONYM_WHITELIST:
        pattern = r"\b" + re.escape(ac) + r"\b"
        if re.search(pattern, hay_full):
            if ac not in tags:
                tags.append(ac)

    return tags


def slug_from_url(url: str) -> str:
    """Uzmi poslednji deo URL-a (bez query stringa) za ID."""
    if not url:
        return "unknown"
    core = url.split("?", 1)[0].rstrip("/")
    slug = core.rsplit("/", 1)[-1]
    if not slug:
        slug = "root"
    return slug


def main():
    if not INPUT_FILE.exists():
        print(f"❌ INPUT ne postoji: {INPUT_FILE}")
        return

    count_articles = 0
    count_chunks = 0

    with open(INPUT_FILE, "r", encoding="utf-8") as fin, open(
        OUTPUT_FILE, "w", encoding="utf-8"
    ) as fout:
        for line_idx, line in enumerate(fin, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON decode error u liniji {line_idx}: {e}")
                continue

            url = obj.get("url") or ""
            title = obj.get("title") or ""
            content = obj.get("content") or ""
            if not content.strip():
                continue

            count_articles += 1

            date_iso, quarter = parse_date_and_quarter(
                obj.get("date_published", "") or "", obj.get("date_updated", "") or ""
            )

            base_cat = obj.get("news_type") or obj.get("content_type") or "News article"
            base_categories = [base_cat]

            slug = slug_from_url(url)
            blocks = build_chunk_blocks(content)

            for local_idx, block in enumerate(blocks, start=1):
                block = clean_whitespace(block)
                if not block:
                    continue

                thematic = infer_thematic_categories(block, title)
                # spoji kategorije bez duplikata
                categories: List[str] = []
                for c in base_categories + thematic:
                    if c and c not in categories:
                        categories.append(c)

                tags = infer_tags(block, title)

                chunk_id = f"eu-news::{slug}::{local_idx:03d}"

                rec = {
                    "id": chunk_id,
                    "text": block,
                    "title": title,
                    "url": url,
                    "source": "eu-news",
                    "date": date_iso,
                    "quarter": quarter,
                    "categories": categories,
                    "tags": tags,
                    "origin_site": "digital-strategy",
                }

                fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
                count_chunks += 1

    print("\n======================================")
    print("Završeno EU DS chunkovanje (v3 PRO)!")
    print(f"Ukupno članaka: {count_articles}")
    print(f"Generisano chunkova: {count_chunks}")
    print(f"Output fajl: {OUTPUT_FILE}")
    print("======================================\n")


if __name__ == "__main__":
    main()
