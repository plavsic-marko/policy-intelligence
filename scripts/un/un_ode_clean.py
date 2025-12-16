import json
import re

INPUT_FILE = "un_ode_news_full.jsonl"
OUTPUT_FILE = "un_ode_news_clean.jsonl"


def clean_un_ode_text(text):

    lines = text.split("\n")

    cleaned_lines = []
    seen = set()

    for line in lines:
        original = line.strip()

        if not original:
            continue

        if original.lower().startswith("learn more"):
            continue
        if "see more recent news" in original.lower():
            continue

        if "media contact" in original.lower():
            continue
        if "media inquiries" in original.lower():
            continue
        if "for media inquiries" in original.lower():
            continue

        if re.match(r"https?://\S+", original):
            continue

        if original not in seen:
            cleaned_lines.append(original)
            seen.add(original)

    cleaned_text = "\n\n".join(cleaned_lines)

    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)

    return cleaned_text


def main():
    print("🧹 Cleaning UN ODET articles...")

    with open(INPUT_FILE, "r", encoding="utf-8") as f_in, open(
        OUTPUT_FILE, "w", encoding="utf-8"
    ) as f_out:

        for line in f_in:
            item = json.loads(line)

            cleaned = clean_un_ode_text(item["text"])
            item["text"] = cleaned

            f_out.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(" Cleaning complete!")
    print(f" Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
