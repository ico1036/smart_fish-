"""Graph API - ontology generation, graph building, data retrieval."""
import threading
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from ..services.storage import get_storage
from ..services.ontology_service import OntologyService
from ..services.graph_builder import GraphBuilder
from ..tools.graph_tools import get_graph_service
from ..utils.text_processor import split_into_chunks
from ..utils.file_parser import extract_text
from ..models.project import Project, UploadedFile, ProjectStatus, Ontology, EntityType, EdgeType
from ..config import settings

router = APIRouter()

class BuildRequest(BaseModel):
    project_id: str
    simulation_requirement: str = ""
    chunk_size: int = 500
    chunk_overlap: int = 50

_tasks: dict[str, dict] = {}

@router.post("/ontology/generate")
async def generate_ontology(
    files: list[UploadFile] = File(...),
    simulation_requirement: str = Form(""),
):
    """Upload files and generate ontology in one step."""
    project = Project(name="Untitled")
    upload_dir = settings.UPLOAD_DIR / project.project_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    uploaded = []
    for f in files:
        ext = f.filename.rsplit(".", 1)[-1].lower() if f.filename else ""
        if ext not in settings.ALLOWED_EXTENSIONS:
            continue
        file_path = upload_dir / f.filename
        content = await f.read()
        file_path.write_bytes(content)
        text = extract_text(str(file_path))
        uploaded.append(UploadedFile(filename=f.filename, size=len(content), text_content=text))

    if not uploaded:
        raise HTTPException(status_code=400, detail="No valid files uploaded")

    project.files = uploaded
    combined_text = "\n\n---\n\n".join(f.text_content for f in uploaded if f.text_content)
    if not combined_text:
        raise HTTPException(status_code=400, detail="No text content in uploaded files")

    service = OntologyService()
    ontology = await service.agenerate(simulation_requirement, combined_text)
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
        raw_nodes = svc.get_nodes(graph_id)
        raw_edges = svc.get_edges(graph_id)
        # Map field names for frontend compatibility
        nodes = [{"uuid": n.pop("node_id"), **n} for n in raw_nodes]
        edges = [{"source_node_uuid": e.pop("source_id"), "target_node_uuid": e.pop("target_id"), **e} for e in raw_edges]
        return {"graph_id": graph_id, "nodes": nodes, "edges": edges, "node_count": len(nodes), "edge_count": len(edges)}
    except KeyError:
        raise HTTPException(status_code=404, detail="Graph not found")
