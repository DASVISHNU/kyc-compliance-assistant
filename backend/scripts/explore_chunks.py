# Lesson 4: check paragraph detection.
from rag import config
from rag.ingest.pdf_loader import load_pdf
from rag.ingest.cleaning import clean_pages
from rag.ingest.chunking import split_into_paragraphs

pages = load_pdf(config.RAW_DIR / "kyc_directions_2025_main.pdf")
lines = clean_pages(pages)
blocks = split_into_paragraphs(lines)

print("Clean lines:", len(lines))
print("Paragraph blocks:", len(blocks))

long_blocks = 0
for b in blocks:
    if len(b["text"].split()) > config.MAX_CHUNK_WORDS:
        long_blocks = long_blocks + 1
print("Blocks longer than", config.MAX_CHUNK_WORDS, "words:", long_blocks)

out_path = config.DATA_DIR / "debug_blocks.txt"
with open(out_path, "w", encoding="utf-8") as f:
    for b in blocks:
        words = len(b["text"].split())
        f.write("=" * 80 + "\n")
        f.write(b["annex"] + " | " + b["chapter"] + " | " + b["section"] + "\n")
        f.write("para " + b["para"] + " | pages " + str(b["pages"]) + " | " + str(words) + " words\n")
        f.write(b["text"][:300] + " ...\n")
print("Saved to:", out_path)