import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")
    CLAUDE_SIM_MODEL: str = os.getenv("CLAUDE_SIMULATION_MODEL", "claude-haiku-4-5")

    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "5001"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    BASE_DIR: Path = Path(__file__).parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    DATA_DIR: Path = BASE_DIR / "data"

    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: set = {"pdf", "md", "txt", "markdown"}

    DEFAULT_CHUNK_SIZE: int = 500
    DEFAULT_CHUNK_OVERLAP: int = 50

    SIM_MAX_ROUNDS: int = int(os.getenv("SIM_MAX_ROUNDS", "10"))
    SIM_PLATFORMS: list = ["twitter", "reddit"]

settings = Settings()
