from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    app = FastAPI(title="SmartFish", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    from .api import project, graph, simulation, report
    app.include_router(project.router, prefix="/api/project")
    app.include_router(graph.router, prefix="/api/graph")
    app.include_router(simulation.router, prefix="/api/simulation")
    app.include_router(report.router, prefix="/api/report")
    return app
