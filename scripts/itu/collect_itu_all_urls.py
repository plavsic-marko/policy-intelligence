import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE = "https://www.itu.int/hub/?s=&post_type=post&paged={}"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

NEWS_RE = re.compile(r"^https://www\.itu\.int/hub/\d{4}/\d{2}/.+?/?$")
OUT = Path("itu_all_urls.jsonl")


def collect_all():
    all_urls = {}
    page = 1

    while True:
        url = BASE.format(page)
        resp = requests.get(url, headers=HEADERS, timeout=20)

        if resp.status_code != 200:
            break
        if "Nothing found" in resp.text:
            break

        soup = BeautifulSoup(resp.text, "html.parser")

        found_on_page = 0
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if href.startswith("/hub/"):
                href = "https://www.itu.int" + href

            if not NEWS_RE.match(href):
                continue

            title = a.get_text(strip=True)
            if not title:
                continue

            if href not in all_urls:
                all_urls[href] = {
                    "url": href,
                    "title": title,
                    "origin_site": "itu.int",
                    "source": "itu-news",
                }
                found_on_page += 1

        print(f"Page {page}: {found_on_page} URLs")

        if found_on_page == 0:
            break

        page += 1

    with OUT.open("w", encoding="utf-8") as f:
        for obj in all_urls.values():
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    print(f"\nDONE. Total URLs collected: {len(all_urls)}")
    print(f"Saved to: {OUT}")


if __name__ == "__main__":
    collect_all()
