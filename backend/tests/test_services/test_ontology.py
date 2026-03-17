import pytest
from unittest.mock import patch, MagicMock
from app.services.ontology_service import OntologyService

MOCK_ONTOLOGY_RESPONSE = {
    "entity_types": [
        {"name": "Student", "description": "University student", "attributes": ["major", "year"]},
        {"name": "Professor", "description": "University professor", "attributes": ["department"]},
        {"name": "University", "description": "Educational institution", "attributes": ["location"]},
        {"name": "Course", "description": "Academic course", "attributes": ["subject"]},
        {"name": "Department", "description": "Academic department", "attributes": ["faculty"]},
        {"name": "ResearchGroup", "description": "Research team", "attributes": ["focus"]},
        {"name": "MediaOutlet", "description": "News/media org", "attributes": ["type"]},
        {"name": "GovernmentAgency", "description": "Government body", "attributes": ["level"]},
        {"name": "Person", "description": "Generic person", "attributes": ["role"]},
        {"name": "Organization", "description": "Generic org", "attributes": ["sector"]},
    ],
    "edge_types": [
        {"name": "ENROLLED_IN", "description": "Student enrolled in course", "source_types": ["Student"], "target_types": ["Course"]},
        {"name": "TEACHES", "description": "Professor teaches course", "source_types": ["Professor"], "target_types": ["Course"]},
        {"name": "BELONGS_TO", "description": "Belongs to department", "source_types": ["Professor"], "target_types": ["Department"]},
        {"name": "AFFILIATED_WITH", "description": "Affiliated with university", "source_types": ["Person"], "target_types": ["University"]},
        {"name": "COLLABORATES", "description": "Research collaboration", "source_types": ["Professor"], "target_types": ["Professor"]},
        {"name": "REPORTS_ON", "description": "Media reports on entity", "source_types": ["MediaOutlet"], "target_types": ["University"]},
    ],
    "analysis_summary": "Ontology designed for university ecosystem simulation."
}

@patch("app.services.ontology_service.get_llm_client")
def test_generate_ontology(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat_json.return_value = MOCK_ONTOLOGY_RESPONSE
    mock_get_client.return_value = mock_client
    service = OntologyService()
    result = service.generate("Simulate university opinion dynamics", "Professor Zhang teaches CS101...")
    assert len(result["entity_types"]) == 10
    assert result["entity_types"][-1]["name"] == "Organization"
    assert result["entity_types"][-2]["name"] == "Person"
    assert len(result["edge_types"]) >= 6

@patch("app.services.ontology_service.get_llm_client")
def test_validate_adds_fallback_types(mock_get_client):
    incomplete = {
        "entity_types": [{"name": "Student", "description": "A student", "attributes": []}],
        "edge_types": [{"name": "KNOWS", "description": "Knows", "source_types": ["Student"], "target_types": ["Student"]}],
        "analysis_summary": "Test"
    }
    mock_client = MagicMock()
    mock_client.chat_json.return_value = incomplete
    mock_get_client.return_value = mock_client
    service = OntologyService()
    result = service.generate("Test", "Some text")
    names = [et["name"] for et in result["entity_types"]]
    assert "Person" in names
    assert "Organization" in names

@patch("app.services.ontology_service.get_llm_client")
def test_ontology_truncates_long_text(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat_json.return_value = MOCK_ONTOLOGY_RESPONSE
    mock_get_client.return_value = mock_client
    service = OntologyService()
    service.generate("Test", "x" * 100000)
    call_args = mock_client.chat_json.call_args[1]["messages"]
    user_msg = [m for m in call_args if m["role"] == "user"][0]["content"]
    assert len(user_msg) < 60000
