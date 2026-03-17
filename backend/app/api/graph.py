"""Graph API - ontology generation, graph building, data retrieval."""
import threading
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.storage import get_storage
from ..services.ontology_service import OntologyService
from ..services.graph_builder import GraphBuilder
from ..tools.graph_tools import get_graph_service
from ..utils.text_processor import split_into_chunks
from ..models.project import ProjectStatus, Ontology, EntityType, EdgeType

router = APIRouter()

class OntologyRequest(BaseModel):
    project_id: str
    simulation_requirement: str = ""

class BuildRequest(BaseModel):
    project_id: str
    simulation_requirement: str = ""
    chunk_size: int = 500
    chunk_overlap: int = 50

_tasks: dict[str, dict] = {}

@router.post("/ontology/generate")
def generate_ontology(req: OntologyRequest):
    project = get_storage().get_project(req.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    combined_text = "\n\n---\n\n".join(f.text_content for f in project.files if f.text_content)
    if not combined_text:
        raise HTTPException(status_code=400, detail="No text content in uploaded files")
    service = OntologyService()
    ontology = service.generate(req.simulation_requirement, combined_text)
    project.ontology = Ontology(
        entity_types=[EntityType(**et) for et in ontology["entity_types"]],
        edge_types=[EdgeType(**et) for et in ontology["edge_types"]],
        analysis_summary=ontology.get("analysis_summary", ""),
    )
    project.status = ProjectStatus.ONTOLOGY_GENERATED
    get_storage().save_project(project)
    return {"project_id": project.project_id, "ontology": ontology}

@router.post("/build")
def build_graph(req: BuildRequest):
    project = get_storage().get_project(req.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not project.ontology:
        raise HTTPException(status_code=400, detail="Generate ontology first")
    task_id = f"build-{req.project_id}"
    _tasks[task_id] = {"status": "processing", "progress": 0, "message": "Starting..."}

    def _run():
        try:
            combined_text = "\n\n".join(f.text_content for f in project.files if f.text_content)
            chunks = split_into_chunks(combined_text, req.chunk_size, req.chunk_overlap)
            ontology = {
                "entity_types": [et.model_dump() for et in project.ontology.entity_types],
                "edge_types": [et.model_dump() for et in project.ontology.edge_types],
            }
            graph_svc = get_graph_service()
            builder = GraphBuilder(graph_service=graph_svc)
            graph_id = f"graph-{req.project_id}"
            builder.build(graph_id, ontology, chunks,
                          on_progress=lambda p, m: _tasks[task_id].update({"progress": p, "message": m}))
            project.graph_id = graph_id
            project.status = ProjectStatus.GRAPH_COMPLETED
            get_storage().save_project(project)
            node_count = graph_svc.get_node_count(graph_id)
            edge_count = len(graph_svc.get_edges(graph_id))
            _tasks[task_id] = {"status": "completed", "progress": 100,
                               "result": {"graph_id": graph_id, "node_count": node_count, "edge_count": edge_count}}
        except Exception as e:
            _tasks[task_id] = {"status": "failed", "progress": 0, "error": str(e)}
            project.status = ProjectStatus.FAILED
            get_storage().save_project(project)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return {"task_id": task_id, "status": "processing"}

@router.get("/build/status")
def build_status(task_id: str):
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return _tasks[task_id]

@router.get("/{graph_id}")
def get_graph_data(graph_id: str):
    svc = get_graph_service()
    try:
        nodes = svc.get_nodes(graph_id)
        edges = svc.get_edges(graph_id)
        return {"graph_id": graph_id, "nodes": nodes, "edges": edges, "node_count": len(nodes), "edge_count": len(edges)}
    except KeyError:
        raise HTTPException(status_code=404, detail="Graph not found")
