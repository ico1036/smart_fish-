import pytest
from app.services.graph_service import GraphService

@pytest.fixture
def svc():
    return GraphService()

def test_create_graph(svc):
    gid = svc.create_graph("test-graph")
    assert gid == "test-graph"
    assert svc.get_node_count(gid) == 0

def test_create_duplicate_graph(svc):
    svc.create_graph("g1")
    svc.create_graph("g1")  # should overwrite without error
    assert svc.get_node_count("g1") == 0

def test_get_nonexistent_graph(svc):
    with pytest.raises(KeyError):
        svc.get_graph("nonexistent")

def test_add_node_and_query(svc):
    svc.create_graph("g1")
    svc.add_node("g1", node_id="n1", name="Alice", labels=["Person"], attributes={"age": "30"})
    nodes = svc.get_nodes("g1")
    assert len(nodes) == 1
    assert nodes[0]["name"] == "Alice"
    assert nodes[0]["age"] == "30"

def test_add_multiple_nodes(svc):
    svc.create_graph("g1")
    svc.add_node("g1", "n1", "Alice", ["Person"])
    svc.add_node("g1", "n2", "Bob", ["Person"])
    svc.add_node("g1", "n3", "MIT", ["University"])
    assert svc.get_node_count("g1") == 3

def test_add_edge(svc):
    svc.create_graph("g1")
    svc.add_node("g1", "n1", "Alice", ["Person"])
    svc.add_node("g1", "n2", "Bob", ["Person"])
    svc.add_edge("g1", source_id="n1", target_id="n2", relation_type="KNOWS")
    edges = svc.get_edges("g1")
    assert len(edges) == 1
    assert edges[0]["relation_type"] == "KNOWS"
    assert edges[0]["source_id"] == "n1"
    assert edges[0]["target_id"] == "n2"

def test_filter_nodes_by_label(svc):
    svc.create_graph("g1")
    svc.add_node("g1", "n1", "Alice", ["Person"])
    svc.add_node("g1", "n2", "MIT", ["University"])
    persons = svc.get_nodes("g1", label_filter="Person")
    assert len(persons) == 1
    assert persons[0]["name"] == "Alice"

def test_search_nodes(svc):
    svc.create_graph("g1")
    svc.add_node("g1", "n1", "Alice", ["Student"], attributes={"summary": "CS student at MIT"})
    svc.add_node("g1", "n2", "Bob", ["Professor"], attributes={"summary": "Math teacher"})
    results = svc.search_nodes("g1", query="student")
    assert len(results) >= 1
    assert results[0]["name"] == "Alice"

def test_search_nodes_case_insensitive(svc):
    svc.create_graph("g1")
    svc.add_node("g1", "n1", "Alice", ["Person"])
    results = svc.search_nodes("g1", query="alice")
    assert len(results) == 1

def test_get_node_context(svc):
    svc.create_graph("g1")
    svc.add_node("g1", "n1", "Alice", ["Person"])
    svc.add_node("g1", "n2", "Bob", ["Person"])
    svc.add_node("g1", "n3", "Carol", ["Person"])
    svc.add_edge("g1", "n1", "n2", "KNOWS")
    svc.add_edge("g1", "n3", "n1", "FOLLOWS")
    ctx = svc.get_node_context("g1", "n1")
    assert ctx["node_id"] == "n1"
    assert ctx["name"] == "Alice"
    assert len(ctx["edges"]) == 2
    assert len(ctx["neighbors"]) == 2

def test_get_all_graphs(svc):
    svc.create_graph("g1")
    svc.create_graph("g2")
    assert len(svc.list_graphs()) == 2

def test_delete_graph(svc):
    svc.create_graph("g1")
    svc.delete_graph("g1")
    with pytest.raises(KeyError):
        svc.get_graph("g1")
