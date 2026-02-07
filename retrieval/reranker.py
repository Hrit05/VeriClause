from sentence_transformers import CrossEncoder
from .hybrid_retrieval import hybrid_search

# Load cross-encoder model
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank(query, top_k=5, rerank_k=10, score_threshold=0.3):
    """
    1. Get candidates from hybrid retrieval
    2. Re-rank using cross-encoder
    3. Filter weak matches
    """

    # Step 1: Retrieve candidates
    candidates = hybrid_search(query, top_k=rerank_k)

    texts = []
    clause_ids = []

    for cid, data in candidates:
        texts.append(data["text"])
        clause_ids.append(cid)

    # Step 2: Prepare (query, text) pairs
    pairs = [(query, text) for text in texts]

    # Step 3: Cross-encoder scoring
    scores = reranker.predict(pairs)

    # Step 4: Merge + filter
    reranked = []
    for cid, text, score in zip(clause_ids, texts, scores):
        if score >= score_threshold:
            reranked.append({
                "clause_id": cid,
                "text": text,
                "score": float(score)
            })

    # Step 5: Sort by score
    reranked.sort(key=lambda x: x["score"], reverse=True)

    return reranked[:top_k]


# -------------------------------
# Test run
# -------------------------------
if __name__ == "__main__":
    query = "Is sharing VPN credentials allowed?"
    results = rerank(query)

    for r in results:
        print("\n---")
        print(r["clause_id"], "score:", round(r["score"], 3))
        print(r["text"])
