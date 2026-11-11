# Reciprocal Rank Fusion: merge several ranked lists using only the positions.


def get_score(pair):
    return pair[1]


def reciprocal_rank_fusion(ranked_lists, k=60):
    """ranked_lists: a list of lists of (row, score), each best-first.
    Returns one merged list of (row, rrf_score), best first."""
    scores = {}
    for ranked in ranked_lists:
        position = 1
        for pair in ranked:
            row = pair[0]
            if row not in scores:
                scores[row] = 0
            scores[row] = scores[row] + 1 / (k + position)
            position = position + 1

    pairs = []
    for row in scores:
        pairs.append((row, scores[row]))
    pairs = sorted(pairs, key=get_score, reverse=True)
    return pairs