import json
from pathlib import Path

ITU_RULES = {
    # 1) AI / veštačka inteligencija
    "Artificial intelligence": [
        " artificial intelligence",
        " artificial-intelligence",
        " ai ",
        " ai,",
        " ai.",
        " ai-",
        "(ai",
        "ai)",
        " ai4good",
        " ai for good",
        " machine learning",
        " ml model",
        " ml ",
    ],
    # 2) Digital infrastructure
    "Digital infrastructure": [
        " network",
        " networks",
        " infrastructure",
        " backbone",
        " broadband",
        " 3g",
        " 4g",
        " 5g",
        " 6g",
        " imt-2020",
        " imt 2020",
        " base station",
        " base stations",
        " optical transport",
        " optical network",
        " optical fibre",
        " optical fiber",
        " passive optical network",
        " pon ",
        " ftth",
        " otn ",
        " transport network",
        " fronthaul",
        " backhaul",
        " radiocommunication",
        " radio communication",
        " radio spectrum",
        " spectrum ",
        " frequency band",
        " frequency bands",
        " satellite link",
        " satellite links",
        " earth station",
        " telecommunication network",
        " telecom network",
        " ict infrastructure",
    ],
    # 3) International standards
    "International standards": [
        " itu-t ",
        " itu-r ",
        " recommendation ",
        " recommendations ",
        " standardization",
        " standardisation",
        " international standard",
        " international standards",
        " technical standard",
        " technical standards",
        " g.709",
        " g.980",
        " g.9802",
        " g.9804",
        " study group 15",
        " study group 13",
        " sg15",
        " sg 15",
        " sg13",
        " sg 13",
        " iso ",
        " iec ",
        " joint statement",
        " standards meeting",
        " standards body",
        " standards bodies",
        " itu world radiocommunication conference",
        " wrc-",
    ],
    # 4) Digital inclusion
    "Digital inclusion": [
        " digital inclusion",
        " inclusive digital",
        " inclusion ",
        " leave no one behind",
        " unconnected",
        " underserved",
        " under-served",
        " remote community",
        " remote communities",
        " rural community",
        " rural communities",
        " low-income",
        " marginalized",
        " marginalized groups",
        " refugees",
        " refugee ",
        " displaced people",
        " forcibly displaced",
        " host community",
        " host communities",
        " global south",
    ],
    # 5) Digital skills & Education
    "Digital skills & Education": [
        " digital skills",
        " skills development",
        " skill development",
        " capacity building",
        " capacity-building",
        " training course",
        " training programmes",
        " training programs",
        " online training",
        " e-learning",
        " education ",
        " educational ",
        " curriculum",
        " school connectivity",
        " schools ",
        " teachers ",
        " students ",
        " youth skills",
        " steam education",
        " steam azerbaijan",
        " digital literacy",
        " ict skills",
    ],
    # 6) Digital accessibility
    "Digital accessibility": [
        " digital accessibility",
        " accessible ict",
        " ict accessibility",
        " accessibility ",
        " accessible ",
        " assistive technology",
        " assistive technologies",
        " persons with disabilities",
        " people with disabilities",
        " disability ",
        " disabilities ",
        " screen reader",
        " screen-reader",
        " captioning",
        " sign language",
        " universal design",
    ],
    # 7) Human rights & inclusion
    "Human rights & inclusion": [
        " human rights",
        " rights-based",
        " fundamental rights",
        " modern slavery",
        " forced labour",
        " forced labor",
        " child labour",
        " child labor",
        " human trafficking",
        " trafficking in persons",
        " discrimination",
        " equality ",
        " non-discrimination",
        " dignity ",
        " vulnerable groups",
        " inclusive societies",
    ],
    # 9) Cybersecurity – striktno cyber
    "Cybersecurity": [
        " cybersecurity",
        " cyber security",
        " cyber-attack",
        " cyber attack",
        " cybercrime",
        " cyber-crime",
        " cyber threat",
        " cyber threats",
        " malware",
        " ransomware",
        " phishing",
        " botnet",
        " intrusion",
        " security breach",
        " data breach",
    ],
    # 10) Maritime & oceans
    "Maritime & oceans": [
        " maritime ",
        " imo ",
        " ship ",
        " ships ",
        " shipping ",
        " vessel ",
        " vessels ",
        " port ",
        " ports ",
        " ocean ",
        " oceans ",
        " sea ",
        " seas ",
        " gmdss",
        " maritime safety",
        " maritime distress",
    ],
    # 11) Space & satellite
    "Space & satellite": [
        " satellite ",
        " satellites ",
        " earth observation",
        " earth-observation",
        " iss ",
        " international space station",
        " nasa ",
        " esa ",
        " jaxa ",
        " orbital ",
        " orbit ",
        " space science",
    ],
    # 12) Digital policy & governance
    "Digital policy & governance": [
        " policy ",
        " policies ",
        " regulatory",
        " regulation",
        " regulations",
        " regulator ",
        " regulators ",
        " governance",
        " framework",
        " frameworks",
        " national strategy",
        " digital strategy",
        " policy makers",
        " policymakers",
        " minister ",
        " ministry ",
        " government strategy",
    ],
}

ALWAYS_CATEGORIES = ["ITU", "News article"]


def detect_categories(title: str, text: str):
    combined = f"{title} {text}".lower()
    found = []

    for category, keywords in ITU_RULES.items():
        for kw in keywords:
            if kw in combined:
                found.append(category)
                break

    return sorted(set(found))


INPUT = Path("../../data/processed/itu_news_paragraphs_v3_pro.jsonl")
OUTPUT = Path("../../data/processed/itu_news_paragraphs_enriched.jsonl")


def main():
    print("Loading ITU paragraph JSONL...")

    with INPUT.open("r", encoding="utf-8") as infile, OUTPUT.open(
        "w", encoding="utf-8"
    ) as outfile:

        count = 0

        for line in infile:
            line = line.strip()
            if not line:
                continue

            obj = json.loads(line)

            title = obj.get("title", "") or ""
            text = obj.get("text", "") or ""

            auto_cats = detect_categories(title, text)

            all_cats = sorted(set(ALWAYS_CATEGORIES + auto_cats))

            obj["categories"] = all_cats
            obj["tags"] = []

            outfile.write(json.dumps(obj, ensure_ascii=False) + "\n")
            count += 1

    print("✓ Enriched ITU fajl je napravljen.")
    print(f"Output: {OUTPUT}")
    print(f"Ukupno obrađeno: {count} paragrafa.")


if __name__ == "__main__":
    main()
