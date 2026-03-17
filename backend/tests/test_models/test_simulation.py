from app.models.simulation import SimState, SimStatus, AgentProfile, AgentAction

def test_sim_state_creation():
    s = SimState(project_id="p1", graph_id="g1")
    assert s.status == SimStatus.CREATED
    assert s.simulation_id is not None
    assert s.max_rounds == 10

def test_agent_profile():
    p = AgentProfile(agent_id=1, name="Alice", username="alice")
    assert p.bio == ""
    assert p.age == 25

def test_agent_action():
    a = AgentAction(round_num=1, platform="twitter", agent_id=1, agent_name="Alice", action_type="CREATE_POST", content="Hello!")
    assert a.content == "Hello!"

def test_sim_status_enum():
    assert SimStatus.RUNNING == "running"
    assert SimStatus.COMPLETED == "completed"
