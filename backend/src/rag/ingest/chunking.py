import re

# Headings and numbered paragraphs in the RBI KYC Directions
CHAPTER = re.compile(r"^Chapter [IVXL]+ [–-] ")        # "Chapter VI – Customer Due Diligence ..."
SECTION = re.compile(r"^[A-F](\.\d)?\.? [A-Z]")         # "A. Short Title ...", "F.1 Enhanced ..."
ANNEX = re.compile(r"^Annex [–-] [IVX]+$")               # "Annex – I"
PARAGRAPH = re.compile(r"^(\d{1,3})\. ")                 # "42. Updation / Periodic Updation of KYC"


def join_lines(text_lines):
    """Join PDF lines into one text. If a line ends with '-', join the next line without a space."""
    text = ""
    for line in text_lines:
        if text == "":
            text = line
        elif text.endswith("-"):
            text = text + line
        else:
            text = text + " " + line
    return text


def new_block(chapter, section, annex, para, page):
    """Create an empty block (one paragraph) with its location in the document."""
    return {"chapter": chapter, "section": section, "annex": annex,
            "para": para, "pages": [page], "lines": []}


def split_into_paragraphs(lines):
    """Group clean lines into blocks: one block per numbered paragraph."""
    blocks = []
    current = None
    chapter = ""
    section = ""
    annex = ""
    expected = 1          # the paragraph number we expect next

    for item in lines:
        line = item["text"]
        page = item["page"]

        # Is this line the start of the NEXT paragraph? (protects against "27." traps)
        para_number = None
        match = PARAGRAPH.match(line)
        if match:
            number = int(match.group(1))
            if number == expected or number == expected + 1:
                para_number = number

        if CHAPTER.match(line):                     # new chapter
            chapter = line
            section = ""
            continue

        if ANNEX.match(line):                       # new annex: numbering restarts
            annex = line
            chapter = ""
            section = ""
            expected = 1
            current = new_block(chapter, section, annex, "intro", page)
            blocks.append(current)
            continue

        if para_number is None and SECTION.match(line) and len(line.split()) <= 12:
            section = line                          # new section heading
            continue

        if para_number is not None:                 # start a new paragraph block
            expected = para_number + 1
            current = new_block(chapter, section, annex, str(para_number), page)
            blocks.append(current)
        elif current is None:                       # text before paragraph 1 (Introduction)
            current = new_block("", "", "", "intro", page)
            blocks.append(current)

        current["lines"].append(line)
        if page not in current["pages"]:
            current["pages"].append(page)

    for block in blocks:
        block["text"] = join_lines(block["lines"])
    return blocks