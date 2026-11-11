# Our own small vector store: a NumPy matrix with one row per chunk.
import numpy as np


def normalize(matrix):
    """Scale every row to length 1, so a dot product equals cosine similarity."""
    lengths = np.linalg.norm(matrix, axis=1, keepdims=True)
    lengths[lengths == 0] = 1                  # avoid dividing by zero
    return matrix / lengths


def save_vectors(vectors, path):
    """Save a list of vectors (lists of numbers) as a normalized float32 matrix."""
    matrix = np.array(vectors, dtype=np.float32)
    matrix = normalize(matrix)
    np.save(path, matrix)
    return matrix


def load_vectors(path):
    return np.load(path)


def get_score(pair):
    return pair[1]


def search(query_vector, matrix, top_k):
    """Return the top_k (row_number, cosine_similarity) pairs, most similar first."""
    q = np.array(query_vector, dtype=np.float32)
    q = q / (np.linalg.norm(q) or 1.0)         # normalize the question vector too
    scores = matrix @ q                        # one dot product per chunk = cosine similarity

    pairs = []
    for i in range(len(scores)):
        pairs.append((i, float(scores[i])))
    pairs = sorted(pairs, key=get_score, reverse=True)
    return pairs[:top_k]