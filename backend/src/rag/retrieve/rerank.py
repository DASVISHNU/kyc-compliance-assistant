# Reranking with Gemini: the LLM reads the question and every candidate, and orders them.
import json
import re

from rag.gemini_client import generate_text

PREVIEW_CHARS = 1200          # how much of each chunk the LLM sees


def build_rerank_prompt(question, candidates):
    text = ""
    for i in range(len(candidates)):
        chunk = candidates[i]
        text = text + "\n[" + str(i) + "] " + chunk["label"] + "\n" + chunk["text"][:PREVIEW_CHARS] + "\n"

    return ("You are ranking passages from an RBI regulation by how well they answer a question.\n\n"
            "Question: " + question + "\n\n"
            "Passages:" + text + "\n"
                       "Rank ALL the passages. Return ONLY a JSON array containing every passage number "
            "exactly once, most useful first, for example [3, 0, 7, 1, 2, 4, 5, 6, 8, 9].")


def parse_ranking(reply, count):
    """Read the passage numbers from the LLM reply, in order. Returns [] if there are none.
    Works for "[3, 0, 7]" and also for "[3], [0], [7]"."""
    start = reply.find("[")
    end = reply.rfind("]")
    if start == -1 or end == -1 or end < start:
        return []
    inside = reply[start:end + 1]

    ranking = []
    for text_number in re.findall(r"\d+", inside):
        n = int(text_number)
        if 0 <= n < count and n not in ranking:
            ranking.append(n)
    return ranking


def rerank(question, candidates, top_k):
    """Return the top_k candidates in the LLM's order. Falls back to the original order."""
    if len(candidates) == 0:
        return []

    reply = generate_text(build_rerank_prompt(question, candidates), max_tokens=100)
    
         # ← add this (temporary)
    ranking = parse_ranking(reply, len(candidates))
    

    if len(ranking) == 0:
        print("  (reranker reply not readable, keeping the hybrid order)")
        return candidates[:top_k]

    reranked = []
    for n in ranking:
        reranked.append(candidates[n])

    # If the LLM chose fewer than top_k, fill up with the next best hybrid results
    for chunk in candidates:
        if len(reranked) >= top_k:
            break
        if chunk not in reranked:
            reranked.append(chunk)

    return reranked[:top_k]