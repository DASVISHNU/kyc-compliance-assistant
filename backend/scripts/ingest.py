# Build the knowledge base: PDFs → clean → chunks → metadata → chunks.json
import json

from rag import config
from rag.ingest.pdf_loader import load_pdf
from rag.ingest.cleaning import clean_pages
from rag.ingest.chunking import split_into_paragraphs, make_chunks
from rag.ingest.metadata import load_documents, add_metadata

documents = load_documents(config.DOCUMENTS_CSV)
print("Documents listed in documents.csv:", len(documents))

all_chunks = []
for file_name in documents:
    doc = documents[file_name]

    if doc["status"] != "in_force":
        print("Skipping (not in force):", file_name)
        continue

    pdf_path = config.RAW_DIR / file_name
    if not pdf_path.exists():
        print("Missing PDF, skipping:", file_name)
        continue

    pages = load_pdf(pdf_path)
    lines = clean_pages(pages)
    blocks = split_into_paragraphs(lines)
    chunks = make_chunks(blocks, config.MAX_CHUNK_WORDS, config.CHUNK_OVERLAP_WORDS)
    chunks = add_metadata(chunks, doc)

    print(file_name, "->", len(pages), "pages,", len(blocks), "paragraphs,", len(chunks), "chunks")
    for chunk in chunks:
        all_chunks.append(chunk)

with open(config.CHUNKS_PATH, "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, ensure_ascii=False, indent=2)

print("\nSaved", len(all_chunks), "chunks to", config.CHUNKS_PATH)