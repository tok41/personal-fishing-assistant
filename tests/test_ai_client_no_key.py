from __future__ import annotations

from pathlib import Path

import pytest

from app.config.settings import Settings
from app.core.ai_client import AIClient


def build_settings_no_key(root: Path) -> Settings:
    return Settings(
        openai_api_key="",
        chat_model="gpt-5-mini",
        embedding_model="text-embedding-3-small",
        openai_timeout_seconds=30,
        search_top_k=5,
        log_level="INFO",
        records_dir=root / "records",
        vector_store_dir=root / "vector_store",
        logs_dir=root / "logs",
        max_document_chars_before_warning=3000,
    )


def test_embed_texts_raises_when_api_key_is_empty(tmp_path) -> None:
    settings = build_settings_no_key(tmp_path)
    client = AIClient(settings)

    with pytest.raises(RuntimeError, match="API key"):
        client.embed_texts(["テスト"])


def test_generate_response_raises_when_api_key_is_empty(tmp_path) -> None:
    settings = build_settings_no_key(tmp_path)
    client = AIClient(settings)

    with pytest.raises(RuntimeError, match="API key"):
        client.generate_response("質問", [])


def test_has_api_key_returns_false_when_empty(tmp_path) -> None:
    settings = build_settings_no_key(tmp_path)
    client = AIClient(settings)

    assert client.has_api_key() is False
