# crawler/ietf_collect_urls.py

import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

LISTING_URL = "https://www.ietf.org/blog/all/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

OUTPUT_PATH = Path("data/raw/ietf/ietf_urls.json")


def load_existing():
    if OUTPUT_PATH.exists():
        try:
            return json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        except:
            return []
    return []


def save(data):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def extract_blog_rows(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = []

    table = soup.find("table")
    if not table:
        print("⚠ Table not found on the page.")
        return rows

    for tr in table.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue

        date = tds[0].get_text(strip=True)

        a = tds[1].find("a")
        if not a:
            continue

        link = a.get("href")
        title = a.get_text(strip=True)

        if link.startswith("/"):
            link = "https://www.ietf.org" + link

        rows.append(
            {
                "url": link,
                "title": title,
                "date": date,
                "topics": [],
            }
        )

    return rows


def main():
    print("→ Fetching IETF blog listing…")

    try:
        resp = requests.get(LISTING_URL, headers=HEADERS, timeout=20)
    except Exception as e:
        print("Network error:", e)
        return

    if resp.status_code != 200:
        print(f"Unexpected status code: {resp.status_code}")
        return

    rows = extract_blog_rows(resp.text)
    if not rows:
        print(" No rows extracted — check HTML structure.")
        return

    existing = load_existing()

    all_urls = {entry["url"]: entry for entry in existing}

    for r in rows:
        all_urls[r["url"]] = r

    final_list = list(all_urls.values())
    save(final_list)

    print(f"✔ Done. Total blog posts collected: {len(final_list)}")
    print(f"✔ Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
