# Lesson 4: check paragraph detection and the final chunks.
from rag import config
from rag.ingest.pdf_loader import load_pdf
from rag.ingest.cleaning import clean_pages
from rag.ingest.chunking import split_into_paragraphs, make_chunks

pages = load_pdf(config.RAW_DIR / "kyc_directions_2025_main.pdf")
lines = clean_pages(pages)
blocks = split_into_paragraphs(lines)

# ---- Lesson 4A: paragraph blocks ----
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

# ---- Lesson 4B: final chunks ----
chunks = make_chunks(blocks, config.MAX_CHUNK_WORDS, config.CHUNK_OVERLAP_WORDS)

word_counts = []
for c in chunks:
    word_counts.append(len(c["text"].split()))

print("\nFinal chunks:", len(chunks))
print("Words per chunk: min", min(word_counts), "| max", max(word_counts),
      "| average", sum(word_counts) // len(word_counts))

out_path = config.DATA_DIR / "debug_chunks.txt"
with open(out_path, "w", encoding="utf-8") as f:
    for c in chunks:
        f.write("=" * 80 + "\n")
        f.write(c["id"] + " | " + c["label"] + " | pages " + str(c["pages"]) + "\n")
        f.write(str(len(c["text"].split())) + " words\n")
        f.write(c["text"] + "\n")
print("Saved to:", out_path)