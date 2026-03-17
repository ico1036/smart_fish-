"""Report API - generate reports, chat, interview agents."""
from __future__ import annotations
import threading
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..services.storage import get_storage
from ..services.report_generator import ReportGenerator
from ..services.chat_service import ChatService

router = APIRouter()
_tasks: dict[str, dict] = {}

class GenerateRequest(BaseModel):
    simulation_id: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class InterviewRequest(BaseModel):
    simulation_id: str
    agent_id: int
    question: str

@router.post("/generate")
def generate_report(req: GenerateRequest):
    state = get_storage().get_simulation(req.simulation_id)
    if not state:
        raise HTTPException(status_code=404, detail="Simulation not found")
    task_id = f"report-{req.simulation_id}"
    _tasks[task_id] = {"status": "processing", "progress": 0}

    def _run():
        try:
            gen = ReportGenerator()
            report = gen.generate(req.simulation_id,
                                  on_progress=lambda p, m: _tasks[task_id].update({"progress": p, "message": m}))
            _tasks[task_id] = {"status": "completed", "progress": 100, "report_id": report.report_id}
        except Exception as e:
            _tasks[task_id] = {"status": "failed", "error": str(e)}

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return {"task_id": task_id, "status": "processing"}

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
def chat_with_report(report_id: str, req: ChatRequest):
    try:
        svc = ChatService()
        response = svc.chat_report(report_id, req.message, req.conversation_id)
        return {"response": response, "conversation_id": req.conversation_id or f"report-{report_id}"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/interview")
def interview_agent(req: InterviewRequest):
    try:
        svc = ChatService()
        response = svc.interview_agent(req.simulation_id, req.agent_id, req.question)
        return {"response": response, "agent_id": req.agent_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
