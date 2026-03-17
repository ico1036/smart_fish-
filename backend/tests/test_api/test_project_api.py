import pytest
from httpx import AsyncClient, ASGITransport
from app import create_app

@pytest.fixture
def app():
    return create_app()

@pytest.mark.asyncio
async def test_list_projects_empty(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/project/list")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

@pytest.mark.asyncio
async def test_upload_project(app, tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test document content for analysis")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with open(test_file, "rb") as f:
            resp = await client.post(
                "/api/project/upload",
                files={"files": ("test.txt", f, "text/plain")},
                data={"project_name": "Test Project", "simulation_requirement": "Test sim"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Test Project"
        assert data["project_id"] is not None
        assert len(data["files"]) == 1

@pytest.mark.asyncio
async def test_get_project(app, tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("Content")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Upload first
        with open(test_file, "rb") as f:
            upload_resp = await client.post(
                "/api/project/upload",
                files={"files": ("test.txt", f, "text/plain")},
                data={"project_name": "Get Test"},
            )
        project_id = upload_resp.json()["project_id"]
        # Then get
        resp = await client.get(f"/api/project/{project_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Get Test"

@pytest.mark.asyncio
async def test_get_project_not_found(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/project/nonexistent")
        assert resp.status_code == 404

@pytest.mark.asyncio
async def test_delete_project(app, tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("To delete")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with open(test_file, "rb") as f:
            upload_resp = await client.post(
                "/api/project/upload",
                files={"files": ("test.txt", f, "text/plain")},
                data={"project_name": "Delete Me"},
            )
        project_id = upload_resp.json()["project_id"]
        resp = await client.delete(f"/api/project/{project_id}")
        assert resp.status_code == 200
        # Verify deleted
        resp = await client.get(f"/api/project/{project_id}")
        assert resp.status_code == 404
