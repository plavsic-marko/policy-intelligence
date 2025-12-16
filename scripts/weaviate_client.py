import os

import weaviate
from dotenv import load_dotenv

load_dotenv()

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
API_KEY = os.getenv("WEAVIATE_API_KEY")


if not WEAVIATE_URL:
    raise ValueError(" Nedostaje WEAVIATE_URL u .env fajlu")
if not API_KEY:
    raise ValueError(" Nedostaje WEAVIATE_API_KEY u .env fajlu")


WVT = weaviate.Client(
    url=WEAVIATE_URL,
    auth_client_secret=weaviate.AuthApiKey(API_KEY),
    additional_headers={"X-Weaviate-Cluster-Url": WEAVIATE_URL},
)
