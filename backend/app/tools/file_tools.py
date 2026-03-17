from ..utils.file_parser import extract_text
from ..utils.text_processor import split_into_chunks

def parse_document(file_path: str) -> str:
    """Parse a document (PDF, MD, TXT) and return its text content."""
    return extract_text(file_path)

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """Split text into overlapping chunks for processing."""
    return split_into_chunks(text, chunk_size, overlap)
