from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

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


def make_document(doc_id: str) -> Document:
    return Document(
        id=doc_id,
        filename=f"{doc_id}.md",
        content="釣果メモ",
        date=None,
        location="日立港",
        created_at=datetime.now(UTC),
    )


def test_process_message_passes_search_results_to_ai_client() -> None:
    document = make_document("2026-02-15_日立港")
    search_results = [SearchResult(document=document, distance=0.1)]
    expected_response = ChatResponse(message="回答です", has_records=True, record_count=1)

    fake_search = FakeSearchEngine(search_results)
    fake_ai = FakeAIClient(expected_response)
    service = ChatService(search_engine=fake_search, ai_client=fake_ai)

    response = service.process_message("次回の注意点は？")

    assert response.message == "回答です"
    assert response.has_records is True
    assert fake_ai.last_query == "次回の注意点は？"
    assert fake_ai.last_documents == [document]


def test_process_message_passes_empty_documents_when_no_search_results() -> None:
    expected_response = ChatResponse(message="一般知識での回答", has_records=False, record_count=0)

    fake_search = FakeSearchEngine([])
    fake_ai = FakeAIClient(expected_response)
    service = ChatService(search_engine=fake_search, ai_client=fake_ai)

    response = service.process_message("仕掛けを教えて")

    assert response.has_records is False
    assert fake_ai.last_documents == []


def test_process_message_passes_query_to_search_engine() -> None:
    class RecordingSearchEngine:
        def __init__(self):
            self.received_query: str | None = None

        def search(self, query: str) -> list[SearchResult]:
            self.received_query = query
            return []

    recording_search = RecordingSearchEngine()
    fake_ai = FakeAIClient(ChatResponse(message="", has_records=False, record_count=0))
    service = ChatService(search_engine=recording_search, ai_client=fake_ai)

    service.process_message("日立港の情報は？")

    assert recording_search.received_query == "日立港の情報は？"
