import pytest
from app.utils.file_parser import extract_text
from app.utils.text_processor import split_into_chunks

def test_extract_text_from_txt(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("Hello World", encoding="utf-8")
    result = extract_text(str(f))
    assert result == "Hello World"

def test_extract_text_from_md(tmp_path):
    f = tmp_path / "test.md"
    f.write_text("# Title\n\nContent here", encoding="utf-8")
    result = extract_text(str(f))
    assert "Title" in result
    assert "Content here" in result

def test_extract_text_unsupported(tmp_path):
    f = tmp_path / "test.xyz"
    f.write_text("data")
    with pytest.raises(ValueError, match="Unsupported"):
        extract_text(str(f))

def test_split_into_chunks_small():
    text = "Short text"
    chunks = split_into_chunks(text, chunk_size=500, overlap=50)
    assert len(chunks) == 1
    assert chunks[0] == "Short text"

def test_split_into_chunks_large():
    text = "a" * 1000
    chunks = split_into_chunks(text, chunk_size=500, overlap=50)
    assert len(chunks) >= 2
    assert len(chunks[0]) == 500

def test_split_into_chunks_overlap():
    text = "abcdefghij" * 100  # 1000 chars
    chunks = split_into_chunks(text, chunk_size=500, overlap=50)
    # Check overlap: end of chunk 0 should match start of chunk 1
    assert chunks[0][-50:] == chunks[1][:50]

def test_extract_text_encoding(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("中文内容测试", encoding="utf-8")
    result = extract_text(str(f))
    assert result == "中文内容测试"


from app.tools.file_tools import parse_document, chunk_text

def test_parse_document_tool(tmp_path):
    f = tmp_path / "tool_test.txt"
    f.write_text("Tool test content", encoding="utf-8")
    result = parse_document(str(f))
    assert result == "Tool test content"

def test_chunk_text_tool():
    text = "a" * 1000
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) >= 2
