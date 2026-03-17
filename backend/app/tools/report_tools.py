from ..services.storage import Storage, get_storage

def get_simulation_actions(simulation_id: str, round_num: int = None, agent_id: int = None, action_type: str = None, storage: Storage = None) -> list[dict]:
    """Query simulation actions with optional filters."""
    storage = storage or get_storage()
    state = storage.get_simulation(simulation_id)
    if not state:
        return []
    actions = state.actions
    if round_num is not None:
        actions = [a for a in actions if a.round_num == round_num]
    if agent_id is not None:
        actions = [a for a in actions if a.agent_id == agent_id]
    if action_type:
        actions = [a for a in actions if a.action_type == action_type]
    return [a.model_dump() for a in actions]

def get_agent_behavior_summary(simulation_id: str, agent_id: int, storage: Storage = None) -> dict:
    """Get a summary of a specific agent's behavior."""
    storage = storage or get_storage()
    state = storage.get_simulation(simulation_id)
    if not state:
        return {"error": "Simulation not found"}
    agent_actions = [a for a in state.actions if a.agent_id == agent_id]
    action_counts = {}
    for a in agent_actions:
        action_counts[a.action_type] = action_counts.get(a.action_type, 0) + 1
    profile = next((p for p in state.agents if p.agent_id == agent_id), None)
    return {
        "agent_id": agent_id,
        "name": profile.name if profile else "Unknown",
        "total_actions": len(agent_actions),
        "action_breakdown": action_counts,
        "rounds_active": len(set(a.round_num for a in agent_actions)),
    }

def get_interaction_network(simulation_id: str, storage: Storage = None) -> dict:
    """Get the interaction network."""
    storage = storage or get_storage()
    state = storage.get_simulation(simulation_id)
    if not state:
        return {"error": "Simulation not found"}
    interactions = []
    for a in state.actions:
        if a.target_agent_id is not None:
            interactions.append({
                "source": a.agent_id,
                "target": a.target_agent_id,
                "type": a.action_type,
                "round": a.round_num,
            })
    return {"interactions": interactions, "total": len(interactions)}
