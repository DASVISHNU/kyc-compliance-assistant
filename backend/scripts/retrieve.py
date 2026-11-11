# Compare hybrid search (RRF) with hybrid + reranking for one question:
#   uv run python scripts\retrieve.py "What is a beneficial owner of a company?"
import sys

from rag.retrieve.retriever import load_index, hybrid_search
from rag.retrieve.rerank import rerank
from rag import config

if len(sys.argv) < 2:
    print('Usage: uv run python scripts\\retrieve.py "your question"')
    raise SystemExit(1)
question = sys.argv[1]

index = load_index()
print("Question:", question)

candidates = hybrid_search(question, index)
print("\n--- Hybrid search (RRF), top", len(candidates), "---")
for i in range(len(candidates)):
    chunk = candidates[i]
    print(f"  {i + 1:2}. {chunk['rrf_score']:.4f} | {chunk['label']}")

final = rerank(question, candidates, config.FINAL_TOP_K)
print("\n--- After reranking, top", len(final), "(these go to the LLM) ---")
for i in range(len(final)):
    chunk = final[i]
    print(f"  {i + 1}. {chunk['label']}")
    print("     " + chunk["text"][:150] + "...")