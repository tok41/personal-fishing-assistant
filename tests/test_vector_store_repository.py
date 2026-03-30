from __future__ import annotations

from datetime import UTC, date, datetime, timezone

import pytest

from app.models.domain import Document
from app.repositories.vector_store_repository import VectorStoreRepository


def make_document(doc_id: str, doc_date: date | None = None) -> Document:
    return Document(
        id=doc_id,
        filename=f"{doc_id}.md",
        content=f"{doc_id}の釣果メモ",
        date=doc_date,
        location="日立港",
        created_at=datetime.now(UTC),
    )


def make_embedding(value: float, dim: int = 4) -> list[float]:
    return [value] * dim


# ---------------------------------------------------------------------------
# replace_documents + save + load のラウンドトリップ
# ---------------------------------------------------------------------------

def test_save_and_load_roundtrip(tmp_path) -> None:
    repo = VectorStoreRepository(tmp_path)
    doc = make_document("2026-02-15_日立港", doc_date=date(2026, 2, 15))
    repo.replace_documents([doc], [make_embedding(0.1)])
    repo.save()

    repo2 = VectorStoreRepository(tmp_path)
    assert repo2.has_index() is False
    repo2.load()

    assert repo2.has_index() is True
    results = repo2.search(make_embedding(0.1), k=1)
    assert len(results) == 1
    assert results[0].document.id == "2026-02-15_日立港"
    assert results[0].document.date == date(2026, 2, 15)
    assert results[0].document.location == "日立港"


def test_save_and_load_roundtrip_with_date_none(tmp_path) -> None:
    repo = VectorStoreRepository(tmp_path)
    doc = make_document("noddate_日立港", doc_date=None)
    repo.replace_documents([doc], [make_embedding(0.5)])
    repo.save()

    repo2 = VectorStoreRepository(tmp_path)
    repo2.load()

    results = repo2.search(make_embedding(0.5), k=1)
    assert results[0].document.date is None


def test_save_and_load_preserves_created_at_timezone(tmp_path) -> None:
    repo = VectorStoreRepository(tmp_path)
    original_dt = datetime(2026, 3, 1, 12, 0, 0, tzinfo=UTC)
    doc = Document(
        id="2026-03-01_那珂湊",
        filename="2026-03-01_那珂湊.md",
        content="メモ",
        date=date(2026, 3, 1),
        location="那珂湊",
        created_at=original_dt,
    )
    repo.replace_documents([doc], [make_embedding(0.3)])
    repo.save()

    repo2 = VectorStoreRepository(tmp_path)
    repo2.load()

    restored = repo2.search(make_embedding(0.3), k=1)[0].document
    assert restored.created_at == original_dt


# ---------------------------------------------------------------------------
# search の距離・順序
# ---------------------------------------------------------------------------

def test_search_returns_closest_document_first(tmp_path) -> None:
    repo = VectorStoreRepository(tmp_path)
    doc_near = make_document("2026-01-01_近い")
    doc_far = make_document("2026-01-02_遠い")
    repo.replace_documents(
        [doc_near, doc_far],
        [make_embedding(1.0), make_embedding(0.0)],
    )

    results = repo.search(make_embedding(1.0), k=2)

    assert results[0].document.id == "2026-01-01_近い"
    assert results[0].distance < results[1].distance


def test_search_respects_top_k(tmp_path) -> None:
    repo = VectorStoreRepository(tmp_path)
    docs = [make_document(f"doc_{i}") for i in range(5)]
    embeddings = [make_embedding(float(i)) for i in range(5)]
    repo.replace_documents(docs, embeddings)

    results = repo.search(make_embedding(0.0), k=2)

    assert len(results) == 2


def test_search_returns_empty_when_not_loaded(tmp_path) -> None:
    repo = VectorStoreRepository(tmp_path)

    results = repo.search(make_embedding(0.1), k=5)

    assert results == []


# ---------------------------------------------------------------------------
# load — 永続化ファイルが存在しない場合
# ---------------------------------------------------------------------------

def test_load_when_files_do_not_exist_leaves_no_index(tmp_path) -> None:
    repo = VectorStoreRepository(tmp_path)
    repo.load()

    assert repo.has_index() is False


# ---------------------------------------------------------------------------
# replace_documents のバリデーション
# ---------------------------------------------------------------------------

def test_replace_documents_raises_for_empty_documents(tmp_path) -> None:
    repo = VectorStoreRepository(tmp_path)

    with pytest.raises(ValueError, match="empty"):
        repo.replace_documents([], [])


def test_replace_documents_raises_for_mismatched_lengths(tmp_path) -> None:
    repo = VectorStoreRepository(tmp_path)
    doc = make_document("2026-01-01_日立港")

    with pytest.raises(ValueError, match="same length"):
        repo.replace_documents([doc], [make_embedding(0.1), make_embedding(0.2)])
