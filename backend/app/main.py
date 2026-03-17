import uvicorn
from .config import settings
from . import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=settings.DEBUG)
