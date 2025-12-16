import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.weaviate_client import WVT

result = WVT.query.raw(
    """
{
  Aggregate {
    PolicyChunksUnified {
      meta {
        count
      }
    }
  }
}
"""
)

count = result["data"]["Aggregate"]["PolicyChunksUnified"][0]["meta"]["count"]
print(f" PolicyChunksUnified ima {count} chunkova")


result = (
    WVT.query.get("PolicyChunksUnified", ["text", "origin_site", "_additional {id}"])
    .with_limit(3)
    .do()
)

print(" Primeri chunkova:")
for i, item in enumerate(result["data"]["Get"]["PolicyChunksUnified"]):
    site = item.get("origin_site", "N/A")
    text_preview = item.get("text", "")[:80] + "..."
    print(f"{i+1}. [{site}] {text_preview}")
