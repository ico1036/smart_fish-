import pytest
from unittest.mock import patch, MagicMock
from app.services.simulation_runner import SimulationRunner
from app.models.simulation import AgentProfile
from app.services.sim_engine import SimEngine

@patch("app.services.simulation_runner.get_fast_llm_client")
def test_run_single_round(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat.return_value = "ACTION: create_post\nCONTENT: Hello world from Alice!"
    mock_get_client.return_value = mock_client
    engine = SimEngine()
    engine.create_platform("twitter")
    agents = [AgentProfile(agent_id=1, name="Alice", username="alice", persona="A curious student", entity_type="Student")]
    runner = SimulationRunner(engine=engine)
    actions = runner.run_round(1, "twitter", agents, "Test simulation")
    assert len(actions) == 1
    assert actions[0].agent_name == "Alice"
    assert actions[0].round_num == 1
    assert actions[0].action_type == "CREATE_POST"

@patch("app.services.simulation_runner.get_fast_llm_client")
def test_run_do_nothing(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat.return_value = "I'll just observe this round.\nACTION: DO_NOTHING"
    mock_get_client.return_value = mock_client
    engine = SimEngine()
    engine.create_platform("twitter")
    agents = [AgentProfile(agent_id=1, name="Bob", username="bob", persona="Professor", entity_type="Professor")]
    runner = SimulationRunner(engine=engine)
    actions = runner.run_round(1, "twitter", agents, "Test")
    assert actions[0].action_type == "DO_NOTHING"

@patch("app.services.simulation_runner.get_fast_llm_client")
def test_run_multiple_agents(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat.return_value = "ACTION: DO_NOTHING"
    mock_get_client.return_value = mock_client
    engine = SimEngine()
    engine.create_platform("twitter")
    agents = [
        AgentProfile(agent_id=1, name="Alice", username="alice", persona="Student", entity_type="Student"),
        AgentProfile(agent_id=2, name="Bob", username="bob", persona="Professor", entity_type="Professor"),
    ]
    runner = SimulationRunner(engine=engine)
    actions = runner.run_round(1, "twitter", agents, "Test")
    assert len(actions) == 2

@patch("app.services.simulation_runner.get_fast_llm_client")
def test_like_action(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    engine = SimEngine()
    engine.create_platform("twitter")
    post_id = engine.create_post("twitter", 99, "Existing post")
    mock_client.chat.return_value = f"ACTION: like_post\nPOST_ID: {post_id}"
    runner = SimulationRunner(engine=engine)
    agents = [AgentProfile(agent_id=1, name="Alice", username="alice", persona="Student", entity_type="Student")]
    actions = runner.run_round(1, "twitter", agents, "Test")
    assert actions[0].action_type == "LIKE"

@patch("app.services.simulation_runner.get_fast_llm_client")
def test_handles_llm_error(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat.side_effect = Exception("API Error")
    mock_get_client.return_value = mock_client
    engine = SimEngine()
    engine.create_platform("twitter")
    agents = [AgentProfile(agent_id=1, name="Alice", username="alice", persona="Student", entity_type="Student")]
    runner = SimulationRunner(engine=engine)
    actions = runner.run_round(1, "twitter", agents, "Test")
    assert len(actions) == 1
    assert actions[0].action_type == "DO_NOTHING"  # graceful fallback
