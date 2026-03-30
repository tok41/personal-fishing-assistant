from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"

if load_dotenv is not None:
    load_dotenv(ENV_PATH)


@dataclass(frozen=True, slots=True)
class Settings:
    openai_api_key: str
    chat_model: str
    embedding_model: str
    openai_timeout_seconds: int
    search_top_k: int
    records_dir: Path
    vector_store_dir: Path
    logs_dir: Path
    max_document_chars_before_warning: int


def load_settings() -> Settings:
    data_dir = PROJECT_ROOT / "data"
    settings = Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        chat_model=os.getenv("OPENAI_CHAT_MODEL", "gpt-5-mini"),
        embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        openai_timeout_seconds=int(os.getenv("OPENAI_TIMEOUT_SECONDS", "30")),
        search_top_k=int(os.getenv("SEARCH_TOP_K", "5")),
        records_dir=Path(os.getenv("RECORDS_DIR", data_dir / "records")),
        vector_store_dir=Path(os.getenv("VECTOR_STORE_DIR", data_dir / "vector_store")),
        logs_dir=Path(os.getenv("LOGS_DIR", data_dir / "logs")),
        max_document_chars_before_warning=int(
            os.getenv("MAX_DOCUMENT_CHARS_BEFORE_WARNING", "3000")
        ),
    )
    settings.records_dir.mkdir(parents=True, exist_ok=True)
    settings.vector_store_dir.mkdir(parents=True, exist_ok=True)
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    return settings


settings = load_settings()
