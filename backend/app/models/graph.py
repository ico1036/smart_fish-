import uuid
from pydantic import BaseModel, Field

class GraphNode(BaseModel):
    node_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str
    labels: list[str] = []
    summary: str = ""
    attributes: dict = {}

class GraphEdge(BaseModel):
    edge_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_id: str
    target_id: str
    relation_type: str
    attributes: dict = {}

class GraphData(BaseModel):
    graph_id: str
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
