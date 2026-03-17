from app.agents.ontology_agent import ONTOLOGY_AGENT_CONFIG, ONTOLOGY_SYSTEM_PROMPT
from app.agents.graph_agent import GRAPH_AGENT_CONFIG, GRAPH_AGENT_PROMPT
from app.agents.sim_agent import create_sim_agent_config, SIM_AGENT_PROMPT_TEMPLATE
from app.agents.report_agent import (
    REPORT_AGENT_CONFIG, REPORT_AGENT_PROMPT,
    create_interview_agent_config, INTERVIEW_PROMPT_TEMPLATE,
)

def test_ontology_agent_config():
    assert ONTOLOGY_AGENT_CONFIG["name"] == "ontology-builder"
    assert "parse_document" in ONTOLOGY_AGENT_CONFIG["tools"]
    assert "entity types" in ONTOLOGY_SYSTEM_PROMPT.lower()

def test_graph_agent_config():
    assert GRAPH_AGENT_CONFIG["name"] == "graph-builder"
    assert "add_entity" in GRAPH_AGENT_CONFIG["tools"]

def test_sim_agent_creation():
    profile = {
        "name": "Alice",
        "persona": "A curious student",
        "age": 22,
        "profession": "Student",
        "mbti": "INFP",
        "bio": "Loves learning",
        "entity_type": "Student",
    }
    config = create_sim_agent_config(profile, "Test simulation", round_num=1, platform="twitter")
    assert "Alice" in config["system_prompt"]
    assert config["model"] == "haiku"
    assert "create_post" in config["tools"]

def test_sim_agent_default_values():
    profile = {"name": "Bob"}
    config = create_sim_agent_config(profile, "Context", 1, "reddit")
    assert "Bob" in config["system_prompt"]
    assert "25" in config["system_prompt"]  # default age

def test_report_agent_config():
    assert REPORT_AGENT_CONFIG["name"] == "report-writer"
    assert "get_simulation_actions" in REPORT_AGENT_CONFIG["tools"]
    assert "Executive Summary" in REPORT_AGENT_PROMPT

def test_interview_agent_creation():
    profile = {"name": "Alice", "persona": "A student who loves debate"}
    config = create_interview_agent_config(profile, "Posted 3 times, liked 5 posts")
    assert "Alice" in config["system_prompt"]
    assert "Posted 3 times" in config["system_prompt"]
    assert config["tools"] == []
    assert config["model"] == "haiku"
