from __future__ import annotations

import logging
from datetime import UTC, datetime

from app.models.domain import ChatResponse, Document, SearchResult
from app.services.chat_service import ChatService


class FakeSearchEngine:
    def __init__(self, results: list[SearchResult]):
        self._results = results

    def search(self, query: str) -> list[SearchResult]:
        return self._results


class FakeAIClient:
    def __init__(self, response: ChatResponse):
        self._response = response
        self.last_query: str | None = None
        self.last_documents: list[Document] | None = None

    def generate_response(self, query: str, documents: list[Document]) -> ChatResponse:
        self.last_query = query
        self.last_documents = documents
        return self._response


class RecordingLogger:
    def __init__(self):
        self.info_calls: list[tuple[str, tuple[object, ...]]] = []
        self.debug_calls: list[tuple[str, tuple[object, ...]]] = []

    def info(self, message: str, *args: object) -> None:
        self.info_calls.append((message, args))

    def debug(self, message: str, *args: object) -> None:
        self.debug_calls.append((message, args))

    def isEnabledFor(self, level: int) -> bool:
        return level == logging.DEBUG


def make_document(doc_id: str) -> Document:
    return Document(
        id=doc_id,
        filename=f"{doc_id}.md",
        content="釣果メモ",
        date=None,
        location="日立港",
        created_at=datetime.now(UTC),
    )


def test_process_message_passes_search_results_to_ai_client(monkeypatch) -> None:
    document = make_document("2026-02-15_日立港")
    search_results = [SearchResult(document=document, distance=0.1)]
    expected_response = ChatResponse(message="回答です", has_records=True, record_count=1)
    recording_logger = RecordingLogger()

    fake_search = FakeSearchEngine(search_results)
    fake_ai = FakeAIClient(expected_response)
    monkeypatch.setattr("app.services.chat_service.get_logger", lambda _: recording_logger)
    service = ChatService(search_engine=fake_search, ai_client=fake_ai)

    response = service.process_message("次回の注意点は？")

    assert response.message == "回答です"
    assert response.has_records is True
    assert fake_ai.last_query == "次回の注意点は？"
    assert fake_ai.last_documents == [document]
    assert recording_logger.info_calls == [
        (
            "Search completed for query=%r hits=%d filenames=%s",
            ("次回の注意点は？", 1, [document.filename]),
        )
    ]
    assert recording_logger.debug_calls == [
        ("Search distance scores=%s", ([(document.filename, 0.1)],))
    ]


def test_process_message_passes_empty_documents_when_no_search_results(monkeypatch) -> None:
    expected_response = ChatResponse(message="一般知識での回答", has_records=False, record_count=0)
    recording_logger = RecordingLogger()

    fake_search = FakeSearchEngine([])
    fake_ai = FakeAIClient(expected_response)
    monkeypatch.setattr("app.services.chat_service.get_logger", lambda _: recording_logger)
    service = ChatService(search_engine=fake_search, ai_client=fake_ai)

    response = service.process_message("仕掛けを教えて")

    assert response.has_records is False
    assert fake_ai.last_documents == []
    assert recording_logger.info_calls == [
        ("Search completed for query=%r hits=%d filenames=%s", ("仕掛けを教えて", 0, []))
    ]
    assert recording_logger.debug_calls == [("Search distance scores=%s", ([],))]


def test_process_message_passes_query_to_search_engine(monkeypatch) -> None:
    class RecordingSearchEngine:
        def __init__(self):
            self.received_query: str | None = None

        def search(self, query: str) -> list[SearchResult]:
            self.received_query = query
            return []

    recording_search = RecordingSearchEngine()
    fake_ai = FakeAIClient(ChatResponse(message="", has_records=False, record_count=0))
    monkeypatch.setattr("app.services.chat_service.get_logger", lambda _: RecordingLogger())
    service = ChatService(search_engine=recording_search, ai_client=fake_ai)

    service.process_message("日立港の情報は？")

    assert recording_search.received_query == "日立港の情報は？"
