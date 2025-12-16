import json
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]

RAW_UPDATES = ROOT / "data" / "raw" / "updates_all.json"
RAW_CATEGORIES = ROOT / "data" / "raw" / "categories.json"
RAW_TAGS = ROOT / "data" / "raw" / "tags.json"

OUT_FILE = ROOT / "data" / "processed" / "digwatch_clean_full.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def strip_html(html):
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(" ", strip=True)


def safe_date(date_str):
    if not date_str:
        return None
    try:
        d = datetime.fromisoformat(date_str.replace("Z", ""))
        return d.isoformat() + "Z"
    except Exception:
        return None


def main():

    updates = load_json(RAW_UPDATES)
    categories = load_json(RAW_CATEGORIES)
    tags = load_json(RAW_TAGS)

    category_map = {c["id"]: c["name"] for c in categories}
    tag_map = {t["id"]: t["name"] for t in tags}

    print(f"[INFO] Loaded {len(category_map)} categories")
    print(f"[INFO] Loaded {len(tag_map)} tags")
    print(f"[INFO] Loaded {len(updates)} digwatch updates")

    processed = []

    for u in updates:

        content_html = u.get("content", {}).get("rendered", "")
        excerpt_html = u.get("excerpt", {}).get("rendered", "")

        item = {
            "id": u.get("id"),
            "url": u.get("link"),
            "title": u.get("title", {}).get("rendered", "").strip(),
            "text": strip_html(content_html),
            "excerpt": strip_html(excerpt_html),
            "date": safe_date(u.get("date")),
            "modified": safe_date(u.get("modified")),
            "quarter": u.get("quarter"),
            "source": "digwatch",
            "origin_site": "digwatch",
            "node_type": u.get("type"),
            "category_ids": u.get("categories", []),
            "category_names": [
                category_map.get(cid, f"unknown:{cid}")
                for cid in u.get("categories", [])
            ],
            "tag_ids": u.get("tags", []),
            "tag_names": [
                tag_map.get(tid, f"unknown:{tid}") for tid in u.get("tags", [])
            ],
        }

        processed.append(item)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)

    print(f"[SUCCESS] Saved {len(processed)} cleaned updates → {OUT_FILE}")


if __name__ == "__main__":
    main()
