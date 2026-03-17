import pytest
from unittest.mock import patch, MagicMock
from app.utils.llm_client import LLMClient

def test_llm_client_init():
    client = LLMClient(api_key="test-key", model="claude-sonnet-4-5")
    assert client.model == "claude-sonnet-4-5"

def test_llm_client_default_model():
    client = LLMClient(api_key="test-key")
    assert "claude" in client.model

@patch("app.utils.llm_client.Anthropic")
def test_chat_returns_text(mock_anthropic):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Hello world")]
    mock_anthropic.return_value.messages.create.return_value = mock_response
    client = LLMClient(api_key="test-key")
    result = client.chat(messages=[{"role": "user", "content": "Hi"}])
    assert result == "Hello world"

@patch("app.utils.llm_client.Anthropic")
def test_chat_strips_think_tags(mock_anthropic):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="<think>reasoning</think>The answer is 42")]
    mock_anthropic.return_value.messages.create.return_value = mock_response
    client = LLMClient(api_key="test-key")
    result = client.chat(messages=[{"role": "user", "content": "test"}])
    assert result == "The answer is 42"

@patch("app.utils.llm_client.Anthropic")
def test_chat_json_parses_fenced(mock_anthropic):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='```json\n{"key": "value"}\n```')]
    mock_anthropic.return_value.messages.create.return_value = mock_response
    client = LLMClient(api_key="test-key")
    result = client.chat_json(messages=[{"role": "user", "content": "test"}])
    assert result == {"key": "value"}

@patch("app.utils.llm_client.Anthropic")
def test_chat_json_parses_bare(mock_anthropic):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='{"items": [1, 2, 3]}')]
    mock_anthropic.return_value.messages.create.return_value = mock_response
    client = LLMClient(api_key="test-key")
    result = client.chat_json(messages=[{"role": "user", "content": "test"}])
    assert result == {"items": [1, 2, 3]}

@patch("app.utils.llm_client.Anthropic")
def test_chat_json_invalid_raises(mock_anthropic):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="not json")]
    mock_anthropic.return_value.messages.create.return_value = mock_response
    client = LLMClient(api_key="test-key")
    with pytest.raises(ValueError, match="invalid JSON"):
        client.chat_json(messages=[{"role": "user", "content": "test"}])

@patch("app.utils.llm_client.Anthropic")
def test_chat_separates_system_message(mock_anthropic):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="response")]
    mock_instance = mock_anthropic.return_value
    mock_instance.messages.create.return_value = mock_response
    client = LLMClient(api_key="test-key")
    client.chat(messages=[
        {"role": "system", "content": "You are helpful"},
        {"role": "user", "content": "Hi"},
    ])
    call_kwargs = mock_instance.messages.create.call_args[1]
    assert call_kwargs["system"] == "You are helpful"
    assert len(call_kwargs["messages"]) == 1
    assert call_kwargs["messages"][0]["role"] == "user"
