# All project settings in one place. Change values here, nowhere else.
import os
from pathlib import Path
from dotenv import load_dotenv

# ---- Folders ----
# This file is backend/src/rag/config.py, so go up 3 levels to reach backend/
BACKEND_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BACKEND_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
DOCUMENTS_CSV = DATA_DIR / "documents.csv"
CHROMA_DIR = DATA_DIR / "chroma_db"
BM25_PATH = DATA_DIR / "bm25_index.pkl"

# ---- API key ----
load_dotenv(BACKEND_DIR / ".env")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ---- Models ----
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
LLM_MODEL = "gemini-2.5-flash-lite"

# ---- Chunking ----
MAX_CHUNK_WORDS = 250
CHUNK_OVERLAP_WORDS = 30

# ---- Retrieval ----
CANDIDATES = 20
RERANK_TOP_N = 10
FINAL_TOP_K = 3
RRF_K = 60

# ---- Database ----
COLLECTION_NAME = "rbi_kyc"
