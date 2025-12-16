import json
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.un.org"
LIST_URL = "https://www.un.org/digital-emerging-technologies/content/news"
HEADERS = {"User-Agent": "Mozilla/5.0"}

DATE_PATTERN = re.compile(r"\d{1,2}\s+[A-Za-z]+\s+\d{4}")


def collect_un_urls():
    print("🔎 Preuzimam listu vesti sa UN ODET...")
    r = requests.get(LIST_URL, headers=HEADERS, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    items = []

    articles = soup.find_all("h2")
    print(f" Pronadjeno H2 tagova: {len(articles)}")

    for h2 in articles:
        title = h2.get_text(strip=True)

        date_tag = h2.find_next("p")
        if not date_tag:
            continue

        date_txt = date_tag.get_text(strip=True)

        if not DATE_PATTERN.match(date_txt):
            continue

        link_tag = h2.find_next("a")
        if not link_tag:
            continue

        href = link_tag.get("href", "")
        full_url = urljoin(BASE_URL, href)

        items.append(
            {
                "title": title,
                "date": date_txt,
                "url": full_url,
                "listing_page": LIST_URL,
            }
        )

    out_file = "un_ode_news_urls.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    print(f"\n Sacuvano: {out_file}")
    print(f" Ukupno URL-ova: {len(items)}")

    return items


if __name__ == "__main__":
    collect_un_urls()
