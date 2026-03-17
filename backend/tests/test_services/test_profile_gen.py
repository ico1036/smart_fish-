import pytest
from unittest.mock import patch, MagicMock
from app.services.profile_generator import ProfileGenerator
from app.services.graph_service import GraphService

MOCK_PROFILE = {
    "bio": "AI researcher passionate about NLP",
    "persona": "Dr. Bob is a meticulous professor who values academic rigor and loves debating ideas.",
    "age": 45,
    "profession": "Professor",
    "mbti": "INTJ",
    "interested_topics": ["AI", "NLP", "education"],
}

@patch("app.services.profile_generator.get_llm_client")
def test_generate_profiles(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat_json.return_value = MOCK_PROFILE
    mock_get_client.return_value = mock_client
    graph_svc = GraphService()
    graph_svc.create_graph("g1")
    graph_svc.add_node("g1", "bob", "Bob", ["Professor"], {"summary": "AI professor at MIT"})
    graph_svc.add_node("g1", "alice", "Alice", ["Student"], {"summary": "CS student"})
    gen = ProfileGenerator(graph_service=graph_svc)
    profiles = gen.generate("g1", "Simulate university dynamics")
    assert len(profiles) == 2
    assert profiles[0].persona != ""

@patch("app.services.profile_generator.get_llm_client")
def test_generate_profiles_by_type(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat_json.return_value = MOCK_PROFILE
    mock_get_client.return_value = mock_client
    graph_svc = GraphService()
    graph_svc.create_graph("g1")
    graph_svc.add_node("g1", "bob", "Bob", ["Professor"], {"summary": "Prof"})
    graph_svc.add_node("g1", "alice", "Alice", ["Student"], {"summary": "Student"})
    gen = ProfileGenerator(graph_service=graph_svc)
    profiles = gen.generate("g1", "Test", entity_types=["Professor"])
    assert len(profiles) == 1
    assert profiles[0].name == "Bob"

@patch("app.services.profile_generator.get_llm_client")
def test_generate_handles_llm_error(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat_json.side_effect = Exception("LLM error")
    mock_get_client.return_value = mock_client
    graph_svc = GraphService()
    graph_svc.create_graph("g1")
    graph_svc.add_node("g1", "bob", "Bob", ["Professor"], {"summary": "Prof"})
    gen = ProfileGenerator(graph_service=graph_svc)
    profiles = gen.generate("g1", "Test")
    assert len(profiles) == 1  # fallback profile created
    assert profiles[0].name == "Bob"
