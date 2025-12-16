import json
import uuid
from pathlib import Path

from scripts.weaviate_client import WVT

CLASS_NAME = "PolicyChunksUnified"


EU_DS_DATA = Path("data/processed/eu_news_paragraphs_v3_pro.jsonl")


def to_rfc3339(value):
    if not value:
        return None
    v = str(value).strip()

    try:
        if len(v) == 10 and v[4] == "-" and v[7] == "-":
            return v + "T00:00:00Z"
    except:
        pass

    if "T" in v:
        return v if v.endswith("Z") else v + "Z"

    return None


def to_quarter(rfc3339_date):
    if not rfc3339_date:
        return None
    try:
        y = int(rfc3339_date[:4])
        m = int(rfc3339_date[5:7])
        q = (m - 1) // 3 + 1
        return f"{y}-Q{q}"
    except:
        return None


def stable_uuid(url, idx):
    base = f"digital-strategy|{url}#{idx}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, base))


def load_eu_ds():
    if not EU_DS_DATA.exists():
        print("[eu-ds] Fajl ne postoji → preskačem.")
        return []

    counters = {}
    items = []

    with EU_DS_DATA.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            obj = json.loads(line)

            text = (obj.get("text") or "").strip()
            if not text:
                continue

            url = (obj.get("url") or "").rstrip("/")
            if not url:
                continue

            raw_date = obj.get("date")
            date_iso = to_rfc3339(raw_date)
            quarter = obj.get("quarter") or to_quarter(date_iso)

            key = ("digital-strategy", url)
            counters[key] = counters.get(key, 0) + 1
            idx = counters[key]

            uid = stable_uuid(url, idx)

            raw_tags = obj.get("tags") or []
            tags = [t.lower().strip() for t in raw_tags if t]

            categories = [(c or "").strip() for c in (obj.get("categories") or [])]

            props = {
                "title": obj.get("title") or "",
                "text": text,
                "url": url,
                "source": obj.get("source") or "eu-news",
                "origin_site": "digital-strategy",
                "date": date_iso,
                "quarter": quarter,
                "categories": categories,
                "tags": tags,
            }

            items.append((uid, props))

    print(f"[eu-ds] ukupno chunkova: {len(items)}")
    return items


def main():
    schema = WVT.schema.get()
    existing = {c["class"] for c in schema.get("classes", [])}
    if CLASS_NAME not in existing:
        print(" Schema ne postoji! Kreiraj je prvo preko glavne ingest skripte.")
        return

    eu_ds_items = load_eu_ds()
    total = len(eu_ds_items)
    if total == 0:
        print("Nema EU DS chunkova za ingest.")
        return

    processed = 0

    with WVT.batch as batch:
        batch.batch_size = 200

        for uid, props in eu_ds_items:
            batch.add_data_object(props, CLASS_NAME, uuid=uid)
            processed += 1

            if processed % 500 == 0:
                pct = processed / total * 100
                print(f"... upisano {processed}/{total} ({pct:.1f}%)")

    print("---------------------------------------------")
    print(f"EU DS INGEST GOTOV: ukupno={processed}")
    print("---------------------------------------------")


if __name__ == "__main__":
    main()
