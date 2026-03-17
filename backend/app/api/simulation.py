from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from ..services.storage import get_storage
from ..models.simulation import SimState

router = APIRouter()

class CreateSimRequest(BaseModel):
    project_id: str
    graph_id: str
    platforms: list[str] = ["twitter", "reddit"]
    max_rounds: int = 10

@router.post("/create")
def create_simulation(req: CreateSimRequest):
    state = SimState(
        project_id=req.project_id,
        graph_id=req.graph_id,
        platforms=req.platforms,
        max_rounds=req.max_rounds,
    )
    get_storage().save_simulation(state)
    return state.model_dump()

@router.get("/{sim_id}")
def get_simulation(sim_id: str):
    state = get_storage().get_simulation(sim_id)
    if not state:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return state.model_dump()

@router.websocket("/{sim_id}/stream")
async def simulation_stream(websocket: WebSocket, sim_id: str):
    """WebSocket endpoint for real-time simulation streaming."""
    await websocket.accept()

    state = get_storage().get_simulation(sim_id)
    if not state:
        await websocket.close(code=4004, reason="Simulation not found")
        return

    try:
        # TODO: Wire up Claude Agent SDK for actual simulation
        await websocket.send_json({
            "type": "info",
            "message": "Simulation WebSocket connected. Awaiting Claude Agent SDK integration.",
        })
    except WebSocketDisconnect:
        pass
    finally:
        try:
            await websocket.close()
        except RuntimeError:
            pass
