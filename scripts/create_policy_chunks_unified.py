from weaviate_client import WVT


def create_policy_chunks_unified():
    print(" Proveravam da li klasa već postoji...")

    schema = WVT.schema.get()
    existing_classes = [c["class"] for c in schema.get("classes", [])]

    if "PolicyChunksUnified" in existing_classes:
        print(
            " Klasa PolicyChunksUnified već postoji! Pre brisanja proveri da li si siguran."
        )
        return

    print(" Kreiram klasu PolicyChunksUnified...")

    class_obj = {
        "class": "PolicyChunksUnified",
        "description": "Unified policy chunks from multiple sources",
        "vectorizer": "text2vec-weaviate",
        "moduleConfig": {
            "text2vec-weaviate": {
                "baseURL": "https://api.embedding.weaviate.io",
                "model": "Snowflake/snowflake-arctic-embed-l-v2.0",
                "truncate": "right",
                "vectorizeClassName": False,
            }
        },
        "properties": [
            {
                "name": "text",
                "dataType": ["text"],
                "description": "Chunk text",
            },
            {
                "name": "title",
                "dataType": ["text"],
                "description": "Article title",
            },
            {
                "name": "url",
                "dataType": ["text"],
                "description": "Link to original content",
            },
            {
                "name": "source",
                "dataType": ["text"],
                "description": "Source identifier (digwatch, ietf.org, eu-news)",
            },
            {
                "name": "origin_site",
                "dataType": ["text"],
                "description": "Original website or system",
            },
            {
                "name": "date",
                "dataType": ["date"],
                "description": "ISO date",
            },
            {
                "name": "quarter",
                "dataType": ["text"],
                "description": "Quarter (e.g., 2025-Q2)",
            },
            {
                "name": "categories",
                "dataType": ["text[]"],
                "description": "List of categories",
            },
            {
                "name": "tags",
                "dataType": ["text[]"],
                "description": "List of tags",
            },
        ],
    }

    WVT.schema.create_class(class_obj)

    print(" Klasa PolicyChunksUnified uspešno kreirana!")


if __name__ == "__main__":
    create_policy_chunks_unified()
