# Try both searches from the terminal:
#   uv run python scripts\search.py "How often should KYC be updated for high-risk customers?"
import json
import sys

from rag import config
from rag.store.embeddings import embed_query
from rag.store.vector_store import load_vectors, search
from rag.store.bm25_index import load_bm25, search_bm25

if len(sys.argv) < 2:
    print('Usage: uv run python scripts\\search.py "your question"')
    raise SystemExit(1)
question = sys.argv[1]

with open(config.CHUNKS_PATH, encoding="utf-8") as f:
    chunks = json.load(f)
matrix = load_vectors(config.VECTORS_PATH)
bm25 = load_bm25(config.BM25_PATH)

print("Question:", question)

print("\n--- Semantic search (cosine similarity, higher = closer) ---")
for pair in search(embed_query(question), matrix, top_k=5):
    chunk = chunks[pair[0]]
    print(f"  {pair[1]:.3f} | {chunk['label']}")
    print("        " + chunk["text"][:120] + "...")

print("\n--- BM25 keyword search (higher = better) ---")
for pair in search_bm25(bm25, question, top_k=5):
    chunk = chunks[pair[0]]
    print(f"  {pair[1]:.2f} | {chunk['label']}")
    print("        " + chunk["text"][:120] + "...")