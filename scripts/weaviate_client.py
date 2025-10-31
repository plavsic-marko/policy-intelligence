# weaviate_client.py
import os
import weaviate
from dotenv import load_dotenv

load_dotenv()

weaviate_url = os.getenv("WEAVIATE_URL")
api_key = os.getenv("WEAVIATE_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

if not weaviate_url:
    raise ValueError("WEAVIATE_URL nije definisan u .env fajlu")

if api_key:
    auth = weaviate.AuthApiKey(api_key=api_key)
    WVT = weaviate.Client(
        url=weaviate_url,
        auth_client_secret=auth,
        additional_headers={
            "X-OpenAI-Api-Key": openai_key  # dodaj OpenAI ključ za text2vec-openai
        }
    )
else:
    WVT = weaviate.Client(
        url=weaviate_url,
        additional_headers={
            "X-OpenAI-Api-Key": openai_key
        }
    )
