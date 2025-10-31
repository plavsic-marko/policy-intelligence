import os
import requests
from dotenv import load_dotenv

# Učitaj .env fajl iz root foldera
load_dotenv()

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
API_KEY = os.getenv("WEAVIATE_API_KEY")

if not WEAVIATE_URL or not API_KEY:
    raise RuntimeError(
        "Nisam našao WEAVIATE_URL ili WEAVIATE_API_KEY u .env fajlu.")

headers = {"Authorization": f"Bearer {API_KEY}"}


def delete_class(class_name: str):
    url = f"{WEAVIATE_URL}/v1/schema/{class_name}"
    r = requests.delete(url, headers=headers, timeout=30)
    print(f"Brisanje klase {class_name}: {r.status_code} {r.text[:200]}")


# 1) Prikaz trenutne šeme
r = requests.get(f"{WEAVIATE_URL}/v1/schema", headers=headers, timeout=20)
print("Pre brisanja:", r.status_code, r.text[:200])

# 2) Brisanje klasa (ako postoje)
for cls in ["DigwatchParagraph", "DigwatchUpdate"]:
    delete_class(cls)

# 3) Ponovna provera
r = requests.get(f"{WEAVIATE_URL}/v1/schema", headers=headers, timeout=20)
print("Posle brisanja:", r.status_code, r.text[:200])
