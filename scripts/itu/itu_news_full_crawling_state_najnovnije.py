import json
import random
import re
import time
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# ----------------------------------------
# CONFIG
# ----------------------------------------

INPUT_FILE = "itu_all_urls.jsonl"
OUTPUT_FILE = "itu_all_clean.jsonl"
STATE_FILE = "itu_state.json"  # <--- DODATO (state resume)
TEST_LIMIT = None  # None = full crawl

SKIP_LINES = [
    "Share on Facebook",
    "Share on Twitter",
    "Share on LinkedIn",
    "Share via URL",
    "Subscribe to our newsletter",
    "Home",
    "News",
]

STOP_PHRASES = [
    "Header image credit",
    "Related content",
    "Related links",
    "Read more",
    "Read the Seoul Statement",
]

GLOBAL_REMOVE_PATTERNS = [
    r"^\s*Home\s*$",
    r"^\s*News\s*$",
    r"\s*Subscribe to our newsletter.*?$",
    r"Share on (Facebook|Twitter|LinkedIn|WhatsApp|Email).*?$",
    r"^\s*-\s*Home\s*$",
    r"^\s*-\s*News\s*$",
]

DATE_XPATH = '//*[@id="content"]/div/div[2]/div/div[1]/article/div[1]/div[1]/span'


def load_state() -> int:
    """Returns the index from which we should resume crawling."""
    if not Path(STATE_FILE).exists():
        return 0
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return int(data.get("last_index", 0))
    except Exception:
        return 0


def save_state(index: int) -> None:
    """Saves the last processed index."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_index": index}, f, ensure_ascii=False, indent=2)


def clean_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def global_clean(text: str) -> str:
    cleaned = text
    for p in GLOBAL_REMOVE_PATTERNS:
        cleaned = re.sub(p, "", cleaned, flags=re.MULTILINE | re.DOTALL)
    cleaned = re.sub(r"\n\s*\n\s*\n+", "\n\n", cleaned)
    return cleaned.strip()


def get_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--log-level=3")
    return webdriver.Chrome(options=opts)


def extract_date(driver) -> str:
    try:
        el = driver.find_element(By.XPATH, DATE_XPATH)
        return el.text.strip()
    except Exception:
        return ""


def extract_content(html):
    soup = BeautifulSoup(html, "html.parser")

    main = soup.find("main")
    if not main:
        return ""

    lines = []
    seen = set()

    for tag in main.find_all(["p", "h2", "h3", "li"]):

        txt = tag.get_text(" ", strip=True)
        if not txt:
            continue

        if any(txt.startswith(stop) for stop in STOP_PHRASES):
            break

        if txt in SKIP_LINES:
            continue

        txt = clean_spaces(txt)
        if txt in seen:
            continue
        seen.add(txt)

        if tag.name in ("h2", "h3"):
            lines.append(txt)
        elif tag.name == "li":
            lines.append(f"- {txt}")
        else:
            lines.append(txt)

    return global_clean("\n\n".join(lines))


def main():
    print("STARTING FULL ITU CRAWL")

    if not Path(INPUT_FILE).exists():
        print("Nema ulaznog fajla:", INPUT_FILE)
        return

    urls = []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            urls.append(json.loads(line))

    total = len(urls)
    limit = total if TEST_LIMIT is None else min(TEST_LIMIT, total)

    start_index = load_state()
    print(f"▶ Nastavljam od indexa: {start_index}")

    mode = "a" if start_index > 0 and Path(OUTPUT_FILE).exists() else "w"
    fout = open(OUTPUT_FILE, mode, encoding="utf-8")

    driver = get_driver()

    for i in range(start_index, limit):
        obj = urls[i]
        url = obj["url"]

        print(f"[{i+1}/{limit}] Fetch → {url}")

        try:
            driver.get(url)
            time.sleep(2.3)

            date_str = extract_date(driver)
            html = driver.page_source

        except Exception as e:
            fout.write(
                json.dumps(
                    {
                        "url": url,
                        "success": False,
                        "error": f"selenium_error: {e}",
                        "date": "",
                        "content": "",
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            fout.flush()
            save_state(i + 1)
            continue

        content = extract_content(html)

        fout.write(
            json.dumps(
                {
                    "url": url,
                    "success": bool(content),
                    "error": None if content else "empty_content",
                    "date": date_str,
                    "content": content,
                },
                ensure_ascii=False,
            )
            + "\n"
        )

        fout.flush()
        save_state(i + 1)
        time.sleep(random.uniform(0.5, 1.2))

    fout.close()
    driver.quit()

    print("\nFULL CRAWL FINISHED!")
    print("Sačuvano u:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
