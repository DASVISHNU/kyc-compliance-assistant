# One shared Gemini client + retry, used by embeddings (Lesson 6) and answers (Lesson 8).
import time

from google import genai
from google.genai import errors

from rag import config

TEMPORARY_ERRORS = [429, 500, 503]      # rate limit, server errors: worth retrying

_client = None                          # created the first time it's needed


def get_client():
    """Return the Gemini client, creating it once."""
    global _client
    if _client is None:
        if config.GEMINI_API_KEY == "":
            raise RuntimeError("GEMINI_API_KEY is missing. Add it to backend/.env")
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


def call_with_retry(function_to_call, *args, **kwargs):
    """Call a Gemini function; on 429/5xx errors wait and try again (15s, 30s, 60s)."""
    wait_seconds = 15
    for attempt in range(1, 5):
        try:
            return function_to_call(*args, **kwargs)
        except errors.APIError as e:
            if e.code in TEMPORARY_ERRORS and attempt < 4:
                print("  Gemini returned", e.code, "- waiting", wait_seconds, "seconds...")
                time.sleep(wait_seconds)
                wait_seconds = wait_seconds * 2
            else:
                raise
def generate_text(prompt, max_tokens=1024, temperature=0.0):
    """Send a prompt to the LLM and return its reply as plain text."""
    from google.genai import types

    response = call_with_retry(
        get_client().models.generate_content,
        model=config.LLM_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=temperature,
                                           max_output_tokens=max_tokens),
    )
    if response.text is None:
        return ""
    return response.text.strip()