import json
import re
import time
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://digital-strategy.ec.europa.eu"
START_URL = f"{BASE}/en/news"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


STATE_FILE = "eu_news_collector_state.json"


class EUFullNewsCollectorWithState:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = HEADERS
        self.items = []
        self.seen_urls = set()
        self.state = self._load_state()

    def _load_state(self):
        """Učitava state ako postoji, inače kreira novi"""
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
                print(f"🔄 NASTAVLJAM SA STRANE {state.get('current_page', 0) + 1}")
                return state
        except FileNotFoundError:
            print("🆕 POKREĆEM OD POČETKA")
            return {
                "current_page": 0,
                "total_collected": 0,
                "last_successful_page": 0,
                "started_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
            }

    def _save_state(self):
        """Čuva trenutni state"""
        self.state.update(
            {
                "current_page": self.state.get("current_page", 0),
                "total_collected": len(self.items),
                "last_updated": datetime.now().isoformat(),
                "items_count": len(self.items),
            }
        )

        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def _save_checkpoint(self):
        """Čuva checkpoint sa podacima i state-om"""
        checkpoint_data = {
            "state": self.state,
            "items": self.items,
            "checkpoint_at": datetime.now().isoformat(),
        }

        checkpoint_file = f"checkpoint_page_{self.state['current_page']}.json"
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)

        print(f"💾 Checkpoint sačuvan: {checkpoint_file}")

    def _get_soup(self, url, retry_label=""):
        """Stabilan HTTP sa pametnim rate-limit retry mehanizmom."""
        for attempt in range(5):
            try:
                r = self.session.get(url, timeout=20)

                if r.status_code == 429:
                    wait = (attempt + 1) * 20
                    print(f"⏳ RATE LIMIT {retry_label}! Čekam {wait}s...")
                    time.sleep(wait)
                    continue

                if r.status_code != 200:
                    print(f"⚠️ STATUS {r.status_code} → {url}")
                    return None

                return BeautifulSoup(r.text, "html.parser")

            except Exception as e:
                print(f"💥 ERROR {url}: {e}")
                time.sleep(10)

        return None

    def _extract_date_and_type(self, link_element):
        """Ekstrakcija datuma i tipa vesti sa listinga."""
        parent = link_element.parent
        if not parent:
            return None, "News article"

        txt = parent.get_text(" ", strip=True)

        # datum
        date_pattern = r"(\d{1,2}\s+[A-Za-z]+\s+\d{4})"
        date_match = re.search(date_pattern, txt)
        date = date_match.group(1) if date_match else None

        type_pattern = r"\b(Digibyte|Press release|Opinion|Projects story)\b"
        type_match = re.search(type_pattern, txt, re.IGNORECASE)
        news_type = type_match.group(1) if type_match else "News article"

        return date, news_type

    def collect_all_news(self, max_empty=5, checkpoint_interval=10):
        """Puna paginacija sa state management-om."""
        print("\n STARTING FULL NEWS COLLECTION WITH STATE MANAGEMENT")
        print("========================================================")

        current_page = self.state.get("current_page", 0)
        consecutive_empty = 0
        total_before = len(self.items)

        while True:
            url = START_URL if current_page == 0 else f"{START_URL}?page={current_page}"
            print(f"🔎 Strana {current_page + 1}…", end=" ")

            soup = self._get_soup(url, retry_label=f"page {current_page + 1}")
            if not soup:
                print("❌ Kritična greška — čuvam state i prekidam.")
                self._save_state()
                break

            links = soup.select('a[href*="/en/news/"]')

            if not links:
                consecutive_empty += 1
                print(f" Prazno ({consecutive_empty}/{max_empty})")
                if consecutive_empty >= max_empty:
                    print(" Kraj — previše praznih strana.")
                    self.state["completed"] = True
                    self._save_state()
                    break
                current_page += 1
                self.state["current_page"] = current_page
                time.sleep(3)
                continue

            consecutive_empty = 0
            page_count = 0

            for link in links:
                href = link.get("href", "")
                if "/en/news/" not in href or href == "/en/news/":
                    continue

                full_url = urljoin(BASE, href)

                if full_url in self.seen_urls:
                    continue
                self.seen_urls.add(full_url)

                title = link.get_text(strip=True)
                date_listing, news_type = self._extract_date_and_type(link)

                self.items.append(
                    {
                        "url": full_url,
                        "title": title,
                        "content_type": "news",
                        "news_type": news_type,
                        "date_listing": date_listing,
                        "source_page": url,
                        "collected_at": datetime.now().isoformat(),
                    }
                )

                page_count += 1

            print(f" {page_count} novih (ukupno: {len(self.items)})")

            self.state["current_page"] = current_page
            self.state["last_successful_page"] = current_page
            self._save_state()

            if current_page % checkpoint_interval == 0:
                self._save_checkpoint()

            next_btn = soup.select_one(".ecl-pagination__item--next a, .pager-next a")
            if not next_btn:
                print("🏁 KRAJ PAGINACIJE — GOTOVO!")
                self.state["completed"] = True
                self._save_state()
                break

            current_page += 1
            time.sleep(2)

        new_items = len(self.items) - total_before
        print(f"\n📈 U ovoj sesiji: {new_items} novih vesti")
        return self.items

    def save_final(self):
        """Čuva finalne rezultate i briše state fajl."""
        filename = f"eu_news_full_{datetime.now().strftime('%Y%m%d_%H%M')}.json"

        type_stats = {}
        for item in self.items:
            t = item["news_type"]
            type_stats[t] = type_stats.get(t, 0) + 1

        out = {
            "metadata": {
                "collected_at": datetime.now().isoformat(),
                "total_urls": len(self.items),
                "urls_with_dates": len([x for x in self.items if x["date_listing"]]),
                "urls_without_dates": len(
                    [x for x in self.items if not x["date_listing"]]
                ),
                "news_by_type": type_stats,
                "base_url": BASE,
                "collection_completed": self.state.get("completed", False),
            },
            "items": self.items,
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)

        if self.state.get("completed"):
            import os

            if os.path.exists(STATE_FILE):
                os.remove(STATE_FILE)
                print(" Obrisan state fajl (završeno)")

        print(f"\n Finalni fajl: {filename}")
        print(f" Ukupno URL-ova: {len(self.items)}")

        print(" STATISTIKA TIPOVA:")
        for t, c in type_stats.items():
            print(f"   {t}: {c}")

        return filename


def main():
    collector = EUFullNewsCollectorWithState()

    start = datetime.now()
    items = collector.collect_all_news()
    filename = collector.save_final()
    end = datetime.now()

    duration = (end - start).total_seconds() / 60

    print("\n GOTOVO!")
    print(f" Trajanje: {duration:.1f} min")
    print(f" Ukupno vesti: {len(items)}")

    if collector.state.get("completed"):
        print(" KOMPLETNA ARHIVA SKINUTA!")
    else:
        print(" SKUPLJANJE PAUZIRANO - POKRENI PONOVO DA NASTAVIŠ!")


if __name__ == "__main__":
    main()
