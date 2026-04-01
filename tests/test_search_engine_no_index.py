from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from app.config.settings import Settings
from app.core.ai_client import AIClient
from app.core.search_engine import SearchEngine


class FakeAIClient(AIClient):
    def __init__(self, settings: Settings):
        super().__init__(settings, client=object())

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2] for _ in texts]


class FakeVectorStoreRepositoryNoIndex:
    """load() を呼んでもインデックスが存在しない状態を再現する。"""

    def __init__(self):
        self.load_called = False

    def has_index(self) -> bool:
        return False

    def load(self) -> None:
        self.load_called = True

    def search(self, query_embedding, k):
        return []


def build_settings(tmpdir: str) -> Settings:
    root = Path(tmpdir)
    return Settings(
        openai_api_key="test-key",
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


def test_search_returns_empty_when_index_not_found_after_load(tmp_path) -> None:
    settings = build_settings(str(tmp_path))
    repository = FakeVectorStoreRepositoryNoIndex()
    engine = SearchEngine(repository, FakeAIClient(settings), top_k=5)

    results = engine.search("釣れる場所は？")

    assert results == []
    assert repository.load_called is True
