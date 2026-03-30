from __future__ import annotations

from app.core.ai_client import AIClient
from app.core.search_engine import SearchEngine
from app.models.domain import ChatResponse


class ChatService:
    def __init__(self, search_engine: SearchEngine, ai_client: AIClient):
        self._search_engine = search_engine
        self._ai_client = ai_client

    def process_message(self, query: str) -> ChatResponse:
        results = self._search_engine.search(query)
        documents = [result.document for result in results]
        return self._ai_client.generate_response(query, documents)
