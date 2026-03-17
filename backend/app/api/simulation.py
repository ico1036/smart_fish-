"""Simulation API - create, prepare, run via WebSocket."""
import json
import asyncio
import threading
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from ..services.storage import get_storage
from ..services.profile_generator import ProfileGenerator
from ..services.simulation_runner import SimulationRunner
from ..services.sim_engine import SimEngine
from ..tools.graph_tools import get_graph_service
from ..models.simulation import SimState, SimStatus

router = APIRouter()
_tasks: dict[str, dict] = {}

class CreateSimRequest(BaseModel):
    project_id: str
    graph_id: str
    platforms: list[str] = ["twitter", "reddit"]
    max_rounds: int = 10

class PrepareRequest(BaseModel):
    simulation_requirement: str = ""
    entity_types: list[str] = []

@router.get("/history")
def simulation_history(limit: int = 20):
    """List recent simulations for history display."""
    storage = get_storage()
    # Scan simulations directory
    sim_dir = storage.data_dir / "simulations"
    if not sim_dir.exists():
        return []
    sims = []
    for f in sim_dir.glob("*.json"):
        try:
            state = storage.get_simulation(f.stem)
            if state:
                sims.append(state.model_dump())
        except Exception:
            continue
    sims.sort(key=lambda s: s.get("created_at", ""), reverse=True)
    return sims[:limit]

@router.post("/create")
def create_simulation(req: CreateSimRequest):
    state = SimState(project_id=req.project_id, graph_id=req.graph_id,
                     platforms=req.platforms, max_rounds=req.max_rounds)
    get_storage().save_simulation(state)
    return state.model_dump()

@router.get("/{sim_id}")
def get_simulation(sim_id: str):
    state = get_storage().get_simulation(sim_id)
    if not state:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return state.model_dump()

@router.post("/{sim_id}/prepare")
def prepare_simulation(sim_id: str, req: PrepareRequest):
    state = get_storage().get_simulation(sim_id)
    if not state:
        raise HTTPException(status_code=404, detail="Simulation not found")
    task_id = f"prepare-{sim_id}"
    _tasks[task_id] = {"status": "processing", "progress": 0, "message": "Starting..."}

    def _run():
        try:
            state.status = SimStatus.PREPARING
            get_storage().save_simulation(state)
            graph_svc = get_graph_service()
            gen = ProfileGenerator(graph_service=graph_svc)
            profiles = gen.generate(state.graph_id, req.simulation_requirement,
                                    entity_types=req.entity_types or None,
                                    on_progress=lambda p, m: _tasks[task_id].update({"progress": p, "message": m}))
            state.agents = profiles
            state.status = SimStatus.READY
            get_storage().save_simulation(state)
            _tasks[task_id] = {"status": "completed", "progress": 100, "agents_count": len(profiles)}
        except Exception as e:
            state.status = SimStatus.FAILED
            get_storage().save_simulation(state)
            _tasks[task_id] = {"status": "failed", "error": str(e)}

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return {"task_id": task_id, "status": "processing"}

@router.get("/{sim_id}/prepare/status")
def prepare_status(sim_id: str, task_id: str):
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return _tasks[task_id]

@router.websocket("/{sim_id}/stream")
async def simulation_stream(websocket: WebSocket, sim_id: str):
    await websocket.accept()
    state = get_storage().get_simulation(sim_id)
    if not state:
        await websocket.close(code=4004, reason="Simulation not found")
        return
    if not state.agents:
        await websocket.send_json({"type": "error", "message": "No agents prepared. Run /prepare first."})
        await websocket.close()
        return
    try:
        state.status = SimStatus.RUNNING
        get_storage().save_simulation(state)
        engine = SimEngine()
        for platform in state.platforms:
            engine.create_platform(platform)
        runner = SimulationRunner(engine=engine)
        for round_num in range(1, state.max_rounds + 1):
            await websocket.send_json({"type": "round_start", "round": round_num})
            for platform in state.platforms:
                actions = await asyncio.to_thread(
                    runner.run_round, round_num, platform, state.agents,
                    f"Round {round_num}/{state.max_rounds}")
                for action in actions:
                    state.actions.append(action)
                    await websocket.send_json({
                        "type": "agent_action", "round": round_num, "platform": platform,
                        "agent": action.agent_name, "action_type": action.action_type,
                        "content": action.content,
                        "message": f"{action.agent_name}: {action.action_type} {action.content[:80]}"})
            state.current_round = round_num
            get_storage().save_simulation(state)
            await websocket.send_json({"type": "round_end", "round": round_num})
        state.status = SimStatus.COMPLETED
        get_storage().save_simulation(state)
        await websocket.send_json({"type": "simulation_complete", "total_actions": len(state.actions)})
    except WebSocketDisconnect:
        state.status = SimStatus.STOPPED
        get_storage().save_simulation(state)
    except Exception as e:
        state.status = SimStatus.FAILED
        get_storage().save_simulation(state)
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
