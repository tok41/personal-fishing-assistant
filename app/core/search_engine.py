from __future__ import annotations

from app.core.ai_client import AIClient
from app.models.domain import SearchResult
from app.repositories.vector_store_repository import VectorStoreRepository


class SearchEngine:
    def __init__(
        self,
        vector_store_repository: VectorStoreRepository,
        ai_client: AIClient,
        *,
        top_k: int,
    ):
        self._vector_store_repository = vector_store_repository
        self._ai_client = ai_client
        self._top_k = top_k

    def search(self, query: str) -> list[SearchResult]:
        if not query.strip():
            return []

        if not self._vector_store_repository.has_index():
            self._vector_store_repository.load()

        if not self._vector_store_repository.has_index():
            return []

        query_embedding = self._ai_client.embed_texts([query])[0]
        return self._vector_store_repository.search(query_embedding, self._top_k)
