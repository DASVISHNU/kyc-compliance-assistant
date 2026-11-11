# The full retrieval pipeline: semantic + BM25 -> RRF -> rerank.
import json

from rag import config
from rag.store.embeddings import embed_query
from rag.store.vector_store import load_vectors, search
from rag.store.bm25_index import load_bm25, search_bm25
from rag.retrieve.fusion import reciprocal_rank_fusion
from rag.retrieve.rerank import rerank


def load_index():
    """Load chunks, vectors and BM25 once, into one dictionary."""
    with open(config.CHUNKS_PATH, encoding="utf-8") as f:
        chunks = json.load(f)
    return {
        "chunks": chunks,
        "matrix": load_vectors(config.VECTORS_PATH),
        "bm25": load_bm25(config.BM25_PATH),
    }


def hybrid_search(question, index):
    """Semantic top N + BM25 top N, merged with RRF. Returns chunks with their scores."""
    semantic = search(embed_query(question), index["matrix"], config.CANDIDATES)
    keyword = search_bm25(index["bm25"], question, config.CANDIDATES)
    fused = reciprocal_rank_fusion([semantic, keyword], config.RRF_K)

    results = []
    for pair in fused[:config.RERANK_TOP_N]:
        chunk = dict(index["chunks"][pair[0]])     # a copy, so we don't change the loaded data
        chunk["rrf_score"] = pair[1]
        results.append(chunk)
    return results


def retrieve(question, index, use_rerank=True):
    """The chunks to send to the LLM: hybrid search, then (optionally) LLM reranking."""
    candidates = hybrid_search(question, index)
    if use_rerank:
        return rerank(question, candidates, config.FINAL_TOP_K)
    return candidates[:config.FINAL_TOP_K]