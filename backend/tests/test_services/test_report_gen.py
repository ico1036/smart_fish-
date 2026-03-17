import pytest
from unittest.mock import patch, MagicMock
from app.services.report_generator import ReportGenerator
from app.models.simulation import SimState, AgentProfile, AgentAction
from app.models.report import Report
from app.services.storage import Storage

def _make_sim_state(storage):
    state = SimState(project_id="p1", graph_id="g1")
    state.agents = [
        AgentProfile(agent_id=1, name="Alice", username="alice", entity_type="Student"),
        AgentProfile(agent_id=2, name="Bob", username="bob", entity_type="Professor"),
    ]
    state.actions = [
        AgentAction(round_num=1, platform="twitter", agent_id=1, agent_name="Alice", action_type="CREATE_POST", content="Hello!"),
        AgentAction(round_num=1, platform="twitter", agent_id=2, agent_name="Bob", action_type="LIKE", target_agent_id=1),
        AgentAction(round_num=2, platform="twitter", agent_id=1, agent_name="Alice", action_type="REPLY", content="Thanks!", target_agent_id=2),
    ]
    state.current_round = 2
    storage.save_simulation(state)
    return state

@patch("app.services.report_generator.get_llm_client")
def test_generate_report(mock_get_client, tmp_path):
    mock_client = MagicMock()
    mock_client.chat.return_value = "## Executive Summary\n\nThe simulation showed interesting patterns between students and professors."
    mock_get_client.return_value = mock_client
    storage = Storage(data_dir=tmp_path)
    state = _make_sim_state(storage)
    gen = ReportGenerator(storage=storage)
    report = gen.generate(state.simulation_id)
    assert report.simulation_id == state.simulation_id
    assert len(report.summary) > 20

@patch("app.services.report_generator.get_llm_client")
def test_report_uses_sim_data(mock_get_client, tmp_path):
    mock_client = MagicMock()
    mock_client.chat.return_value = "Analysis complete."
    mock_get_client.return_value = mock_client
    storage = Storage(data_dir=tmp_path)
    state = _make_sim_state(storage)
    gen = ReportGenerator(storage=storage)
    gen.generate(state.simulation_id)
    call_msgs = mock_client.chat.call_args[1]["messages"]
    user_msg = [m for m in call_msgs if m["role"] == "user"][0]["content"]
    assert "Alice" in user_msg or "Bob" in user_msg

@patch("app.services.report_generator.get_llm_client")
def test_report_saved(mock_get_client, tmp_path):
    mock_client = MagicMock()
    mock_client.chat.return_value = "Report content here."
    mock_get_client.return_value = mock_client
    storage = Storage(data_dir=tmp_path)
    state = _make_sim_state(storage)
    gen = ReportGenerator(storage=storage)
    report = gen.generate(state.simulation_id)
    loaded = storage.get_report(report.report_id)
    assert loaded is not None
    assert loaded.summary == "Report content here."

@patch("app.services.report_generator.get_llm_client")
def test_report_not_found(mock_get_client, tmp_path):
    mock_get_client.return_value = MagicMock()
    storage = Storage(data_dir=tmp_path)
    gen = ReportGenerator(storage=storage)
    with pytest.raises(ValueError, match="not found"):
        gen.generate("nonexistent")
