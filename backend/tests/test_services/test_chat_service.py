import pytest
from unittest.mock import patch, MagicMock
from app.services.chat_service import ChatService
from app.models.report import Report
from app.models.simulation import SimState, AgentProfile, AgentAction
from app.services.storage import Storage

@patch("app.services.chat_service.get_llm_client")
def test_chat_with_report(mock_get_client, tmp_path):
    mock_client = MagicMock()
    mock_client.chat.return_value = "Students were more active than professors."
    mock_get_client.return_value = mock_client
    storage = Storage(data_dir=tmp_path)
    report = Report(simulation_id="sim1", summary="Students posted 3x more than professors.")
    storage.save_report(report)
    svc = ChatService(storage=storage)
    response = svc.chat_report(report.report_id, "Who was more active?")
    assert len(response) > 5

@patch("app.services.chat_service.get_fast_llm_client")
def test_interview_agent(mock_get_client, tmp_path):
    mock_client = MagicMock()
    mock_client.chat.return_value = "As a student, I felt compelled to share my opinions."
    mock_get_client.return_value = mock_client
    storage = Storage(data_dir=tmp_path)
    state = SimState(project_id="p1", graph_id="g1")
    state.agents = [AgentProfile(agent_id=1, name="Alice", username="alice", persona="A passionate CS student")]
    state.actions = [AgentAction(round_num=1, platform="twitter", agent_id=1, agent_name="Alice", action_type="CREATE_POST", content="Policy change is unfair!")]
    storage.save_simulation(state)
    svc = ChatService(storage=storage)
    response = svc.interview_agent(state.simulation_id, 1, "Why did you post?")
    assert len(response) > 10

@patch("app.services.chat_service.get_llm_client")
def test_chat_maintains_history(mock_get_client, tmp_path):
    mock_client = MagicMock()
    mock_client.chat.side_effect = ["First answer.", "Second answer."]
    mock_get_client.return_value = mock_client
    storage = Storage(data_dir=tmp_path)
    report = Report(simulation_id="sim1", summary="Report content.")
    storage.save_report(report)
    svc = ChatService(storage=storage)
    svc.chat_report(report.report_id, "Q1", conversation_id="conv-1")
    svc.chat_report(report.report_id, "Q2", conversation_id="conv-1")
    second_call_msgs = mock_client.chat.call_args_list[1][1]["messages"]
    assert len(second_call_msgs) >= 4  # system + Q1 + A1 + Q2

@patch("app.services.chat_service.get_fast_llm_client")
def test_interview_not_found(mock_get_client, tmp_path):
    mock_get_client.return_value = MagicMock()
    storage = Storage(data_dir=tmp_path)
    svc = ChatService(storage=storage)
    with pytest.raises(ValueError, match="not found"):
        svc.interview_agent("fake", 1, "question")
