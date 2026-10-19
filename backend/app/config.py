import os
from pathlib import Path
from typing import List
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseModel):
    project_name: str = "Office Knowledge Assistant"
    app_display_name: str = "Office Knowledge Assistant"
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    port: int = int(os.getenv("PORT", "8000"))
    host: str = os.getenv("HOST", "127.0.0.1")
    cors_origins: List[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    ]

    # Auth & Security
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production-office-knowledge-assistant")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    mock_auth_enabled: bool = os.getenv("MOCK_AUTH_ENABLED", "true").lower() == "true"

    # Database
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'office_knowledge.db'}")

    # LLM & Embeddings
    llm_provider: str = os.getenv("LLM_PROVIDER", "built-in")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "built-in")

    # Web Search
    web_search_enabled: bool = os.getenv("WEB_SEARCH_ENABLED", "true").lower() == "true"
    web_search_provider: str = os.getenv("WEB_SEARCH_PROVIDER", "mock_or_official")
    serper_api_key: str = os.getenv("SERPER_API_KEY", "")
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")

    # Dataset Governance
    accept_dataset_licenses: bool = os.getenv("ACCEPT_DATASET_LICENSES", "false").lower() == "true"
    enable_voice_datasets: bool = os.getenv("ENABLE_VOICE_DATASETS", "false").lower() == "true"
    dataset_storage_path: Path = BASE_DIR / "data" / "public"
    private_docs_storage_path: Path = BASE_DIR / "data" / "private"
    configs_path: Path = BASE_DIR / "configs"

    # Preferences & Defaults
    default_reply_language: str = os.getenv("DEFAULT_REPLY_LANGUAGE", "auto")
    default_answer_depth: str = os.getenv("DEFAULT_ANSWER_DEPTH", "standard")
    max_memory_items_per_user: int = int(os.getenv("MAX_MEMORY_ITEMS_PER_USER", "50"))
    short_term_memory_turns: int = int(os.getenv("SHORT_TERM_MEMORY_TURNS", "10"))

settings = Settings()
