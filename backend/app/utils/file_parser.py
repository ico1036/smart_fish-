from pathlib import Path

def extract_text(file_path: str) -> str:
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        return _extract_pdf(path)
    elif ext in (".md", ".markdown", ".txt"):
        return _extract_text_file(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def _extract_pdf(path: Path) -> str:
    import fitz  # PyMuPDF
    doc = fitz.open(str(path))
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text.strip()

def _extract_text_file(path: Path) -> str:
    encodings = ["utf-8", "gbk", "gb2312", "latin-1"]
    for enc in encodings:
        try:
            return path.read_text(encoding=enc).strip()
        except (UnicodeDecodeError, LookupError):
            continue
    return path.read_bytes().decode("utf-8", errors="replace").strip()
