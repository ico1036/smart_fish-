from __future__ import annotations
import json
from pathlib import Path
from ..models.project import Project
from ..models.simulation import SimState
from ..models.report import Report
from ..config import settings

class Storage:
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or settings.DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "projects").mkdir(exist_ok=True)
        (self.data_dir / "simulations").mkdir(exist_ok=True)
        (self.data_dir / "reports").mkdir(exist_ok=True)

    def save_project(self, project: Project):
        path = self.data_dir / "projects" / f"{project.project_id}.json"
        path.write_text(project.model_dump_json(indent=2), encoding="utf-8")

    def get_project(self, project_id: str) -> Project | None:
        path = self.data_dir / "projects" / f"{project_id}.json"
        if not path.exists():
            return None
        return Project.model_validate_json(path.read_text(encoding="utf-8"))

    def list_projects(self) -> list[Project]:
        projects = []
        for f in (self.data_dir / "projects").glob("*.json"):
            projects.append(Project.model_validate_json(f.read_text(encoding="utf-8")))
        return sorted(projects, key=lambda p: p.created_at, reverse=True)

    def delete_project(self, project_id: str):
        path = self.data_dir / "projects" / f"{project_id}.json"
        if path.exists():
            path.unlink()

    def save_simulation(self, state: SimState):
        path = self.data_dir / "simulations" / f"{state.simulation_id}.json"
        path.write_text(state.model_dump_json(indent=2), encoding="utf-8")

    def get_simulation(self, sim_id: str) -> SimState | None:
        path = self.data_dir / "simulations" / f"{sim_id}.json"
        if not path.exists():
            return None
        return SimState.model_validate_json(path.read_text(encoding="utf-8"))

    def save_report(self, report: Report):
        path = self.data_dir / "reports" / f"{report.report_id}.json"
        path.write_text(report.model_dump_json(indent=2), encoding="utf-8")

    def get_report(self, report_id: str) -> Report | None:
        path = self.data_dir / "reports" / f"{report_id}.json"
        if not path.exists():
            return None
        return Report.model_validate_json(path.read_text(encoding="utf-8"))

_storage: Storage | None = None

def get_storage() -> Storage:
    global _storage
    if _storage is None:
        _storage = Storage()
    return _storage
