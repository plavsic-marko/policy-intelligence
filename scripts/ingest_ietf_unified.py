# scripts/ingest_ietf_unified.py

import json
import uuid
from pathlib import Path

from scripts.weaviate_client import WVT

CLASS_NAME = "PolicyChunksUnified"
INPUT_FILE = Path("data/processed/ietf_chunks.jsonl")


def fix_date(value):
    if not value:
        return None

    v = str(value).strip()

    if v.endswith("Z"):
        return v

    if "T" in v:
        return v + "Z"

    return v


def load_ietf():
    if not INPUT_FILE.exists():
        print(f" Ne postoji fajl: {INPUT_FILE}")
        return []

    items = []

    with INPUT_FILE.open("r", encoding="utf-8") as f:
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

            tags = [str(t).lower() for t in (obj.get("tags") or [])]

            props = {
                "title": obj.get("title") or "",
                "text": text,
                "url": obj.get("url") or "",
                "source": obj.get("source") or "ietf.org",
                "origin_site": obj.get("origin_site") or "ietf.org",
                "date": date,
                "quarter": quarter,
                "categories": obj.get("categories") or [],
                "tags": tags,
            }

            items.append((uid, props))

    print(f"[ietf] ukupno chunkova: {len(items)}")
    return items


def ingest():
    print(" IETF INGEST START")

    schema = WVT.schema.get()
    classes = {c["class"] for c in schema.get("classes", [])}
    if CLASS_NAME not in classes:
        print(" Klasa ne postoji!")
        return

    ietf_items = load_ietf()
    total = len(ietf_items)

    if total == 0:
        print("Nema IETF chunkova za ingest.")
        return

    processed = 0

    with WVT.batch as batch:
        batch.batch_size = 200

        for uid, props in ietf_items:
            batch.add_data_object(props, CLASS_NAME, uuid=uid)
            processed += 1

            if processed % 500 == 0:
                pct = processed / total * 100
                print(f"... upisano {processed}/{total} ({pct:.1f}%)")

    print("---------------------------------------------")
    print(f"IETF INGEST GOTOV: ukupno={processed}")
    print("---------------------------------------------")


if __name__ == "__main__":
    ingest()
