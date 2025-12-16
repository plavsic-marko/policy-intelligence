import os

import weaviate
from dotenv import load_dotenv

load_dotenv()

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
API_KEY = os.getenv("WEAVIATE_API_KEY")

if not WEAVIATE_URL:
    raise ValueError(" Nedostaje WEAVIATE_URL u .env")
if not API_KEY:
    raise ValueError(" Nedostaje WEAVIATE_API_KEY u .env")


client = weaviate.Client(
    url=WEAVIATE_URL,
    auth_client_secret=weaviate.AuthApiKey(API_KEY),
    additional_headers={"X-Weaviate-Cluster-Url": WEAVIATE_URL},
)

CLASS = "PolicyChunksUnified"


query = (
    client.query.get(CLASS, ["_additional { id }"])
    .with_where(
        {
            "path": ["origin_site"],
            "operator": "Equal",
            "valueString": "ietf.org",
        }
    )
    .with_limit(10000)
    .do()
)

objs = query.get("data", {}).get("Get", {}).get(CLASS, [])

print(f"🗑 Brišem {len(objs)} IETF objekata...")


with client.batch as batch:
    batch.batch_size = 200
    for obj in objs:
        batch.delete_object(CLASS, obj["_additional"]["id"])

print("✔ Gotovo — svi IETF objekti obrisani.")
