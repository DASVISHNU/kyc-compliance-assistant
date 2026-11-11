# Keyword search with BM25. The index is saved to a file with pickle.
import pickle
import re

from rank_bm25 import BM25Okapi


def tokenize(text):
    """Lowercase, then keep runs of letters/digits. "Para 42(1)" -> ["para", "42", "1"]"""
    return re.findall(r"\w+", text.lower())


def build_bm25(texts):
    tokenized = []
    for text in texts:
        tokenized.append(tokenize(text))
    return BM25Okapi(tokenized)


def save_bm25(index, path):
    with open(path, "wb") as f:              # "wb" = write binary
        pickle.dump(index, f)


def load_bm25(path):
    with open(path, "rb") as f:              # only load pickle files that YOU created
        return pickle.load(f)


def get_score(pair):
    return pair[1]


def search_bm25(index, query, top_k):
    """Return the top_k (row_number, bm25_score) pairs, best first."""
    scores = index.get_scores(tokenize(query))
    pairs = []
    for i in range(len(scores)):
        pairs.append((i, float(scores[i])))
    pairs = sorted(pairs, key=get_score, reverse=True)
    return pairs[:top_k]