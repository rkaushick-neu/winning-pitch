# from qdrant_client import QdrantClient, models
from openai import OpenAI
import uuid, os

def get_qdrant_client():
    return QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))

def get_openai_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

COLLECTION_NAME = "winning_pitch_embeddings"

qdrant = get_qdrant_client()
openai_client = get_openai_client()

def ensure_collection_exists():
    from qdrant_client.http import models as rest_models

    if COLLECTION_NAME not in [c.name for c in qdrant.get_collections().collections]:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=rest_models.VectorParams(
                size=1536,   # for OpenAI text-embedding-3-small
                distance=rest_models.Distance.COSINE
            )
        )
        print(f"Created collection: {COLLECTION_NAME}")
    else:
        print(f"Collection {COLLECTION_NAME} already exists.")

def store_in_qdrant(text, metadata):
    if not text or not text.strip():
        return

    embedding = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    ).data[0].embedding

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload=metadata
            )
        ]
    )

if __name__ == "__main__":
    ensure_collection_exists()