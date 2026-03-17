from app.tools.report_tools import (
    get_simulation_actions, get_agent_behavior_summary, get_interaction_network
)
from app.models.simulation import SimState, AgentProfile, AgentAction
from app.services.storage import Storage

def test_get_simulation_actions(tmp_path):
    storage = Storage(data_dir=tmp_path)
    state = SimState(project_id="p1", graph_id="g1")
    state.actions = [
        AgentAction(round_num=1, platform="twitter", agent_id=1, agent_name="Alice", action_type="CREATE_POST", content="Hello"),
        AgentAction(round_num=1, platform="twitter", agent_id=2, agent_name="Bob", action_type="LIKE", content=""),
        AgentAction(round_num=2, platform="twitter", agent_id=1, agent_name="Alice", action_type="REPLY", content="Thanks"),
    ]
    storage.save_simulation(state)
    actions = get_simulation_actions(state.simulation_id, storage=storage)
    assert len(actions) == 3

def test_get_actions_filtered_by_round(tmp_path):
    storage = Storage(data_dir=tmp_path)
    state = SimState(project_id="p1", graph_id="g1")
    state.actions = [
        AgentAction(round_num=1, platform="twitter", agent_id=1, agent_name="Alice", action_type="CREATE_POST"),
        AgentAction(round_num=2, platform="twitter", agent_id=1, agent_name="Alice", action_type="REPLY"),
    ]
    storage.save_simulation(state)
    actions = get_simulation_actions(state.simulation_id, round_num=1, storage=storage)
    assert len(actions) == 1

def test_get_agent_behavior_summary(tmp_path):
    storage = Storage(data_dir=tmp_path)
    state = SimState(project_id="p1", graph_id="g1")
    state.agents = [AgentProfile(agent_id=1, name="Alice", username="alice")]
    state.actions = [
        AgentAction(round_num=1, platform="twitter", agent_id=1, agent_name="Alice", action_type="CREATE_POST"),
        AgentAction(round_num=2, platform="twitter", agent_id=1, agent_name="Alice", action_type="LIKE"),
        AgentAction(round_num=2, platform="twitter", agent_id=1, agent_name="Alice", action_type="CREATE_POST"),
    ]
    storage.save_simulation(state)
    summary = get_agent_behavior_summary(state.simulation_id, 1, storage=storage)
    assert summary["name"] == "Alice"
    assert summary["total_actions"] == 3
    assert summary["action_breakdown"]["CREATE_POST"] == 2

def test_get_interaction_network(tmp_path):
    storage = Storage(data_dir=tmp_path)
    state = SimState(project_id="p1", graph_id="g1")
    state.actions = [
        AgentAction(round_num=1, platform="twitter", agent_id=1, agent_name="Alice", action_type="REPLY", target_agent_id=2),
        AgentAction(round_num=1, platform="twitter", agent_id=2, agent_name="Bob", action_type="LIKE", target_agent_id=1),
    ]
    storage.save_simulation(state)
    network = get_interaction_network(state.simulation_id, storage=storage)
    assert network["total"] == 2
    assert len(network["interactions"]) == 2
