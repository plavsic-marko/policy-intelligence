import json
from pathlib import Path

IETF_RULES = {
    "Artificial intelligence": [
        " ai ",
        "artificial intelligence",
        "machine learning",
        "aipref",
        "ai crawler",
        "ai governance",
        "ai standards",
    ],
    "Internet standards": [
        "yang",
        "semver",
        "internet-draft",
        "internet draft",
        "rfc",
        "standard",
    ],
    "Cybersecurity": [
        "security",
        "tls",
        "encryption",
        "certificate",
        "dnssec",
        "vulnerability",
        "attack",
        "secure ",
    ],
    "Network infrastructure": [
        "infrastructure",
        "network",
        "routing",
        "ipv6",
        "protocol",
        "transport",
        "cloud infrastructure",
        "service window",
        "service outage",
    ],
    "IETF governance": [
        "governance",
        "multistakeholder",
        "internet governance",
        "wsis",
    ],
    "IETF events": ["ietf ", "ietf 12", "igf", "wsis", "meeting"],
    "Web governance": ["crawler", "crawling", "robots", "ai-pref"],
    "Content policy": ["content moderation", "publisher", "publication", "policy"],
    "Technical operations": [
        "maintenance",
        "service window",
        "datatracker",
        "imap",
        "rsync",
        "service outage",
        "authentication service",
    ],
}

ALWAYS_TAGS = ["IETF", "Technical article"]


def detect_categories(title: str, text: str):
    combined = f"{title} {text}".lower()
    found = []

    for category, keywords in IETF_RULES.items():
        for kw in keywords:
            if kw in combined:
                found.append(category)
                break

    return list(set(found))


INPUT = Path("../../data/raw/ietf/ietf_articles_all.jsonl")
OUTPUT = Path("../../data/processed/ietf_articles_enriched.jsonl")


def main():
    print("Loading crawled IETF JSONL...")

    with INPUT.open("r", encoding="utf-8") as infile, OUTPUT.open(
        "w", encoding="utf-8"
    ) as outfile:

        count = 0

        for line in infile:
            line = line.strip()
            if not line:
                continue

            obj = json.loads(line)

            title = obj.get("title", "")
            text = (
                obj.get("text_content")
                or obj.get("html_content")
                or obj.get("text")
                or ""
            )

            auto_cats = detect_categories(title, text)
            all_cats = list(set(auto_cats + ALWAYS_TAGS))

            obj["categories"] = all_cats
            obj["tags"] = []

            outfile.write(json.dumps(obj, ensure_ascii=False) + "\n")
            count += 1

    print("✓ Enriched IETF fajl je napravljen.")
    print(f"Output: {OUTPUT}")
    print(f"Ukupno obrađeno: {count} članaka.")


if __name__ == "__main__":
    main()
