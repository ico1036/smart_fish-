import uuid
from enum import Enum
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class SimStatus(str, Enum):
    CREATED = "created"
    PREPARING = "preparing"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    STOPPED = "stopped"
    FAILED = "failed"

class AgentProfile(BaseModel):
    agent_id: int
    name: str
    username: str
    bio: str = ""
    persona: str = ""
    age: int = 25
    profession: str = ""
    mbti: str = ""
    entity_type: str = ""

class AgentAction(BaseModel):
    round_num: int
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    platform: str
    agent_id: int
    agent_name: str
    action_type: str
    content: str = ""
    target_agent_id: Optional[int] = None
    target_post_id: Optional[str] = None

class SimState(BaseModel):
    simulation_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str
    graph_id: str
    status: SimStatus = SimStatus.CREATED
    platforms: List[str] = ["twitter", "reddit"]
    agents: List[AgentProfile] = []
    actions: List[AgentAction] = []
    current_round: int = 0
    max_rounds: int = 10
    created_at: datetime = Field(default_factory=datetime.now)
