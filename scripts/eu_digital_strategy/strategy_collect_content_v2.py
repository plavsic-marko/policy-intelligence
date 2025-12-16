import json
import random
import time
from pathlib import Path

import requests
from lxml import html

INPUT_FILE = "eu_news_full_20251120_0008.json"
OUTPUT_DIR = Path("content_output")
STATE_FILE = Path("content_state.json")

OUTPUT_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

MAX_RETRIES = 7
BASE_SLEEP = 1.5


def load_urls(path: str):
    print(f"🔎 Učitavam ulaz: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        print(f"✔ Detektovan format: LIST ({len(data)} objekata)")
        return data

    if isinstance(data, dict) and "items" in data:
        print(f"✔ Detektovan format: DICT['items'] ({len(data['items'])} objekata)")
        return data["items"]

    if isinstance(data, dict) and "successful_items" in data:
        merged = data["successful_items"] + data.get("failed_items", [])
        print(f"✔ Detektovan format: successful+failed ({len(merged)} objekata)")
        return merged

    if isinstance(data, dict) and "processed_items" in data:
        print(
            f"✔ Detektovan format: processed_items ({len(data['processed_items'])} objekata)"
        )
        return data["processed_items"]

    raise ValueError("❌ Nepoznat format input JSON fajla!")


def load_state():
    if not STATE_FILE.exists():
        return {"done_urls": set(), "last_index": 0}

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        st = json.load(f)
        st["done_urls"] = set(st.get("done_urls", []))
        return st


def save_state(state):
    state_copy = dict(state)
    state_copy["done_urls"] = list(state_copy["done_urls"])
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state_copy, f, indent=2, ensure_ascii=False)


def fetch_page(url: str):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=12)
            if r.status_code == 200:
                return r.text

            if r.status_code == 429:
                wait = min(60, BASE_SLEEP * attempt * random.uniform(1.3, 2.2))
                print(f"⚠️ 429 → čekam {wait:.1f}s (pokušaj {attempt}/{MAX_RETRIES})")
                time.sleep(wait)
                continue

            if 500 <= r.status_code < 600:
                wait = 2 + attempt * 2
                print(
                    f" {r.status_code} → pauza {wait}s (pokušaj {attempt}/{MAX_RETRIES})"
                )
                time.sleep(wait)
                continue

            print(f" HTTP {r.status_code} → {url}")
            return None

        except Exception as e:
            wait = 2 + attempt * 2
            print(f" Greška: {e} → čekam {wait}s")
            time.sleep(wait)

    return None


def extract_content(html_text: str):
    try:
        doc = html.fromstring(html_text)
        paragraphs = doc.xpath("//p/text()")
        text = "\n".join([p.strip() for p in paragraphs if p.strip()])
        return text if text else None
    except:
        return None


def main():
    items = load_urls(INPUT_FILE)
    total = len(items)

    print(f" Ukupno URL-ova za obradu: {total}")

    state = load_state()

    for idx in range(state["last_index"], total):
        obj = items[idx]
        url = obj.get("url")

        print(f"[{idx+1}/{total}] → {url}")

        if url in state["done_urls"]:
            print("   ↳ preskačem (već urađeno)")
            continue

        html_text = fetch_page(url)
        if not html_text:
            obj["success"] = False
            obj["error"] = "fetch_failed"
        else:
            content = extract_content(html_text)
            if not content:
                obj["success"] = False
                obj["error"] = "parse_failed"
            else:
                obj["success"] = True
                obj["content"] = content

        out_path = OUTPUT_DIR / f"content_{idx+1:05d}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)

        state["done_urls"].add(url)
        state["last_index"] = idx + 1
        save_state(state)

        time.sleep(random.uniform(0.2, 0.7))

    print("🎉 GOTOVO – sve obradjeno!")


if __name__ == "__main__":
    main()
