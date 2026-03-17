from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.storage import get_storage
from ..models.report import Report

router = APIRouter()

_tasks: dict[str, dict] = {}

class GenerateRequest(BaseModel):
    simulation_id: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None

@router.post("/generate")
async def generate_report(req: GenerateRequest):
    state = get_storage().get_simulation(req.simulation_id)
    if not state:
        raise HTTPException(status_code=404, detail="Simulation not found")

    report = Report(simulation_id=req.simulation_id)
    get_storage().save_report(report)

    task_id = f"report-{report.report_id}"
    _tasks[task_id] = {"status": "pending_sdk", "report_id": report.report_id}

    return {"task_id": task_id, "report_id": report.report_id}

@router.get("/generate/status")
def report_status(task_id: str):
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return _tasks[task_id]

@router.get("/{report_id}")
def get_report(report_id: str):
    report = get_storage().get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report.model_dump()

@router.post("/{report_id}/chat")
async def chat_with_report(report_id: str, req: ChatRequest):
    report = get_storage().get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # TODO: Wire up Claude Agent SDK for actual chat
    return {
        "response": "Chat functionality pending Claude Agent SDK integration.",
        "conversation_id": req.conversation_id or "new",
    }
