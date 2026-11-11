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


# ---------------- Lesson 4B: split long paragraphs into chunks ----------------

# A sub-item at the start of a line: "(1) ...", "(12) ...", "(iv) ..."
SUBITEM = re.compile(r"^\((\d{1,2}|[ivxl]{1,6})\) ")


def split_by_words(text, max_words, overlap):
    """Last resort for one huge piece: fixed-size word chunks with overlap."""
    words = text.split()
    step = max_words - overlap
    parts = []
    for i in range(0, len(words), step):
        part = " ".join(words[i:i + max_words])
        if part != "":
            parts.append(part)
        if i + max_words >= len(words):      # this part reached the end: stop
            break
    return parts


def split_block(block, max_words, overlap):
    """Split one paragraph block into texts of at most max_words words, at its sub-items."""
    if len(block["text"].split()) <= max_words:
        return [block["text"]]                      # short enough: keep it whole

    # 1. Cut the paragraph into pieces: a new piece starts at every sub-item line
    pieces = []
    current_lines = []
    for line in block["lines"]:
        if SUBITEM.match(line) and len(current_lines) > 0:
            pieces.append(join_lines(current_lines))
            current_lines = []
        current_lines.append(line)
    if len(current_lines) > 0:
        pieces.append(join_lines(current_lines))

    # 2. The paragraph's opening words give context to every part
    lead_words = pieces[0].split()[:30]
    lead = " ".join(lead_words)

    # 3. Basket: fill each chunk with whole pieces until the next one doesn't fit
    texts = []
    basket = []
    basket_words = 0
    for piece in pieces:
        piece_words = len(piece.split())

        if piece_words > max_words:                      # one piece is too big by itself
            if len(basket) > 0:
                texts.append(" ".join(basket))
                basket = []
                basket_words = 0
            for part in split_by_words(piece, max_words, overlap):
                texts.append(part)
            continue

        if basket_words + piece_words > max_words and len(basket) > 0:
            texts.append(" ".join(basket))               # basket full: close it
            basket = []
            basket_words = 0

        basket.append(piece)
        basket_words = basket_words + piece_words

    if len(basket) > 0:                                  # don't forget the last basket!
        texts.append(" ".join(basket))

    # 4. Give every part after the first the paragraph's opening words as context
    result = [texts[0]]
    for text in texts[1:]:
        result.append("[" + lead + " ...] " + text)
    return result


def make_chunks(blocks, max_words, overlap):
    """Turn paragraph blocks into the final chunks, each with an id and a readable label."""
    chunks = []
    for block in blocks:
        texts = split_block(block, max_words, overlap)

        prefix = ""
        if block["annex"] != "":
            prefix = "annex-" + block["annex"].split()[-1] + "-"     # "Annex – I" → "annex-I-"

        for i in range(len(texts)):
            part = i + 1
            chunk_id = prefix + "para-" + block["para"] + "-" + str(part)

            label = ""
            if block["annex"] != "":
                label = block["annex"] + ", "
            if block["chapter"] != "":
                label = label + block["chapter"] + ", "

            if block["para"] == "intro" and block["annex"] == "":
                label = label + "Introduction"                 # the text before paragraph 1
            elif block["para"] == "intro":
                label = label + "opening text"                 # the start of an annex
            else:
                label = label + "para " + block["para"]

            if len(texts) > 1:
                label = label + " (part " + str(part) + " of " + str(len(texts)) + ")"

            chunks.append({
                "id": chunk_id,
                "label": label,
                "chapter": block["chapter"],
                "section": block["section"],
                "annex": block["annex"],
                "para": block["para"],
                "pages": block["pages"],
                "text": texts[i],
            })
    return chunks