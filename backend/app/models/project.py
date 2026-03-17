import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class ProjectStatus(str, Enum):
    CREATED = "created"
    ONTOLOGY_GENERATED = "ontology_generated"
    GRAPH_BUILDING = "graph_building"
    GRAPH_COMPLETED = "graph_completed"
    FAILED = "failed"

class UploadedFile(BaseModel):
    filename: str
    size: int
    text_content: str = ""

class EntityType(BaseModel):
    name: str
    description: str
    attributes: list[str] = []

class EdgeType(BaseModel):
    name: str
    description: str
    source_types: list[str] = []
    target_types: list[str] = []

class Ontology(BaseModel):
    entity_types: list[EntityType] = []
    edge_types: list[EdgeType] = []
    analysis_summary: str = ""

class Project(BaseModel):
    project_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str
    status: ProjectStatus = ProjectStatus.CREATED
    files: list[UploadedFile] = []
    ontology: Optional[Ontology] = None
    graph_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
