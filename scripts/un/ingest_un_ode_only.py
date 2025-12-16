import json
import uuid
from pathlib import Path

from scripts.weaviate_client import WVT

CLASS_NAME = "PolicyChunksUnified"

UN_ODE_FILE = Path("data/processed/un_ode_news_chunks.jsonl")


def to_rfc3339(value):
    if not value:
        return None
    v = str(value).strip()

    if len(v) == 10 and v[4] == "-" and v[7] == "-":
        return v + "T00:00:00Z"

    if "T" in v:
        return v if v.endswith("Z") else v + "Z"

    return None


def to_quarter(rfc3339):
    if not rfc3339:
        return None
    try:
        y = int(rfc3339[:4])
        m = int(rfc3339[5:7])
        q = (m - 1) // 3 + 1
        return f"{y}-Q{q}"
    except:
        return None


def stable_uuid(url, idx):
    base = f"un-ode|{url}#{idx}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, base))


def load_un_ode():
    if not UN_ODE_FILE.exists():
        print("[un-ode] Fajl ne postoji → preskačem.")
        return []

    counters = {}
    rows = []

    with UN_ODE_FILE.open("r", encoding="utf-8") as f:
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

            key = ("un-ode", url)
            counters[key] = counters.get(key, 0) + 1
            idx = counters[key]

            uid = stable_uuid(url, idx)

            props = {
                "title": obj.get("title") or "",
                "text": text,
                "url": url,
                "source": obj.get("source") or "un-ode-news",
                "origin_site": "un-ode",
                "date": date_iso,
                "quarter": quarter,
                "categories": obj.get("categories") or [],
                "tags": obj.get("tags") or [],
            }

            rows.append((uid, props))

    print(f"[un-ode] ukupno chunkova: {len(rows)}")
    return rows


def main():
    schema = WVT.schema.get()
    existing = {c["class"] for c in schema.get("classes", [])}

    if CLASS_NAME not in existing:
        print(" Schema ne postoji! Kreiraj je prvo glavnom ingest skriptom.")
        return

    items = load_un_ode()
    total = len(items)

    if total == 0:
        print("Nema UN ODET chunkova za ingest.")
        return

    processed = 0

    with WVT.batch as batch:
        batch.batch_size = 200

        for uid, props in items:
            batch.add_data_object(props, CLASS_NAME, uuid=uid)
            processed += 1

            if processed % 500 == 0:
                pct = processed / total * 100
                print(f"... upisano {processed}/{total} ({pct:.1f}%)")

    print("---------------------------------------------")
    print(f"UN ODET INGEST GOTOV: ukupno={processed}")
    print("---------------------------------------------")


if __name__ == "__main__":
    main()
