import pytest
from httpx import AsyncClient, ASGITransport
from app import create_app

@pytest.fixture
def app():
    return create_app()

@pytest.mark.asyncio
async def test_create_simulation(app, tmp_path):
    # First upload a project
    test_file = tmp_path / "test.txt"
    test_file.write_text("Simulation content")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with open(test_file, "rb") as f:
            upload_resp = await client.post(
                "/api/project/upload",
                files={"files": ("test.txt", f, "text/plain")},
                data={"project_name": "Sim Test"},
            )
        project_id = upload_resp.json()["project_id"]

        resp = await client.post("/api/simulation/create", json={
            "project_id": project_id,
            "graph_id": "g1",
            "platforms": ["twitter"],
            "max_rounds": 5,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["simulation_id"] is not None
        assert data["status"] == "created"

@pytest.mark.asyncio
async def test_get_simulation_not_found(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/simulation/nonexistent")
        assert resp.status_code == 404
