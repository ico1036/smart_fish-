import networkx as nx


class GraphService:
    def __init__(self):
        self._graphs: dict[str, nx.DiGraph] = {}

    def create_graph(self, graph_id: str) -> str:
        self._graphs[graph_id] = nx.DiGraph()
        return graph_id

    def get_graph(self, graph_id: str) -> nx.DiGraph:
        if graph_id not in self._graphs:
            raise KeyError(f"Graph {graph_id} not found")
        return self._graphs[graph_id]

    def list_graphs(self) -> list[str]:
        return list(self._graphs.keys())

    def delete_graph(self, graph_id: str):
        if graph_id in self._graphs:
            del self._graphs[graph_id]

    def add_node(self, graph_id: str, node_id: str, name: str, labels: list[str] = None, attributes: dict = None):
        g = self.get_graph(graph_id)
        g.add_node(node_id, name=name, labels=labels or [], **(attributes or {}))

    def add_edge(self, graph_id: str, source_id: str, target_id: str, relation_type: str, attributes: dict = None):
        g = self.get_graph(graph_id)
        g.add_edge(source_id, target_id, relation_type=relation_type, **(attributes or {}))

    def get_nodes(self, graph_id: str, label_filter: str = None) -> list[dict]:
        g = self.get_graph(graph_id)
        nodes = []
        for nid, data in g.nodes(data=True):
            if label_filter and label_filter not in data.get("labels", []):
                continue
            nodes.append({"node_id": nid, **data})
        return nodes

    def get_edges(self, graph_id: str) -> list[dict]:
        g = self.get_graph(graph_id)
        return [
            {"source_id": u, "target_id": v, **data}
            for u, v, data in g.edges(data=True)
        ]

    def get_node_count(self, graph_id: str) -> int:
        return self.get_graph(graph_id).number_of_nodes()

    def search_nodes(self, graph_id: str, query: str) -> list[dict]:
        q = query.lower()
        results = []
        for node in self.get_nodes(graph_id):
            searchable = f"{node.get('name', '')} {' '.join(node.get('labels', []))} {node.get('summary', '')}".lower()
            if q in searchable:
                results.append(node)
        return results

    def get_node_context(self, graph_id: str, node_id: str) -> dict:
        g = self.get_graph(graph_id)
        node_data = {"node_id": node_id, **g.nodes[node_id]}
        neighbors = []
        edges = []
        for u, v, data in g.out_edges(node_id, data=True):
            edges.append({"source_id": u, "target_id": v, **data})
            neighbors.append({"node_id": v, **g.nodes[v]})
        for u, v, data in g.in_edges(node_id, data=True):
            edges.append({"source_id": u, "target_id": v, **data})
            neighbors.append({"node_id": u, **g.nodes[u]})
        node_data["edges"] = edges
        node_data["neighbors"] = neighbors
        return node_data
