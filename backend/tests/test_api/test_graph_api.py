import pytest
from httpx import AsyncClient, ASGITransport
from app import create_app

@pytest.fixture
def app():
    return create_app()

@pytest.mark.asyncio
async def test_build_graph_project_not_found(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/graph/build", json={"project_id": "fake", "simulation_requirement": "test"})
        assert resp.status_code == 404

@pytest.mark.asyncio
async def test_get_graph_not_found(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/graph/nonexistent")
        assert resp.status_code == 404

@pytest.mark.asyncio
async def test_build_status_not_found(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/graph/build/status?task_id=fake")
        assert resp.status_code == 404
