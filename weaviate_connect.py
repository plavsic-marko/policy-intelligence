import weaviate
import os
from dotenv import load_dotenv

load_dotenv()

client = weaviate.Client(
    url=os.getenv("WEAVIATE_URL"),
    auth_client_secret=weaviate.AuthApiKey(
        api_key=os.getenv("WEAVIATE_API_KEY")
    )
)

print("Ping:", client.is_ready())
