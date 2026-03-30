from __future__ import annotations

from pathlib import Path

from app.config.settings import Settings
from app.core.ai_client import AIClient
from app.core.document_parser import DocumentParser
from app.repositories.document_repository import DocumentRepository
from app.services.import_service import ImportService


class FakeAIClient(AIClient):
    def __init__(self, settings: Settings):
        super().__init__(settings, client=object())

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(texts[0])), 1.0] for _ in texts]


class FakeVectorStoreRepository:
    def __init__(self):
        self.documents = None
        self.embeddings = None
        self.saved = False
        self.cleared = False

    def replace_documents(self, documents, embeddings):
        self.documents = documents
        self.embeddings = embeddings

    def save(self):
        self.saved = True

    def clear(self):
        self.cleared = True


def build_settings(root: Path) -> Settings:
    return Settings(
        openai_api_key="test-key",
        chat_model="gpt-5-mini",
        embedding_model="text-embedding-3-small",
        openai_timeout_seconds=30,
        search_top_k=5,
        records_dir=root / "records",
        vector_store_dir=root / "vector_store",
        logs_dir=root / "logs",
        max_document_chars_before_warning=10,
    )


def test_import_documents_skips_invalid_files_and_saves_valid_ones(tmp_path) -> None:
    settings = build_settings(tmp_path)
    settings.records_dir.mkdir(parents=True)
    settings.logs_dir.mkdir(parents=True)
    (settings.records_dir / "2026-03-01_日立港.md").write_text(
        "かなり長い本文です。" * 4,
        encoding="utf-8",
    )
    (settings.records_dir / "invalid_name.md").write_text(
        "本文",
        encoding="utf-8",
    )

    vector_store_repository = FakeVectorStoreRepository()
    service = ImportService(
        document_repository=DocumentRepository(settings.records_dir),
        document_parser=DocumentParser(settings),
        vector_store_repository=vector_store_repository,
        ai_client=FakeAIClient(settings),
    )

    result = service.import_documents()

    assert result.imported_count == 1
    assert result.skipped_count == 1
    assert result.total_files == 2
    assert len(result.warnings) == 1
    assert "1件インポート完了" in result.message
    assert vector_store_repository.saved is True


def test_import_documents_returns_zero_when_directory_is_empty(tmp_path) -> None:
    settings = build_settings(tmp_path)
    settings.records_dir.mkdir(parents=True)
    settings.logs_dir.mkdir(parents=True)

    vector_store_repository = FakeVectorStoreRepository()
    service = ImportService(
        document_repository=DocumentRepository(settings.records_dir),
        document_parser=DocumentParser(settings),
        vector_store_repository=vector_store_repository,
        ai_client=FakeAIClient(settings),
    )

    result = service.import_documents()

    assert result.imported_count == 0
    assert result.total_files == 0
    assert "0件" in result.message
    assert vector_store_repository.cleared is True
