import pytest
from app.services.storage import Storage
from app.models.project import Project, ProjectStatus
from app.models.simulation import SimState, SimStatus, AgentProfile, AgentAction
from app.models.report import Report, ReportSection


@pytest.fixture
def storage(tmp_path):
    return Storage(data_dir=tmp_path)


# --- Project tests ---
def test_save_and_load_project(storage):
    p = Project(name="test-project")
    storage.save_project(p)
    loaded = storage.get_project(p.project_id)
    assert loaded is not None
    assert loaded.name == "test-project"
    assert loaded.status == ProjectStatus.CREATED


def test_get_nonexistent_project(storage):
    assert storage.get_project("nonexistent") is None


def test_list_projects(storage):
    storage.save_project(Project(name="p1"))
    storage.save_project(Project(name="p2"))
    projects = storage.list_projects()
    assert len(projects) == 2


def test_delete_project(storage):
    p = Project(name="to-delete")
    storage.save_project(p)
    storage.delete_project(p.project_id)
    assert storage.get_project(p.project_id) is None


def test_update_project(storage):
    p = Project(name="test")
    storage.save_project(p)
    p.status = ProjectStatus.GRAPH_COMPLETED
    storage.save_project(p)
    loaded = storage.get_project(p.project_id)
    assert loaded.status == ProjectStatus.GRAPH_COMPLETED


# --- Simulation tests ---
def test_save_and_load_simulation(storage):
    state = SimState(project_id="p1", graph_id="g1")
    state.agents.append(AgentProfile(agent_id=1, name="Alice", username="alice"))
    storage.save_simulation(state)
    loaded = storage.get_simulation(state.simulation_id)
    assert loaded is not None
    assert len(loaded.agents) == 1
    assert loaded.agents[0].name == "Alice"


def test_simulation_with_actions(storage):
    state = SimState(project_id="p1", graph_id="g1")
    state.actions.append(
        AgentAction(
            round_num=1,
            platform="twitter",
            agent_id=1,
            agent_name="Alice",
            action_type="CREATE_POST",
            content="Hello",
        )
    )
    storage.save_simulation(state)
    loaded = storage.get_simulation(state.simulation_id)
    assert len(loaded.actions) == 1
    assert loaded.actions[0].content == "Hello"


def test_get_nonexistent_simulation(storage):
    assert storage.get_simulation("nonexistent") is None


# --- Report tests ---
def test_save_and_load_report(storage):
    report = Report(simulation_id="sim1", summary="Test summary")
    report.sections.append(ReportSection(title="Intro", content="Content", order=1))
    storage.save_report(report)
    loaded = storage.get_report(report.report_id)
    assert loaded is not None
    assert loaded.summary == "Test summary"
    assert len(loaded.sections) == 1


def test_get_nonexistent_report(storage):
    assert storage.get_report("nonexistent") is None
