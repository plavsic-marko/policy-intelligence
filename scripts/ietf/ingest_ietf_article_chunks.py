import json
import uuid
from collections import defaultdict
from pathlib import Path

from scripts.weaviate_client import WVT

DATA = Path("data/processed/ietf_paragraphs.jsonl")
CLASS_NAME = "IETF_ArticleChunks"


def to_rfc3339(v):
    """
    Vrati RFC3339 string:
    - 'YYYY-MM-DD'             -> 'YYYY-MM-DDT00:00:00Z'
    - 'YYYY-MM-DDTHH:MM:SS'    -> doda 'Z' ako ne postoji
    - već ima 'Z' ili vremensku zonu -> ostavi kako jeste
    - prazno/None -> None
    """
    if not v:
        return None
    s = str(v).strip()
    if not s:
        return None

    if len(s) == 10 and s[4] == "-" and s[7] == "-":
        return s + "T00:00:00Z"

    if "T" in s:
        if s.endswith("Z") or "+" in s or s.endswith("z"):
            return s
        return s + "Z"

    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        return s[:10] + "T00:00:00Z"
    return None


def para_uuid(url: str, idx: int) -> str:
    """Stabilan UUID po URL-u + lokalnom indeksu pasusa."""
    norm = (url or "").rstrip("/")
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{norm}#{idx}"))


def main():
    assert DATA.exists(), f"Nema {DATA}"

    counters = defaultdict(int)

    total = 0
    with WVT.batch as b:
        b.batch_size = 200

        with DATA.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)

                if obj.get("node_type") != "paragraph":
                    continue

                url = (obj.get("url") or "").rstrip("/")
                if not url:
                    continue

                idx = counters[url]
                counters[url] += 1
                puid = para_uuid(url, idx)

                effective_date_raw = obj.get("effective_date")
                effective_date = to_rfc3339(effective_date_raw)

                props = {
                    "source": obj.get("source") or "ietf.org",
                    "url": url,
                    "title": obj.get("title") or "",
                    "author": obj.get("author") or "",
                    "section_title": obj.get("section_title"),
                    "subsection_title": obj.get("subsection_title"),
                    "text": obj.get("text") or "",
                    "node_type": obj.get("node_type") or "paragraph",
                    "quarter": obj.get("quarter"),
                    "effective_date": effective_date,
                    "topics": obj.get("topics") or [],
                }

                if not props["text"]:
                    continue

                WVT.batch.add_data_object(
                    data_object=props,
                    class_name=CLASS_NAME,
                    uuid=puid,
                )

                total += 1
                if total % 1000 == 0:
                    print(f"… IETF chunks: {total}")

    print(f"[OK] Ingest za {CLASS_NAME} gotov. Ukupno chunkova: {total}")


if __name__ == "__main__":
    main()
