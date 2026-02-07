import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle

CLAUSE_PATH = "clauses.json"
INDEX_PATH = "policy_index.faiss"
META_PATH = "policy_metadata.pkl"

# Load clauses
with open(CLAUSE_PATH, "r", encoding="utf-8") as f:
    clauses = json.load(f)

texts = [c["text"] for c in clauses]

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Generate embeddings
embeddings = model.encode(texts, convert_to_numpy=True)

# Normalize for cosine similarity
faiss.normalize_L2(embeddings)

# Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)

# Save index
faiss.write_index(index, INDEX_PATH)

# Save metadata
with open(META_PATH, "wb") as f:
    pickle.dump(clauses, f)

print(f"Index built with {len(clauses)} clauses.")