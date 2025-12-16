# scripts/create_schema_ietf.py
from scripts.weaviate_client import WVT


def class_exists(name: str) -> bool:
    schema = WVT.schema.get() or {}
    return any(c.get("class") == name for c in schema.get("classes", []))


def ensure_class_ietf_article_chunks():
    name = "IETF_ArticleChunks"
    if class_exists(name):
        print(f"[=] {name} već postoji (skip create).")
        return

    WVT.schema.create_class(
        {
            "class": name,
            "description": "Paragraph-level chunks from IETF blog articles, with metadata.",
            "vectorizer": "text2vec-weaviate",
            "moduleConfig": {"text2vec-weaviate": {"vectorizeClassName": False}},
            "properties": [
                {"name": "source", "dataType": ["text"]},
                {"name": "url", "dataType": ["text"]},
                {"name": "title", "dataType": ["text"]},
                {"name": "author", "dataType": ["text"]},
                {"name": "section_title", "dataType": ["text"]},
                {"name": "subsection_title", "dataType": ["text"]},
                {"name": "text", "dataType": ["text"]},
                {"name": "node_type", "dataType": ["text"]},
                {"name": "quarter", "dataType": ["text"]},
                {"name": "effective_date", "dataType": ["date"]},
                {"name": "topics", "dataType": ["text[]"]},
            ],
        }
    )
    print(f"[+] Kreirana klasa {name}")


def main():
    ensure_class_ietf_article_chunks()
    print("[OK] IETF schema ensured (bez brisanja).")


if __name__ == "__main__":
    main()
