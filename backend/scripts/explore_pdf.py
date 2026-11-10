#Inspect the kyc PDF:how many pages,how much text,and what the text looks like.
from rag import config
from rag.ingest.pdf_loader import load_pdf
from rag.ingest.cleaning import clean_pages
pdf_path=config.RAW_DIR/"kyc_directions_2025_main.pdf"
pages=load_pdf(pdf_path)
lines=clean_pages(pages)
print("File:",pdf_path.name)
print("Clean lines:", len(lines))
print("number of pages:",len(pages))
print("First page kept:", lines[0]["page"])

total_words=0
empty_pages=[]
for p in pages:
    words=len(p["text"].split())
    total_words=total_words+words
    if words==0:
        empty_pages.append(p["page"])
print("Total words:",total_words)
print("pages with no text",empty_pages)

print("\n==== PAGE 1(printed)  ====")
print(pages[0]["text"][:1500])

if len(pages)>=5:
    print("\n=== PAGE 5(raw,with hidden characters)====")
    print(repr(pages[4]["text"][:800]))


out_path=config.DATA_DIR/"debug_main_text.txt"
with open(out_path,"w",encoding="utf-8") as f:
    for p in pages:
        f.write("\n\n====PAGE"+str(p["page"])+"====\n")
        f.write(p["text"])
print("\nFull text saved to:",out_path)

print("\n===== First 15 clean lines =====")
for item in lines[:15]:
    print("p" + str(item["page"]) + " | " + item["text"])

# Save all clean lines to a file, to check in VS Code
out_path = config.DATA_DIR / "debug_clean_lines.txt"
with open(out_path, "w", encoding="utf-8") as f:
    for item in lines:
        f.write("p" + str(item["page"]) + " | " + item["text"] + "\n")
print("\nSaved to:", out_path)