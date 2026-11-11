# Generation: build a grounded prompt from the retrieved chunks and ask Gemini for a cited answer.
from rag.gemini_client import generate_text
from rag.retrieve.retriever import retrieve

NO_ANSWER = "I could not find this in the RBI KYC Directions I have."


def build_prompt(question, chunks):
    """The grounded RAG prompt: rules + numbered sources + the question."""
    sources = ""
    for i in range(len(chunks)):
        chunk = chunks[i]
        sources = sources + "[" + str(i + 1) + "] " + chunk["title"] + ", " + chunk["label"]
        sources = sources + " (page " + str(chunk["pages"][0]) + ")\n"
        sources = sources + chunk["text"] + "\n\n"

    return (
        "You are an assistant that answers questions about RBI's Know Your Customer (KYC) rules "
        "for commercial banks.\n\n"
        "Rules:\n"
        "1. Answer ONLY from the sources below. Do not use any other knowledge.\n"
        "2. If the sources do not contain the answer, reply exactly: \"" + NO_ANSWER + "\"\n"
        "3. After every fact, cite its source number in square brackets, like [1] or [2].\n"
        "4. Copy numbers, time periods and limits exactly as written in the sources.\n"
        "5. Keep the answer short and clear: 2-6 sentences, or a short list.\n\n"
        "Sources:\n" + sources +
        "Question: " + question + "\n\n"
        "Answer:"
    )


def answer_question(question, index):
    """The whole RAG pipeline for one question. Returns the answer and the sources used."""
    chunks = retrieve(question, index)

    if len(chunks) == 0:
        return {"question": question, "answer": NO_ANSWER, "sources": []}

    answer = generate_text(build_prompt(question, chunks), max_tokens=1500, temperature=0.0)
    if answer == "" or NO_ANSWER in answer:
        return {"question": question, "answer": NO_ANSWER, "sources": []}

    sources = []
    for i in range(len(chunks)):
        chunk = chunks[i]
        sources.append({
            "number": i + 1,
            "id": chunk["id"],
            "label": chunk["label"],
            "pages": chunk["pages"],
            "text": chunk["text"],
        })
    return {"question": question, "answer": answer, "sources": sources}