from __future__ import annotations

from app.core.ai_client import AIClient
from app.core.search_engine import SearchEngine
from app.models.domain import ChatResponse
from app.utils.logger import get_logger


class ChatService:
    def __init__(self, search_engine: SearchEngine, ai_client: AIClient):
        self._search_engine = search_engine
        self._ai_client = ai_client
        self._logger = get_logger(__name__)

    def process_message(self, query: str) -> ChatResponse:
        results = self._search_engine.search(query)
        filenames = [result.document.filename for result in results]
        self._logger.info(
            "Search completed for query=%r hits=%d filenames=%s",
            query,
            len(results),
            filenames,
        )
        self._logger.debug(
            "Search distance scores=%s",
            [(result.document.filename, result.distance) for result in results],
        )
        documents = [result.document for result in results]
        return self._ai_client.generate_response(query, documents)
