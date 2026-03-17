from app.models.graph import GraphNode, GraphEdge, GraphData

def test_graph_node():
    n = GraphNode(name="Alice", labels=["Person"], summary="A student")
    assert n.node_id is not None
    assert n.name == "Alice"

def test_graph_edge():
    e = GraphEdge(source_id="n1", target_id="n2", relation_type="KNOWS")
    assert e.relation_type == "KNOWS"

def test_graph_data():
    g = GraphData(graph_id="g1")
    assert g.nodes == []
    assert g.edges == []
