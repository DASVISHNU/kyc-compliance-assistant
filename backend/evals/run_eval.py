# Evaluate retrieval (and refusals) on the test questions.
#   uv run python evals\run_eval.py
import json
import time

from rag import config
from rag.store.embeddings import embed_query
from rag.store.vector_store import search
from rag.store.bm25_index import search_bm25
from rag.retrieve.retriever import load_index, hybrid_search
from rag.retrieve.rerank import rerank
from rag.generate.answer import answer_question, NO_ANSWER

K = 3                      # we judge the top 3 results (what the LLM would see)
PAUSE_SECONDS = 4          # between Gemini calls, to stay under the free-tier limit


def load_questions(path):
    questions = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line != "":
                questions.append(json.loads(line))
    return questions


def para_key(chunk):
    """'kyc_directions_2025_main/para-42-3' -> 'para-42' (which paragraph, ignoring the part)."""
    short_id = chunk["id"].split("/")[-1]          # 'para-42-3'
    return short_id.rsplit("-", 1)[0]              # 'para-42'


def first_hit_rank(chunks, expected):
    """Position (1, 2, 3...) of the first chunk from an expected paragraph, or 0 if none."""
    for i in range(len(chunks)):
        if para_key(chunks[i]) in expected:
            return i + 1
    return 0


def rows_to_chunks(pairs, index):
    chunks = []
    for pair in pairs:
        chunks.append(index["chunks"][pair[0]])
    return chunks


index = load_index()
questions = load_questions(config.BACKEND_DIR / "evals" / "questions.jsonl")

pipelines = ["semantic", "bm25", "hybrid", "hybrid+rerank"]
hits = {}
reciprocal = {}
for name in pipelines:
    hits[name] = 0
    reciprocal[name] = 0.0

answerable = 0
misses = []
for q in questions:
    if len(q["expected"]) == 0:
        continue                                   # out-of-scope questions are checked below
    answerable = answerable + 1
    question = q["question"]

    results = {}
    results["semantic"] = rows_to_chunks(search(embed_query(question), index["matrix"], K), index)
    results["bm25"] = rows_to_chunks(search_bm25(index["bm25"], question, K), index)
    candidates = hybrid_search(question, index)
    results["hybrid"] = candidates[:K]
    results["hybrid+rerank"] = rerank(question, candidates, K)
    time.sleep(PAUSE_SECONDS)

    line = ""
    for name in pipelines:
        rank = first_hit_rank(results[name], q["expected"])
        if rank > 0:
            hits[name] = hits[name] + 1
            reciprocal[name] = reciprocal[name] + 1 / rank
            line = line + f"{name}:#{rank}  "
        else:
            line = line + f"{name}:MISS  "
            if name == "hybrid+rerank":
                misses.append(question)
    print(question[:60].ljust(60), "|", line)

print("\n" + "Pipeline".ljust(16) + "Hit@3".rjust(8) + "MRR@3".rjust(8))
print("-" * 32)
for name in pipelines:
    hit_rate = hits[name] / answerable
    mrr = reciprocal[name] / answerable
    print(name.ljust(16) + f"{hit_rate:.0%}".rjust(8) + f"{mrr:.2f}".rjust(8))

print("\nFull pipeline missed:", len(misses))
for question in misses:
    print("  -", question)

# Out-of-scope questions: the system should refuse with NO_ANSWER
print("\nOut-of-scope questions (should say it cannot find the answer):")
refused = 0
total_out = 0
for q in questions:
    if len(q["expected"]) > 0:
        continue
    total_out = total_out + 1
    result = answer_question(q["question"], index)
    ok = result["answer"] == NO_ANSWER
    if ok:
        refused = refused + 1
    print("  ", "OK  " if ok else "FAIL", q["question"])
    time.sleep(PAUSE_SECONDS)
print("Correct refusals:", refused, "/", total_out)