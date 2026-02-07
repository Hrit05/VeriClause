import pickle
import json
import faiss
from pathlib import Path
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import numpy as np

# -------------------------------
# Path setup
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

CLAUSE_PATH = ROOT_DIR/"clauses.json"
INDEX_PATH = ROOT_DIR / "policy_index.faiss"
META_PATH = ROOT_DIR / "policy_metadata.pkl"

# -------------------------------
# Load data
# -------------------------------
with open(CLAUSE_PATH, "r", encoding="utf-8") as f:
    clauses = json.load(f)

with open(META_PATH, "rb") as f:
    metadata = pickle.load(f)

index = faiss.read_index(str(INDEX_PATH))

model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------------
# BM25 setup
# -------------------------------
tokenized_corpus = [
    clause["text"].lower().split()
    for clause in clauses
]

bm25 = BM25Okapi(tokenized_corpus)

# -------------------------------
# Hybrid search
# -------------------------------
def hybrid_search(query, top_k=5):
    results = {}

    # -------- Vector Search --------
    query_vec = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_vec)

    scores, indices = index.search(query_vec, top_k)

    for idx, score in zip(indices[0], scores[0]):
        clause = metadata[idx]
        results[clause["clause_id"]] = {
            "text": clause["text"],
            "page": clause["page"],
            "vector_score": float(score),
            "bm25_score": 0.0
        }

    # -------- BM25 Search --------
    tokenized_query = query.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query)

    top_bm25_idx = np.argsort(bm25_scores)[-top_k:]

    for idx in top_bm25_idx:
        clause = clauses[idx]
        cid = clause["clause_id"]

        if cid not in results:
            results[cid] = {
                "text": clause["text"],
                "page": clause["page"],
                "vector_score": 0.0,
                "bm25_score": float(bm25_scores[idx])
            }
        else:
            results[cid]["bm25_score"] = float(bm25_scores[idx])

    # -------- Merge & rank --------
    final = list(results.items())
    final.sort(
        key=lambda x: (x[1]["vector_score"] + x[1]["bm25_score"]),
        reverse=True
    )

    return final[:top_k]


# -------------------------------
# Test run
# -------------------------------
if __name__ == "__main__":
    query = "Is sharing VPN credentials allowed?"
    results = hybrid_search(query)

    for cid, data in results:
        print("\n---")
        print(cid)
        print("Vector:", round(data["vector_score"], 3),
              "| BM25:", round(data["bm25_score"], 3))
        print(data["text"])
