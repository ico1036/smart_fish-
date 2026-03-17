from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from ..services.storage import get_storage
from ..tools.graph_tools import get_graph_service
from ..config import settings

router = APIRouter()

class BuildRequest(BaseModel):
    project_id: str
    simulation_requirement: str = ""

_tasks: dict[str, dict] = {}

@router.post("/build")
async def build_graph(req: BuildRequest, background_tasks: BackgroundTasks):
    project = get_storage().get_project(req.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    task_id = f"task-{req.project_id}"
    _tasks[task_id] = {"status": "processing", "progress": 0, "message": "Starting graph build..."}

    # TODO: Wire up agent-powered graph building
    # For now, mark as pending SDK integration
    _tasks[task_id] = {"status": "pending_sdk", "progress": 0, "message": "Awaiting Claude Agent SDK integration"}

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
        return {"graph_id": graph_id, "nodes": nodes, "edges": edges}
    except KeyError:
        raise HTTPException(status_code=404, detail="Graph not found")
