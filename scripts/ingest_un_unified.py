import json
import uuid
from pathlib import Path

from scripts.weaviate_client import WVT

CLASS_NAME = "PolicyChunksUnified"


UN_DATA = Path("data/processed/un_ode_filtered.jsonl")


def fix_date(value):
    if not value:
        return None

    v = str(value).strip()

    if v.endswith("Z"):
        return v

    if "T" in v:
        return v + "Z"

    return v


def load_un():
    if not UN_DATA.exists():
        print("[un]  Fajl ne postoji!")
        return []

    items = []

    with UN_DATA.open("r", encoding="utf-8") as f:
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

            uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, raw_id))

            date = fix_date(obj.get("date"))
            quarter = obj.get("quarter")

            tags = obj.get("tags") or []
            tags = [str(t).lower() for t in tags]

            props = {
                "title": obj.get("title") or "",
                "text": text,
                "url": obj.get("url") or "",
                "source": obj.get("source") or "un",
                "origin_site": obj.get("origin_site") or "un",
                "date": date,
                "quarter": quarter,
                "categories": obj.get("categories") or [],
                "tags": tags,
            }

            items.append((uid, props))

    print(f"[un] ukupno chunkova: {len(items)}")
    return items


def ingest():
    print(" UN INGEST START")

    schema = WVT.schema.get()
    classes = {c["class"] for c in schema.get("classes", [])}

    if CLASS_NAME not in classes:
        print(" Klasa ne postoji!")
        return

    un_items = load_un()
    total = len(un_items)

    if total == 0:
        print("Nema UN chunkova za ingest.")
        return

    processed = 0

    with WVT.batch as batch:
        batch.batch_size = 200

        for uid, props in un_items:
            batch.add_data_object(props, CLASS_NAME, uuid=uid)
            processed += 1

            if processed % 500 == 0:
                pct = processed / total * 100
                print(f"... upisano {processed}/{total} ({pct:.1f}%)")

    print("---------------------------------------------")
    print(f" UN INGEST GOTOV: ukupno={processed}")
    print("---------------------------------------------")


if __name__ == "__main__":
    ingest()
