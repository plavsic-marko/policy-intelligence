import json
import random
import re
import time
from pathlib import Path

import requests
from lxml import html

INPUT_URLS_FILE = "eu_news_full_20251120_0008.json"
OUTPUT_FILE = "eu_news_FULL_REBUILT.jsonl"
STATE_FILE = "eu_ds_state.json"


TEST_LIMIT = None

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

MAX_RETRIES = 6


SKIP_LINES = [
    "Share this page",
    "Follow us on",
    "Page of interest",
    "Find out about us",
    "©",
    "Subscribe to our newsletter",
    "Contact us",
    "Press and Communication officer",
    "Head of Sector Media and Content",
    "Read more",
    "Read the full press release",
]

STOP_PHRASES = [
    "Related topics",
    "Related content",
    "Related links",
    "Policy and legislation |",
    "Event report |",
    "Digibyte |",
    "Consultation |",
]

GLOBAL_REMOVE_PATTERNS = [
    r"This is a machine translation provided by the European Commission",
    r"Your booklet .*? available for download",
    r"Your data extraction with Task ID.*?available for download",
    r"Each project \(from H2020 onwards\).*?",
    r"Amount of money, by way of direct subsidy.*?",
    r"This website may no longer be available.*?",
    r"Our security system detects an error.*?",
    r"Visiting a hacked website may harm your computer.*?",
    r"\{\{.*?\}\}",
    r"Article available in the following languages:",
    r"Article Category",
]

XPATH_PUBLISHED = '//*[@id="block-cnt-theme-pageheader"]/div/div/div/ul/li[2]'
XPATH_UPDATED = '//*[@id="block-cnt-theme-main-page-content"]/article/div/div[2]/div/div/div/section/div[2]/div[1]/p'


def clean_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def is_footer_date(text: str) -> bool:
    return bool(re.fullmatch(r"\d{1,2} \w+ 20\d{2}", text.strip()))


def global_clean(text: str) -> str:
    if not text:
        return ""
    cleaned = text
    for p in GLOBAL_REMOVE_PATTERNS:
        cleaned = re.sub(p, "", cleaned, flags=re.DOTALL)

    cleaned = re.sub(r"European Union, 20\d{2}.*$", "", cleaned, flags=re.DOTALL)

    cleaned = re.sub(r"\n\s*\n\s*\n+", "\n\n", cleaned)
    return cleaned.strip()


def load_state() -> int:
    """Učitava last_index iz STATE_FILE. Ako ne postoji → 0."""
    if not Path(STATE_FILE).exists():
        return 0
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return int(data.get("last_index", 0))
    except Exception:
        return 0


