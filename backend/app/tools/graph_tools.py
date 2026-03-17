from ..services.graph_service import GraphService

_graph_service = GraphService()

def get_graph_service() -> GraphService:
    return _graph_service

def create_knowledge_graph(graph_id: str) -> str:
    """Create a new knowledge graph. Returns the graph ID."""
    return _graph_service.create_graph(graph_id)

def add_entity(graph_id: str, node_id: str, name: str, labels: list, summary: str = "", attributes: dict = None) -> str:
    """Add an entity node to the knowledge graph."""
    attrs = attributes or {}
    attrs["summary"] = summary
    _graph_service.add_node(graph_id, node_id, name, labels, attrs)
    return f"Added entity {name} ({', '.join(labels)})"

def add_relationship(graph_id: str, source_id: str, target_id: str, relation_type: str, attributes: dict = None) -> str:
    """Add a relationship edge between two entities."""
    _graph_service.add_edge(graph_id, source_id, target_id, relation_type, attributes)
    return f"Added {relation_type} edge: {source_id} -> {target_id}"

def query_entities(graph_id: str, query: str) -> list:
    """Search entities by name, label, or summary text."""
    return _graph_service.search_nodes(graph_id, query)

def get_entity_context(graph_id: str, node_id: str) -> dict:
    """Get an entity with all its relationships and neighbors."""
    return _graph_service.get_node_context(graph_id, node_id)

def get_graph_overview(graph_id: str) -> dict:
    """Get overview statistics of the knowledge graph."""
    nodes = _graph_service.get_nodes(graph_id)
    edges = _graph_service.get_edges(graph_id)
    label_counts = {}
    for n in nodes:
        for lbl in n.get("labels", []):
            label_counts[lbl] = label_counts.get(lbl, 0) + 1
    return {
        "graph_id": graph_id,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "entity_types": label_counts,
    }
