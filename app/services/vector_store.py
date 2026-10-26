# app/services/vector_store.py
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.core.ai_client import generate_embedding

COLLECTION_NAME = "pharma_sops"
VECTOR_DIMENSION = 768  # nomic-embed-text outputs 768 dimensions

# Local disk persistence storage folder for Qdrant
STORAGE_DIR = Path("data/qdrant_db")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Initialize Qdrant Client (Uses persistent local disk storage - zero Docker startup required!)
client = QdrantClient(path=str(STORAGE_DIR))


def init_vector_collection():
    """
    Creates the 'pharma_sops' collection if it doesn't already exist.
    Uses Cosine distance for semantic similarity.
    """
    collections = client.get_collections().collections
    collection_names = [col.name for col in collections]

    if COLLECTION_NAME not in collection_names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_DIMENSION,
                distance=Distance.COSINE
            )
        )
        print(f"Created Qdrant collection: '{COLLECTION_NAME}' (dimension: {VECTOR_DIMENSION})")


def ingest_sop_documents(documents: list[dict]) -> int:
    """
    Ingests SOP chunks into Qdrant.
    Each item in documents must have:
      - 'id': int
      - 'text': str
      - 'sop_id': str
      - 'section': str
    Returns the count of points inserted.
    """
    init_vector_collection()

    points = []
    print(f"Embedding and ingesting {len(documents)} SOP documents into Qdrant...")

    for doc in documents:
        # 1. Generate 768-dim embedding via our unified AI client
        vector = generate_embedding(doc["text"])

        # 2. Package into a Qdrant Point
        point = PointStruct(
            id=doc["id"],
            vector=vector,
            payload={
                "sop_id": doc["sop_id"],
                "section": doc["section"],
                "text": doc["text"]
            }
        )
        points.append(point)

    # 3. Batch upsert into Qdrant
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    return len(points)


def search_sops(query: str, top_k: int = 2) -> list[dict]:
    """
    Searches the Qdrant vector database for the top_k most relevant SOP chunks.
    """
    init_vector_collection()

    # 1. Embed query
    query_vector = generate_embedding(query)

    # 2. Fast vector search in Qdrant
    response = client.query_points(
        collection_name=COLLECTION_NAME, query=query_vector, limit=top_k
    )
    results = response.points

    # 3. Format output
    formatted = []
    for hit in results:
        formatted.append({
            "score": round(hit.score, 4),
            "sop_id": hit.payload.get("sop_id"),
            "section": hit.payload.get("section"),
            "text": hit.payload.get("text")
        })

    return formatted


# Standalone verification block
if __name__ == "__main__":
    print("=== Testing Qdrant Vector Store Ingestion & Query ===")

    SAMPLE_SOPS = [
        {
            "id": 1,
            "sop_id": "SOP-701",
            "section": "Section 4.1 (Assay)",
            "text": "The active pharmaceutical ingredient potency must fall strictly within 98.0% and 102.0% of label claim."
        },
        {
            "id": 2,
            "sop_id": "SOP-701",
            "section": "Section 4.2 (Acidity & pH)",
            "text": "Solution pH must be maintained between 5.8 and 6.8 at 25 degrees Celsius to guarantee chemical stability."
        },
        {
            "id": 3,
            "sop_id": "SOP-701",
            "section": "Section 4.3 (Dissolution)",
            "text": "Not less than 80.0% of the active compound must dissolve within 45 minutes in 0.1M hydrochloric acid buffer."
        }
    ]

    # Ingest
    count = ingest_sop_documents(SAMPLE_SOPS)
    print(f"Successfully ingested {count} SOP documents.")

    # Query Qdrant
    query = "What is the dissolution rate requirement?"
    print(f"\nQuerying Qdrant for: '{query}'")
    hits = search_sops(query, top_k=1)

    for hit in hits:
        print(f"\nTop Match (Score: {hit['score']}):")
        print(f"SOP: {hit['sop_id']} - {hit['section']}")
        print(f"Evidence: {hit['text']}")