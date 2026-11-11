# Turn texts into vectors with Gemini. Every vector is cached in a file, so we never pay twice.
import hashlib
import json
import time

from google.genai import types

from rag import config
from rag.gemini_client import get_client, call_with_retry

BATCH_SIZE = 50               # texts per API call
PAUSE_SECONDS = 35            # wait between batches: stays under the free-tier per-minute limit


def cache_key(text, task_type):
    """A short fingerprint of (model, size, task type, text)."""
    raw = config.EMBED_MODEL + "|" + str(config.EMBED_DIMS) + "|" + task_type + "|" + text
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def load_cache():
    if config.EMBED_CACHE_PATH.exists():
        with open(config.EMBED_CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(config.EMBED_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f)


def embed_batch(texts, task_type):
    """One API call: a list of texts -> a list of vectors (same order)."""
    response = call_with_retry(
        get_client().models.embed_content,
        model=config.EMBED_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(task_type=task_type,
                                        output_dimensionality=config.EMBED_DIMS),
    )
    vectors = []
    for e in response.embeddings:
        vectors.append(e.values)
    return vectors


def embed_texts(texts, task_type="RETRIEVAL_DOCUMENT"):
    """Embed many texts. Uses the cache; only texts never embedded before are sent to Gemini."""
    cache = load_cache()

    # 1. Find which texts are not in the cache yet
    missing = []
    for text in texts:
        key = cache_key(text, task_type)
        if key not in cache and text not in missing:
            missing.append(text)
    print("Embeddings: ", len(texts) - len(missing), "from cache,", len(missing), "to create")

    # 2. Embed the missing ones in batches, saving the cache after every batch
    for i in range(0, len(missing), BATCH_SIZE):
        batch = missing[i:i + BATCH_SIZE]
        vectors = embed_batch(batch, task_type)
        for j in range(len(batch)):
            cache[cache_key(batch[j], task_type)] = vectors[j]
        save_cache(cache)
        print("  embedded", min(i + BATCH_SIZE, len(missing)), "/", len(missing))
        if i + BATCH_SIZE < len(missing):          # more batches to come: pause
            time.sleep(PAUSE_SECONDS)

    # 3. Return the vectors in the same order as the input texts
    result = []
    for text in texts:
        result.append(cache[cache_key(text, task_type)])
    return result


def embed_query(question):
    """Embed one search question (task type RETRIEVAL_QUERY)."""
    return embed_texts([question], task_type="RETRIEVAL_QUERY")[0]