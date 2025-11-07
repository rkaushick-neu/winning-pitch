# portfolio_ingest.py
from qdrant_client import QdrantClient
from openai import OpenAI
import requests, re, os
from bs4 import BeautifulSoup

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text: str):
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return response.data[0].embedding

def ingest_portfolio():
    # qdrant_client = QdrantClient(":memory:")  # or your local instance
    soup = BeautifulSoup(requests.get("https://www.boxone.xyz/portfolio").text, "html.parser")

    entries = []
    for card in soup.select("div#portfolio-list div.portfolio-homepage-item-wrapper"):
        a_tag = card.find("a")
        link = a_tag["href"]
        name = a_tag.get_text(strip=True)
        if not name:
            name = link.rstrip("/").split("/")[-1]
        desc = a_tag.get("title", "").strip()
        entries.append({"name": name, "desc": desc, "url": link})

    # Print entries to verify scraping
    for entry in entries:
        print(entry)

    # # create embeddings & upsert to Qdrant
    # for e in entries:
    #     embedding = get_embedding(e["desc"])
    #     qdrant_client.upsert(
    #         collection_name="boxone_portfolio",
    #         points=[{
    #             "id": e["name"],
    #             "vector": embedding,
    #             "payload": {"name": e["name"], "url": e["url"], "desc": e["desc"], "invested": True}
    #         }]
    #     )

ingest_portfolio()