import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.weaviate_client import WVT

QUESTION = "What happened with AI governance at the UN level in 2024?"

query = f"""
{{
  Get {{
    PolicyChunksUnified(
      hybrid: {{
        query: "{QUESTION}",
        alpha: 0.5
      }},
      limit: 5
    ) {{
      text
      url
      origin_site
      _additional {{
        score
        id
      }}
    }}
  }}
}}
"""

print("\n Šaljem HYBRID query...")
response = WVT.query.raw(query)

print("\n--- REZULTAT ---")
for item in response["data"]["Get"]["PolicyChunksUnified"]:
    print(f"\n• SCORE: {item['_additional']['score']}")
    print(f"  SITE:  {item['origin_site']}")
    print(f"  URL:   {item['url']}")
    print(f"  TEXT:  {item['text'][:300]}...")
    print("-" * 40)
