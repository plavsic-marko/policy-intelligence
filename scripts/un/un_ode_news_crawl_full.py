import json
from datetime import datetime

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

INPUT_URLS = "un_ode_news_urls.json"
OUTPUT_FILE = "un_ode_news_full.jsonl"


def parse_date(date_str):
    date_str = date_str.strip()
    try:
        return datetime.strptime(date_str, "%d %B %Y").strftime("%Y-%m-%d")
    except:
        return date_str  # fallback


def extract_text(soup):
    """
    Pokušavamo 3 nivoa:
    1) UN standardni body div (.field--name-body)
    2) <main> pa <p>
    3) fallback: SVI <p>
    """

    body = soup.select_one(".field--name-body")
    if body:
        paragraphs = [p.get_text(" ", strip=True) for p in body.find_all("p")]
        return "\n\n".join(paragraphs)

    main_tag = soup.find("main")
    if main_tag:
        paragraphs = [p.get_text(" ", strip=True) for p in main_tag.find_all("p")]
        if paragraphs:
            return "\n\n".join(paragraphs)

    all_p = soup.find_all("p")
    if all_p:
        paragraphs = [p.get_text(" ", strip=True) for p in all_p]
        return "\n\n".join(paragraphs)

    return ""


def crawl_article(item):
    url = item["url"]
    print(f" Crawling: {url}")

    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print(f" ERROR {url}: {e}")
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    text = extract_text(soup)
    if not text:
        print(f"⚠️ Empty content: {url}")

    iso_date = parse_date(item["date"])

    return {
        "id": f"un-ode::{url}",
        "title": item["title"],
        "date": iso_date,
        "url": url,
        "origin_site": "un-ode",
        "text": text,
    }


def main():
    print(" Učitavam URL listu...")
    with open(INPUT_URLS, "r", encoding="utf-8") as f:
        urls = json.load(f)

    print(f" Ukupno za crawling: {len(urls)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for item in urls:
            data = crawl_article(item)
            if data:
                out.write(json.dumps(data, ensure_ascii=False) + "\n")

    print(f"\n Sačuvano: {OUTPUT_FILE}")
    print(" Full crawling završen!")


if __name__ == "__main__":
    main()
