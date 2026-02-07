from pathlib import Path
import faiss
import pickle
from sentence_transformers import SentenceTransformer

# Always resolve paths relative to this file
BASE_DIR = Path(__file__).resolve().parent

INDEX_PATH = BASE_DIR / "policy_index.faiss"
META_PATH = BASE_DIR / "policy_metadata.pkl"

# Load FAISS index
index = faiss.read_index(str(INDEX_PATH))

# Load metadata
with open(META_PATH, "rb") as f:
    clauses = pickle.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")


def search(query, top_k=5):
    query_embedding = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(query_embedding, top_k)

    results = []
    for idx, score in zip(indices[0], scores[0]):
        clause = clauses[idx]
        results.append({
            "clause_id": clause["clause_id"],
            "page": clause["page"],
            "text": clause["text"],
            "score": float(score)
        })

    return results


if __name__ == "__main__":
    query = "Is password sharing allowed?"
    results = search(query)

    for r in results:
        print("\n---")
        print(r["clause_id"], "(score:", round(r["score"], 3), ")")
        print(r["text"])