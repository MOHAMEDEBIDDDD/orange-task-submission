import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

# Load .env file from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

def _resolve_sqlite_url(url: str) -> str:
    """Anchor relative sqlite:/// paths to the project root so the DB opens
    regardless of the process's current working directory at launch time."""
    prefix = "sqlite:///"
    if url.startswith(prefix) and not url.startswith("sqlite:////"):
        rel_path = url[len(prefix):]
        if not Path(rel_path).is_absolute():
            return f"{prefix}{(BASE_DIR / rel_path).resolve().as_posix()}"
    return url

class Settings(BaseModel):
    # LLM Settings
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Search API
    serper_api_key: str = os.getenv("SERPER_API_KEY", "")

    # Database & Cache
    database_url: str = _resolve_sqlite_url(os.getenv("DATABASE_URL", "sqlite:///data/talentmatch.db"))
    cache_ttl_hours: int = int(os.getenv("CACHE_TTL_HOURS", "6"))

    # Sourcing Settings
    sourcing_timeout_seconds: int = int(os.getenv("SOURCING_TIMEOUT_SECONDS", "15"))
    max_candidates_per_source: int = int(os.getenv("MAX_CANDIDATES_PER_SOURCE", "5"))

    # Base Paths
    base_dir: Path = BASE_DIR
    data_dir: Path = BASE_DIR / "data"
    sources_config_path: Path = BASE_DIR / "config" / "sources_config.yaml"

settings = Settings()

# Ensure data directory exists
settings.data_dir.mkdir(parents=True, exist_ok=True)
