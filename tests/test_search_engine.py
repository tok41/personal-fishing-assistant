from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from app.config.settings import Settings
from app.core.ai_client import AIClient
from app.core.search_engine import SearchEngine
from app.models.domain import Document, SearchResult


class FakeAIClient(AIClient):
    def __init__(self, settings: Settings):
        super().__init__(settings, client=object())

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2] for _ in texts]


class FakeVectorStoreRepository:
    def __init__(self):
        self.loaded = False
        self.results = [
            SearchResult(
                document=Document(
                    id="2026-02-15_日立港",
                    filename="2026-02-15_日立港.md",
                    content="釣果メモ",
                    date=None,
                    location="日立港",
                    created_at=datetime.now(UTC),
                ),
                distance=0.42,
            )
        ]

    def has_index(self) -> bool:
        return self.loaded

    def load(self) -> None:
        self.loaded = True

    def search(self, query_embedding, k):
        return self.results[:k]


def build_settings(tmpdir: str) -> Settings:
    root = Path(tmpdir)
    return Settings(
        openai_api_key="test-key",
        chat_model="gpt-5-mini",
        embedding_model="text-embedding-3-small",
        openai_timeout_seconds=30,
        search_top_k=5,
        records_dir=root / "records",
        vector_store_dir=root / "vector_store",
        logs_dir=root / "logs",
        max_document_chars_before_warning=3000,
    )


def test_search_loads_index_and_returns_results(tmp_path) -> None:
    settings = build_settings(str(tmp_path))
    repository = FakeVectorStoreRepository()
    engine = SearchEngine(repository, FakeAIClient(settings), top_k=5)

    results = engine.search("日立港で何を試すべき？")

    assert len(results) == 1
    assert repository.loaded is True
    assert results[0].document.location == "日立港"


def test_search_returns_empty_for_blank_query(tmp_path) -> None:
    settings = build_settings(str(tmp_path))
    repository = FakeVectorStoreRepository()
    engine = SearchEngine(repository, FakeAIClient(settings), top_k=5)

    results = engine.search("   ")

    assert results == []
    assert repository.loaded is False
