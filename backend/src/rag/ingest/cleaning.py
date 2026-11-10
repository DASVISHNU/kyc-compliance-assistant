import re

PAGE_NUMBER=re.compile(r"^\d+$")

FOOTNOTE=re.compile(r"^\d{1,2}\s*(Inserted|Substituted|Amended|Added|Deleted|Omitted)")


def find_body_start(pages):
    """Return the index of the first page after the table of contents(the page with 'Introduction')."""
    for i in range(len(pages)):
        for line in pages[i]["text"].split("\n"):
            if line.strip() =="Introduction":
                return i
    return 0

def clean_pages(pages):
    """Turn raw pages into clean lines:[{"pages":4,"text":chapter I-preliminary"},...]"""
    start=find_body_start(pages)
    lines=[]






    for p in pages[start:]:
        for raw_line in p["text"].split("\n"):
            line=re.sub(r"\s+"," ",raw_line).strip()


            if line == "":
                continue
            if PAGE_NUMBER.match(line):
                continue
            if FOOTNOTE.match(line):
                break
            lines.append({"page":p["page"],"text":line})

    return lines