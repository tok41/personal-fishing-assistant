from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

from app.models.domain import Document, SearchResult

try:
    import faiss
except ImportError:  # pragma: no cover - optional dependency
    faiss = None


class VectorStoreRepository:
    def __init__(self, vector_store_dir: Path):
        self._vector_store_dir = vector_store_dir
        self._index_path = vector_store_dir / "index.faiss"
        self._metadata_path = vector_store_dir / "metadata.json"
        self._index = None
        self._documents: list[Document] = []

    def replace_documents(self, documents: list[Document], embeddings: list[list[float]]) -> None:
        self._ensure_faiss()
        if not documents:
            raise ValueError("documents must not be empty")
        if len(documents) != len(embeddings):
            raise ValueError("documents and embeddings must have the same length")

        matrix = self._to_matrix(embeddings)
        self._index = faiss.IndexFlatL2(matrix.shape[1])
        self._index.add(matrix)
        self._documents = list(documents)

    def clear(self) -> None:
        self._index = None
        self._documents = []
        if self._index_path.exists():
            self._index_path.unlink()
        if self._metadata_path.exists():
            self._metadata_path.unlink()

    def search(self, query_embedding: list[float], k: int) -> list[SearchResult]:
        if not self.has_index():
            return []

        try:
            import numpy as np
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("numpy is not installed. Please install numpy.") from exc

        query = np.asarray([query_embedding], dtype="float32")
        distances, indices = self._index.search(query, min(k, len(self._documents)))

        results: list[SearchResult] = []
        for distance, index in zip(distances[0], indices[0], strict=False):
            if index < 0:
                continue
            results.append(
                SearchResult(
                    document=self._documents[index],
                    distance=float(distance),
                )
            )
        return results

    def has_index(self) -> bool:
        return self._index is not None and bool(self._documents)

    def save(self) -> None:
        self._ensure_faiss()
        if self._index is None:
            return

        self._vector_store_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(self._index_path))
        payload = [self._serialize_document(document) for document in self._documents]
        self._metadata_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load(self) -> None:
        self._ensure_faiss()
        if not self._index_path.exists() or not self._metadata_path.exists():
            self._index = None
            self._documents = []
            return

        self._index = faiss.read_index(str(self._index_path))
        raw_documents = json.loads(self._metadata_path.read_text(encoding="utf-8"))
        self._documents = [self._deserialize_document(item) for item in raw_documents]

    def _ensure_faiss(self) -> None:
        if faiss is None:
            raise RuntimeError("faiss is not installed. Please install faiss-cpu.")

    @staticmethod
    def _to_matrix(embeddings: list[list[float]]):
        try:
            import numpy as np
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("numpy is not installed. Please install numpy.") from exc

        matrix = np.asarray(embeddings, dtype="float32")
        if matrix.ndim != 2 or matrix.shape[0] == 0:
            raise ValueError("embeddings must be a non-empty 2D array")
        return matrix

    @staticmethod
    def _serialize_document(document: Document) -> dict[str, Any]:
        return {
            "id": document.id,
            "filename": document.filename,
            "content": document.content,
            "date": document.date.isoformat() if document.date else None,
            "location": document.location,
            "created_at": document.created_at.isoformat(),
        }

    @staticmethod
    def _deserialize_document(payload: dict[str, Any]) -> Document:
        parsed_date = date.fromisoformat(payload["date"]) if payload["date"] else None
        created_at = datetime.fromisoformat(payload["created_at"])
        return Document(
            id=payload["id"],
            filename=payload["filename"],
            content=payload["content"],
            date=parsed_date,
            location=payload["location"],
            created_at=created_at,
        )
