import csv


def load_documents(csv_path):
    """Read documents.csv and return {file_name: row}, where row is a dictionary of that line."""
    documents = {}
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            documents[row["file_name"]] = row
    return documents


def make_header(chunk, doc):
    """Build the one-line metadata header that is put in front of the chunk for searching."""
    parts = [doc["regulator"], doc["title"], doc["reference"], "Updated as on " + doc["updated_as_on"]]
    if chunk["annex"] != "":
        parts.append(chunk["annex"])
    if chunk["chapter"] != "":
        parts.append(chunk["chapter"])
    if chunk["section"] != "":
        parts.append(chunk["section"])
    parts.append("Para " + chunk["para"])
    return " | ".join(parts)


def add_metadata(chunks, doc):
    """Attach document information to every chunk, and build its search_text."""
    doc_id = doc["file_name"].replace(".pdf", "")
    for chunk in chunks:
        chunk["id"] = doc_id + "/" + chunk["id"]          # unique across ALL documents
        chunk["source_file"] = doc["file_name"]
        chunk["title"] = doc["title"]
        chunk["reference"] = doc["reference"]
        chunk["updated_as_on"] = doc["updated_as_on"]
        chunk["status"] = doc["status"]
        chunk["header"] = make_header(chunk, doc)
        chunk["search_text"] = chunk["header"] + "\n" + chunk["text"]
    return chunks