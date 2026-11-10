# Lesson 3: check the cleaning step.
from rag import config
from rag.ingest.pdf_loader import load_pdf
from rag.ingest.cleaning import clean_pages

pages = load_pdf(config.RAW_DIR / "kyc_directions_2025_main.pdf")
lines = clean_pages(pages)

print("Pages:", len(pages))
print("Clean lines:", len(lines))
print("First page kept:", lines[0]["page"])

print("\n===== First 15 clean lines =====")
for item in lines[:15]:
    print("p" + str(item["page"]) + " | " + item["text"])

out_path = config.DATA_DIR / "debug_clean_lines.txt"
with open(out_path, "w", encoding="utf-8") as f:
    for item in lines:
        f.write("p" + str(item["page"]) + " | " + item["text"] + "\n")
print("\nSaved to:", out_path)