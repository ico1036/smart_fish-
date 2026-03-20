import pytest
from unittest.mock import patch, MagicMock
from app.utils.llm_client import LLMClient


def test_llm_client_init():
    client = LLMClient(model="claude-sonnet-4-5")
    assert client.model == "claude-sonnet-4-5"

def test_llm_client_default_model():
    client = LLMClient()
    assert "claude" in client.model

def _make_cli_result(text: str, returncode: int = 0):
    """Create a mock subprocess result."""
    import json
    result = MagicMock()
    result.returncode = returncode
    result.stdout = json.dumps({"type": "result", "result": text})
    result.stderr = ""
    return result

@patch("app.utils.llm_client.subprocess.run")
def test_chat_returns_text(mock_run):
    mock_run.return_value = _make_cli_result("Hello world")
    client = LLMClient()
    result = client.chat(messages=[{"role": "user", "content": "Hi"}])
    assert result == "Hello world"

@patch("app.utils.llm_client.subprocess.run")
def test_chat_strips_think_tags(mock_run):
    mock_run.return_value = _make_cli_result("<think>reasoning</think>The answer is 42")
    client = LLMClient()
    result = client.chat(messages=[{"role": "user", "content": "test"}])
    assert result == "The answer is 42"

@patch("app.utils.llm_client.subprocess.run")
def test_chat_json_parses_fenced(mock_run):
    mock_run.return_value = _make_cli_result('```json\n{"key": "value"}\n```')
    client = LLMClient()
    result = client.chat_json(messages=[{"role": "user", "content": "test"}])
    assert result == {"key": "value"}

@patch("app.utils.llm_client.subprocess.run")
def test_chat_json_parses_bare(mock_run):
    mock_run.return_value = _make_cli_result('{"items": [1, 2, 3]}')
    client = LLMClient()
    result = client.chat_json(messages=[{"role": "user", "content": "test"}])
    assert result == {"items": [1, 2, 3]}

@patch("app.utils.llm_client.subprocess.run")
def test_chat_json_invalid_raises(mock_run):
    mock_run.return_value = _make_cli_result("not json")
    client = LLMClient()
    with pytest.raises(ValueError, match="invalid JSON"):
        client.chat_json(messages=[{"role": "user", "content": "test"}])

@patch("app.utils.llm_client.subprocess.run")
def test_chat_passes_system_prompt(mock_run):
    mock_run.return_value = _make_cli_result("response")
    client = LLMClient()
    client.chat(messages=[
        {"role": "system", "content": "You are helpful"},
        {"role": "user", "content": "Hi"},
    ])
    cmd = mock_run.call_args[0][0]
    assert "--system-prompt" in cmd
    sp_idx = cmd.index("--system-prompt")
    assert "You are helpful" in cmd[sp_idx + 1]