def save_state(index: int) -> None:
    """Upisuje last_index u STATE_FILE."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_index": index}, f, ensure_ascii=False, indent=2)


def fetch_html(url: str):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)

            if r.status_code == 200:
                return r.text

            if r.status_code == 429:
                sleep = min(90, random.uniform(5, 15) * attempt)
                print(f"⚠️ 429 → sleep {sleep:.1f}s")
                time.sleep(sleep)
                continue

            if 500 <= r.status_code < 600:
                sleep = 4 + attempt * 3
                print(f"⚠️ {r.status_code} → sleep {sleep}s")
                time.sleep(sleep)
                continue

            print(f"❌ HTTP {r.status_code} {url}")
            return None

        except Exception as e:
            sleep = 4 + attempt * 3
            print(f"❌ Network error {e} → sleep {sleep}s")
            time.sleep(sleep)

    return None


def extract_dates(doc: html.HtmlElement):
    """Pokušaj izvlačenja datuma iz header/template polja."""
    try:
        pub_raw = doc.xpath(XPATH_PUBLISHED)
        upd_raw = doc.xpath(XPATH_UPDATED)

        pub = pub_raw[0].text_content().strip() if pub_raw else ""
        upd = upd_raw[0].text_content().strip() if upd_raw else ""

        pub = clean_spaces(pub.replace("Publication", "").replace("Updated", ""))
        upd = clean_spaces(upd.replace("Publication", "").replace("Updated", ""))

        date_pattern = r"\d{1,2} \w+ 20\d{2}"

        if not re.search(date_pattern, pub):
            pub = ""

        if not re.search(date_pattern, upd):
            upd = ""

        return pub, upd

    except Exception:
        return "", ""


def extract_content(doc: html.HtmlElement) -> str:
    """
    Ekstrahuje GLAVNI tekst članka:
      - gleda <main><article> kao osnovni blok
      - prolazi kroz p/h2/h3/li u redosledu
      - filtrira smeće (share, related, footer, press officer...)
      - prekida kada naiđe na STOP_PHRASES
      - deduplikuje linije
      - primenjuje global_clean na kraju
    """
    article_nodes = doc.xpath("//main//article")
    if not article_nodes:
        article_nodes = doc.xpath("//article")

    root = article_nodes[0] if article_nodes else doc
    lines = []
    seen_lines = set()

    for el in root.iter():

        if not hasattr(el, "tag"):
            continue

        if not isinstance(el.tag, str):
            continue

        tag = (el.tag or "").lower()
        if tag not in ("p", "h2", "h3", "li"):
            continue

        txt = el.text_content().strip()
        if not txt:
            continue

        if any(txt.startswith(stop) for stop in STOP_PHRASES):
            break

        if any(skip in txt for skip in SKIP_LINES):
            continue

        txt = clean_spaces(txt)

        if is_footer_date(txt):
            continue

        if not txt:
            continue

        if txt in seen_lines:
            continue
        seen_lines.add(txt)

        if tag in ("h2", "h3"):
            lines.append(txt)
        elif tag == "li":
            lines.append(f"- {txt}")
        else:
            lines.append(txt)

    return global_clean("\n\n".join(lines))


def main():

    if TEST_LIMIT:
        print(f"TEST MODE: limit = {TEST_LIMIT} URL-ova")
        print(f"Output: {OUTPUT_FILE}")
    else:
        print("FULL CRAWL MODE (bez limita)")
        print(f"Output: {OUTPUT_FILE}")

    if not Path(INPUT_URLS_FILE).exists():
        print("INPUT not found:", INPUT_URLS_FILE)
        return

    with open(INPUT_URLS_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)

    items = raw.get("items", [])
    total_items = len(items)

    if total_items == 0:
        print(" Nema items u ulaznom fajlu.")
        return

    print(f"✔ Učitan fajl {INPUT_URLS_FILE} | ukupno URL-ova: {total_items}")

    start_index = load_state()
    if start_index >= total_items:
        print(f"STATE ({start_index}) >= total_items ({total_items}) → ništa za rad.")
        return

    mode = "a" if Path(OUTPUT_FILE).exists() and start_index > 0 else "w"
    fout = open(OUTPUT_FILE, mode, encoding="utf-8")

    print(f"▶ Krećem od indexa {start_index} (0-based). Output mode: {mode}")

    success_count = 0
    fail_count = 0
    processed_in_this_run = 0

    for idx in range(start_index, total_items):

        if TEST_LIMIT and processed_in_this_run >= TEST_LIMIT:
            print(f"\n Test limit dostignut: {TEST_LIMIT} URL-ova")
            save_state(idx)
            break

        obj = items[idx]
        url = obj.get("url")

        print(
            f"\n[{processed_in_this_run + 1}/{TEST_LIMIT if TEST_LIMIT else total_items}] Fetching: {url}"
        )

        html_text = fetch_html(url)

        if not html_text:
            obj["success"] = False
            obj["content"] = ""
            obj["date_published"] = ""
            obj["date_updated"] = ""
            obj["error"] = "fetch_failed"
            fail_count += 1
        else:
            try:
                doc = html.fromstring(html_text)
            except Exception as e:
                obj["success"] = False
                obj["content"] = ""
                obj["date_published"] = ""
                obj["date_updated"] = ""
                obj["error"] = f"html_parse_error: {e}"
                fail_count += 1
            else:
                pub, upd = extract_dates(doc)
                content = extract_content(doc)

                obj["date_published"] = pub
                obj["date_updated"] = upd
                obj["content"] = content
                obj["success"] = bool(content)
                obj["error"] = None if content else "empty_content"

                if obj["success"]:
                    success_count += 1
                else:
                    fail_count += 1

        fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
        fout.flush()

        save_state(idx + 1)
        processed_in_this_run += 1

        time.sleep(random.uniform(0.3, 0.9))

    fout.close()

    print("\n" + "=" * 50)
    if TEST_LIMIT:
        print("🎉 TEST CRAWL FINISHED")
    else:
        print("🎉 FULL CRAWL FINISHED")
    print("=" * 50)
    print(f"Output file: {OUTPUT_FILE}")
    print(" Statistika ove sesije:")
    print(f"   ✔ success: {success_count}")
    print(f"   ✖ fail:    {fail_count}")
    print(f"   Σ processed: {processed_in_this_run}")
    print(
        f" Ukupno do sada (sa state-om): {start_index + processed_in_this_run}/{total_items}"
    )

    if TEST_LIMIT and (start_index + processed_in_this_run) < total_items:
        print("Za full crawl, postavi TEST_LIMIT = None i pokreni ponovo")
        print(
            f"State je sačuvan, nastavlja se od indexa {start_index + processed_in_this_run}"
        )


if __name__ == "__main__":
    main()
