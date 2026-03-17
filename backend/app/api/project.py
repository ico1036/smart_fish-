import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ..services.storage import get_storage
from ..models.project import Project, UploadedFile
from ..utils.file_parser import extract_text
from ..config import settings

router = APIRouter()

@router.get("/list")
def list_projects():
    return [p.model_dump() for p in get_storage().list_projects()]

@router.get("/{project_id}")
def get_project(project_id: str):
    p = get_storage().get_project(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p.model_dump()

@router.post("/upload")
async def upload_and_create(
    files: list[UploadFile] = File(...),
    project_name: str = Form("Untitled"),
    simulation_requirement: str = Form(""),
):
    project = Project(name=project_name)
    upload_dir = settings.UPLOAD_DIR / project.project_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    uploaded = []
    for f in files:
        ext = f.filename.rsplit(".", 1)[-1].lower() if f.filename else ""
        if ext not in settings.ALLOWED_EXTENSIONS:
            continue
        file_path = upload_dir / f.filename
        content = await f.read()
        file_path.write_bytes(content)
        text = extract_text(str(file_path))
        uploaded.append(UploadedFile(filename=f.filename, size=len(content), text_content=text))

    project.files = uploaded
    get_storage().save_project(project)
    return project.model_dump()

@router.delete("/{project_id}")
def delete_project(project_id: str):
    get_storage().delete_project(project_id)
    upload_dir = settings.UPLOAD_DIR / project_id
    if upload_dir.exists():
        shutil.rmtree(upload_dir)
    return {"status": "deleted"}
