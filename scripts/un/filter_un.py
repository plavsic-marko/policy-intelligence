import json

INPUT_FILE = "../../data/processed/un_ode_news_chunks.jsonl"
OUTPUT_FILE = "../../data/processed/un_ode_filtered.jsonl"


def is_valid(chunk):
    text = chunk.get("text", "").lower()
    categories = " ".join(chunk.get("categories", [])).lower()

    keep_keywords = [
        "press release",
        "ai governance",
        "global digital compact",
        "digital public infrastructure",
        "un events",
        "advisory body",
        "oecd",
    ]

    drop_keywords = [
        "linkedin",
        "followers",
        "#worldaidsday",
        "podcast",
        "read more",
        "non-profit",
        "careers",
        "locations",
    ]

    if any(x in text for x in drop_keywords):
        return False

    if any(x in categories or x in text for x in keep_keywords):
        return True

    return False


kept = 0
removed = 0

with open(INPUT_FILE, "r", encoding="utf-8") as infile, open(
    OUTPUT_FILE, "w", encoding="utf-8"
) as outfile:
    for line in infile:
        chunk = json.loads(line)
        if is_valid(chunk):
            outfile.write(json.dumps(chunk, ensure_ascii=False) + "\n")
            kept += 1
        else:
            removed += 1

print(f" Zadržano: {kept}")
print(f"🗑 Izbačeno: {removed}")
