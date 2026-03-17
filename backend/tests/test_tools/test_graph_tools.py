from app.tools.graph_tools import (
    create_knowledge_graph, add_entity, add_relationship,
    query_entities, get_entity_context, get_graph_overview, get_graph_service
)

def test_create_and_add():
    svc = get_graph_service()
    gid = create_knowledge_graph("test-tools-g1")
    assert gid == "test-tools-g1"
    result = add_entity(graph_id="test-tools-g1", node_id="n1", name="Alice", labels=["Person"], summary="A student")
    assert "Alice" in result
    results = query_entities(graph_id="test-tools-g1", query="Alice")
    assert len(results) >= 1

def test_add_relationship():
    create_knowledge_graph("test-tools-g2")
    add_entity("test-tools-g2", "n1", "Alice", ["Person"])
    add_entity("test-tools-g2", "n2", "Bob", ["Person"])
    result = add_relationship("test-tools-g2", "n1", "n2", "KNOWS")
    assert "KNOWS" in result

def test_get_entity_context():
    create_knowledge_graph("test-tools-g3")
    add_entity("test-tools-g3", "n1", "Alice", ["Person"])
    add_entity("test-tools-g3", "n2", "Bob", ["Person"])
    add_relationship("test-tools-g3", "n1", "n2", "KNOWS")
    ctx = get_entity_context("test-tools-g3", "n1")
    assert ctx["name"] == "Alice"
    assert len(ctx["edges"]) >= 1

def test_get_graph_overview():
    create_knowledge_graph("test-tools-g4")
    add_entity("test-tools-g4", "n1", "Alice", ["Person"])
    add_entity("test-tools-g4", "n2", "MIT", ["University"])
    overview = get_graph_overview("test-tools-g4")
    assert overview["node_count"] == 2
    assert "Person" in overview["entity_types"]
