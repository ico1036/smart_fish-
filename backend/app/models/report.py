import uuid
from datetime import datetime
from pydantic import BaseModel, Field

class ReportSection(BaseModel):
    title: str
    content: str
    order: int

class Report(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    simulation_id: str
    sections: list[ReportSection] = []
    summary: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
