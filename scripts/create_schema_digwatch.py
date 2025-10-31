from scripts.weaviate_client import WVT


def drop(name: str):
    try:
        WVT.schema.delete_class(name)
    except Exception:
        pass


def main():
    # prvo obriši ako već postoje
    for cls in ["DigwatchParagraph", "DigwatchUpdate"]:
        drop(cls)

    # Klasa za update (meta info)
    WVT.schema.create_class({
        "class": "DigwatchUpdate",
        "description": "One update (article) from dig.watch",
        "vectorizer": "text2vec-openai",
        "moduleConfig": {
            "text2vec-openai": {"model": "text-embedding-3-small"}
        },
        "properties": [
            {"name": "url", "dataType": ["text"], "tokenization": "field"},
            {"name": "title", "dataType": ["text"]},
            {"name": "date", "dataType": ["text"]},
            {"name": "modified", "dataType": ["text"]},
            {"name": "effective_date", "dataType": ["text"]},
            {"name": "quarter", "dataType": ["text"]},
            {"name": "category_names", "dataType": ["text[]"]},
            {"name": "tag_names", "dataType": ["text[]"]},
            {"name": "source", "dataType": ["text"]},
        ]
    })

    # Klasa za pasuse (chunkovi)
    WVT.schema.create_class({
        "class": "DigwatchParagraph",
        "description": "Paragraph-level chunk from dig.watch updates",
        "vectorizer": "text2vec-openai",
        "moduleConfig": {
            "text2vec-openai": {"model": "text-embedding-3-small"}
        },
        "properties": [
            {"name": "url", "dataType": ["text"], "tokenization": "field"},
            {"name": "title", "dataType": ["text"]},
            {"name": "section_title", "dataType": ["text"]},
            {"name": "subsection_title", "dataType": ["text"]},
            {"name": "text", "dataType": ["text"]},
            {"name": "node_type", "dataType": ["text"]},
            {"name": "updateRef", "dataType": ["DigwatchUpdate"]},
        ]
    })

    print("✅ Weaviate schema ready: DigwatchUpdate + DigwatchParagraph")


if __name__ == "__main__":
    main()
