print("RUNNING FILE:", __file__)

import json
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup, NavigableString
from requests.adapters import HTTPAdapter, Retry

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "ietf"
RAW_DIR.mkdir(parents=True, exist_ok=True)

URLS_PATH = RAW_DIR / "ietf_urls.json"
OUT_PATH = RAW_DIR / "ietf_articles_all.jsonl"
STATE_PATH = RAW_DIR / "ietf_articles_state.json"


def make_session():
    s = requests.Session()
    retries = Retry(
        total=6,
        backoff_factor=0.8,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    return s


def load_state():
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except:
            pass
    return {"next_index": 0}


def save_state(state):
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def clean_text(x):
    return " ".join(x.split())


def dedupe_paragraphs(paragraphs):
    seen = set()
    out = []
    for p in paragraphs:
        key = p.strip()
        if key and key not in seen:
            seen.add(key)
            out.append(p)
    return out


def extract_article(html):
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    if not main:
        return {"title": None, "date": None, "html_content": "", "text_content": ""}

    h1 = main.find("h1")
    if not h1:
        return {"title": None, "date": None, "html_content": "", "text_content": ""}

    title = h1.get_text(strip=True)

    after_nodes = []
    for node in h1.next_siblings:
        if isinstance(node, NavigableString):
            continue
        after_nodes.append(node)

    date = None
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    for node in after_nodes:
        if node.name == "p":
            txt = node.get_text(strip=True)
            if any(m in txt for m in months):
                date = txt
                break

    allowed = {"p", "h2", "h3", "pre", "div"}

    clean_nodes = []
    for node in after_nodes:
        if node.name not in allowed:
            continue

        if node.find("i", class_="bi-twitter") or node.find("i", class_="bi-linkedin"):
            continue

        clean_nodes.append(node)

    html_content = "".join(str(x) for x in clean_nodes)
    paragraphs = [clean_text(x.get_text(" ", strip=True)) for x in clean_nodes]
    paragraphs = dedupe_paragraphs(paragraphs)
    text_content = "\n".join(paragraphs)

    return {
        "title": title,
        "date": date,
        "html_content": html_content,
        "text_content": text_content,
    }


def load_urls():
    if not URLS_PATH.exists():
        print("❌ URLs file not found:", URLS_PATH)
        return []
    try:
        return json.loads(URLS_PATH.read_text(encoding="utf-8"))
    except:
        print("Failed to read URL file")
        return []


def main():
    urls = load_urls()
    if not urls:
        print("No URLs loaded.")
        return

    total = len(urls)
    state = load_state()
    start_index = state.get("next_index", 0)
    print(f"→ Resuming from index {start_index} / {total}")

    s = make_session()
    added_total = 0
    f = OUT_PATH.open("a", encoding="utf-8")

    for i in range(start_index, total):
        entry = urls[i]
        url = entry["url"]

        print(f"\n→ [{i+1}/{total}] Fetching {url}")

        delay = 0.5
        while True:
            try:
                r = s.get(url, timeout=30)
                r.raise_for_status()
                break
            except Exception as e:
                print(f"⚠ Fetch error: {e} | retry in {delay}s")
                time.sleep(delay)
                delay = min(delay + 0.5, 3.0)

        article = extract_article(r.text)

        record = {
            "url": url,
            "topics": entry.get("topics", []),
            **article,
        }

        f.write(json.dumps(record, ensure_ascii=False) + "\n")
        added_total += 1

        save_state({"next_index": i + 1})
        time.sleep(0.5)

    f.close()

    print(f"\n✔ DONE: total saved: {added_total}")
    print(f"→ Output: {OUT_PATH}")
    print(f"→ State saved: {STATE_PATH}")


if __name__ == "__main__":
    main()
