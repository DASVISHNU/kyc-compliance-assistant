from pathlib import Path
from pypdf import PdfReader


def load_pdf(pdf_path):
    """Read a PDF and return one dictionary per page:{
    "page":1,
    "text":"..."
    
    }."""

    pdf_path=Path(pdf_path)
    reader=PdfReader(pdf_path)

    pages=[]
    for i in range(len(reader.pages)):
        page=reader.pages[i]
        text=page.extract_text()
        if text is None:
            text=""
        pages.append({
                "page":i+1,"text":text
            })
    return pages
