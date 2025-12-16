import json
import uuid
from pathlib import Path

from scripts.weaviate_client import WVT

CLASS_NAME = "PolicyChunksUnified"

# Lokacija ITU chunk fajla (ENRICHED)
ITU_DATA = Path("data/processed/itu_news_paragraphs_enriched.jsonl")


# ----------------------------------------------------------
# Normalizacija datuma — dodaj Z ako ga nema
# ----------------------------------------------------------
def fix_date(value):
    if not value:
        return None

    v = str(value).strip()

    if v.endswith("Z"):
        return v

    if "T" in v:
        return v + "Z"

    return v


def load_itu():
    if not ITU_DATA.exists():
        print("[itu]  Fajl ne postoji!")
        return []

    items = []

    with ITU_DATA.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            obj = json.loads(line)

            text = (obj.get("text") or "").strip()
            if not text:
                continue

            raw_id = obj.get("id")
            if not raw_id:
                continue

            uid = str(uuid.uuid5(uuid.NAMESPACE_URL, raw_id))

            date = fix_date(obj.get("date"))
            quarter = obj.get("quarter")

            tags = obj.get("tags") or []
            tags = [str(t).lower() for t in tags]

            props = {
                "title": obj.get("title") or "",
                "text": text,
                "url": obj.get("url") or "",
                "source": obj.get("source") or "itu",
                "origin_site": obj.get("origin_site") or "itu-news",
                "date": date,
                "quarter": quarter,
                "categories": obj.get("categories") or [],
                "tags": tags,
            }

            items.append((uid, props))

    print(f"[itu] ukupno chunkova: {len(items)}")
    return items


def ingest():
    print(" ITU INGEST START")

    schema = WVT.schema.get()
    classes = {c["class"] for c in schema.get("classes", [])}

    if CLASS_NAME not in classes:
        print(" Klasa ne postoji!")
        return

    itu_items = load_itu()
    total = len(itu_items)

    if total == 0:
        print("Nema ITU chunkova za ingest.")
        return

    processed = 0

    with WVT.batch as batch:
        batch.batch_size = 200

        for uid, props in itu_items:
            batch.add_data_object(props, CLASS_NAME, uuid=uid)
            processed += 1

            if processed % 500 == 0:
                pct = processed / total * 100
                print(f"... upisano {processed}/{total} ({pct:.1f}%)")

    print("---------------------------------------------")
    print(f" ITU INGEST GOTOV: ukupno={processed}")
    print("---------------------------------------------")


if __name__ == "__main__":
    ingest()
