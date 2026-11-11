# The web API: FastAPI wraps the RAG pipeline so a website can call it.
#   Run:  uv run uvicorn rag.api:app --reload --port 8000
#   Docs: http://127.0.0.1:8000/docs
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from rag import config
from rag.retrieve.retriever import load_index
from rag.generate.answer import answer_question


# ---- Data shapes (Pydantic models) ----

class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class Source(BaseModel):
    number: int
    id: str
    label: str
    pages: list[int]
    text: str


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]


# ---- The app ----

app = FastAPI(
    title="RBI KYC Assistant API",
    description="Ask questions about RBI's KYC Directions for commercial banks. "
                "For information only, not legal or compliance advice.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.FRONTEND_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

index = load_index()          # chunks + vectors + BM25, loaded once when the server starts


@app.get("/health")
def health():
    """Check that the server is running and the knowledge base is loaded."""
    return {"status": "ok", "chunks": len(index["chunks"])}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    """Answer a question about RBI KYC rules, with numbered sources."""
    question = request.question.strip()
    try:
        result = answer_question(question, index)
    except Exception as error:
        print("Error while answering:", repr(error))
        raise HTTPException(
            status_code=503,
            detail="The assistant could not answer right now. Please try again in a minute.",
        )
    return result