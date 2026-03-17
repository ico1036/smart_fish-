import pytest
from unittest.mock import patch, MagicMock
from app.services.graph_builder import GraphBuilder
from app.services.graph_service import GraphService

MOCK_EXTRACTION = {
    "entities": [
        {"id": "alice", "name": "Alice", "type": "Student", "summary": "CS student at MIT", "attributes": {"major": "CS"}},
        {"id": "bob", "name": "Bob", "type": "Professor", "summary": "AI professor", "attributes": {"department": "CS"}},
    ],
    "relationships": [
        {"source": "alice", "target": "bob", "type": "STUDIES_UNDER", "attributes": {}},
    ]
}

@patch("app.services.graph_builder.get_llm_client")
def test_build_graph_from_chunks(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat_json.return_value = MOCK_EXTRACTION
    mock_get_client.return_value = mock_client
    graph_svc = GraphService()
    builder = GraphBuilder(graph_service=graph_svc)
    ontology = {
        "entity_types": [{"name": "Student", "description": "A student", "attributes": ["major"]}],
        "edge_types": [{"name": "STUDIES_UNDER", "description": "Studies under professor"}],
    }
    graph_id = builder.build("test-graph", ontology, ["Alice is a CS student studying under Professor Bob."])
    assert graph_id == "test-graph"
    nodes = graph_svc.get_nodes("test-graph")
    assert len(nodes) == 2
    edges = graph_svc.get_edges("test-graph")
    assert len(edges) == 1

@patch("app.services.graph_builder.get_llm_client")
def test_build_deduplicates_entities(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat_json.side_effect = [
        {"entities": [{"id": "alice", "name": "Alice", "type": "Student", "summary": "v1", "attributes": {}}], "relationships": []},
        {"entities": [{"id": "alice", "name": "Alice", "type": "Student", "summary": "v2", "attributes": {}}], "relationships": []},
    ]
    mock_get_client.return_value = mock_client
    graph_svc = GraphService()
    builder = GraphBuilder(graph_service=graph_svc)
    builder.build("g1", {"entity_types": [], "edge_types": []}, ["chunk1", "chunk2"])
    nodes = graph_svc.get_nodes("g1")
    assert len(nodes) == 1

@patch("app.services.graph_builder.get_llm_client")
def test_build_with_progress(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat_json.return_value = {"entities": [], "relationships": []}
    mock_get_client.return_value = mock_client
    graph_svc = GraphService()
    builder = GraphBuilder(graph_service=graph_svc)
    updates = []
    builder.build("g1", {"entity_types": [], "edge_types": []}, ["c1", "c2"],
                   on_progress=lambda p, m: updates.append((p, m)))
    assert len(updates) >= 2
