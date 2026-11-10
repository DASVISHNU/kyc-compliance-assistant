# Lesson 2: inspect the raw PDF text.
from rag import config
from rag.ingest.pdf_loader import load_pdf

pdf_path = config.RAW_DIR / "kyc_directions_2025_main.pdf"
pages = load_pdf(pdf_path)

if len(pages) == 0:
    print("ERROR: no pages found. Is this a real PDF?")
    raise SystemExit(1)

print("File:", pdf_path.name)
print("Number of pages:", len(pages))

total_words = 0
empty_pages = []
for p in pages:
    words = len(p["text"].split())
    total_words = total_words + words
    if words == 0:
        empty_pages.append(p["page"])
print("Total words:", total_words)
print("Pages with no text:", empty_pages)

print("\n===== PAGE 1 (printed) =====")
print(pages[0]["text"][:1500])

if len(pages) >= 5:
    print("\n===== PAGE 5 (raw, with hidden characters) =====")
    print(repr(pages[4]["text"][:800]))

out_path = config.DATA_DIR / "debug_main_text.txt"
with open(out_path, "w", encoding="utf-8") as f:
    for p in pages:
        f.write("\n\n====PAGE" + str(p["page"]) + "====\n")
        f.write(p["text"])
print("\nFull text saved to:", out_path)