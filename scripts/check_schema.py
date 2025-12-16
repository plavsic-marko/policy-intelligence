import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from scripts.weaviate_client import WVT


def check_schemas():
    print("🔍 Provera Weaviate shema...")

    try:

        classes = WVT.schema.get()
        print(" Dostupne klase:")
        for cls in classes["classes"]:
            print(f"   - {cls['class']}")

        print("\n" + "=" * 80)

        for cls in classes["classes"]:
            class_name = cls["class"]
            schema = WVT.schema.get(class_name)
            print(f"\n SCHEMA za: {class_name}")
            print(f"   Vectorizer: {schema.get('vectorizer', ' NEMA')}")

            vectorizer_config = schema.get("moduleConfig", {})
            if vectorizer_config:
                print(
                    f"   Vectorizer config: {json.dumps(vectorizer_config, indent=6)}"
                )

            print("    Properties:")
            for prop in schema.get("properties", []):
                module_config = prop.get("moduleConfig", {})
                vectorize = (
                    "🔹 EMBEDDING"
                    if module_config.get("text2vec-openai")
                    or module_config.get("text2vec-cohere")
                    else "🔸 NO EMBEDDING"
                )
                print(f"      - {prop['name']} ({prop['dataType'][0]}) - {vectorize}")

    except Exception as e:
        print(f" Greška: {e}")


if __name__ == "__main__":
    check_schemas()
