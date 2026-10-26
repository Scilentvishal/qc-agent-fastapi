# app/services/embedding_service.py
import math
from app.core.ai_client import generate_embedding


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Calculates cosine similarity between two numeric vectors."""
    if len(vec_a) != len(vec_b):
        raise ValueError(f"Vector dimension mismatch: {len(vec_a)} vs {len(vec_b)}")

    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def search_passages(query: str, passages: list[dict], top_k: int = 2) -> list[dict]:
    """Finds the top_k most semantically relevant passages using unified embedding client."""
    query_vector = generate_embedding(query)
    scored_results = []

    for item in passages:
        doc_vector = item.get("embedding")
        if not doc_vector:
            doc_vector = generate_embedding(item["text"])
            item["embedding"] = doc_vector

        score = cosine_similarity(query_vector, doc_vector)
        scored_results.append({
            "section": item["section"],
            "text": item["text"],
            "similarity_score": round(score, 4)
        })

    scored_results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return scored_results[:top_k]


if __name__ == "__main__":
    print("=== Testing Unified Semantic Search Gateway ===")

    SAMPLE_SOP_CHUNKS = [
        {
            "section": "SOP-701 Section 4.1 (Assay)",
            "text": "The active pharmaceutical ingredient potency must fall strictly within 98.0% and 102.0% of label claim."
        },
        {
            "section": "SOP-701 Section 4.2 (Acidity & pH)",
            "text": "Solution pH must be maintained between 5.8 and 6.8 at 25 degrees Celsius to guarantee chemical stability."
        },
        {
            "section": "SOP-701 Section 4.3 (Dissolution)",
            "text": "Not less than 80.0% of the active compound must dissolve within 45 minutes in 0.1M hydrochloric acid buffer."
        }
    ]

    test_query = "What are the allowed acidity limits for batch release?"
    print(f"Query: '{test_query}'")
    matches = search_passages(test_query, SAMPLE_SOP_CHUNKS, top_k=2)

    for i, match in enumerate(matches, 1):
        print(f"\nMatch #{i} (Score: {match['similarity_score']}):")
        print(f"Section: {match['section']}")
        print(f"Text: {match['text']}")