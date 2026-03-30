from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

from app.config.settings import Settings
from app.core.ai_client import AIClient, AIClientTimeoutError
from app.models.domain import Document


class FakeEmbeddingsAPI:
    def create(self, *, model, input):
        return SimpleNamespace(data=[SimpleNamespace(embedding=[0.1, 0.2]) for _ in input])


class FakeResponsesAPI:
    def __init__(self):
        self.last_request = None

    def create(self, *, model, input, timeout):
        self.last_request = {"model": model, "input": input, "timeout": timeout}
        return SimpleNamespace(output_text="回答です")


class FakeTimeoutError(Exception):
    pass


class TimeoutResponsesAPI:
    def create(self, *, model, input, timeout):
        raise FakeTimeoutError("timed out")


class TimeoutOpenAIClient:
    def __init__(self):
        self.embeddings = FakeEmbeddingsAPI()
        self.responses = TimeoutResponsesAPI()


class FakeOpenAIClient:
    def __init__(self):
        self.embeddings = FakeEmbeddingsAPI()
        self.responses = FakeResponsesAPI()


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


def test_generate_response_includes_record_context(tmp_path) -> None:
    settings = build_settings(str(tmp_path))
    fake_client = FakeOpenAIClient()
    ai_client = AIClient(settings, client=fake_client)
    document = Document(
        id="2026-02-15_日立港",
        filename="2026-02-15_日立港.md",
        content="風が強く、サビキは重めが安定した。",
        date=None,
        location="日立港",
        created_at=datetime.now(UTC),
    )

    response = ai_client.generate_response("次回の注意点は？", [document])

    assert response.message == "回答です"
    assert response.has_records is True
    sent = fake_client.responses.last_request["input"][1]["content"]
    assert "2026-02-15_日立港.md" in sent
    assert "次回の注意点は？" in sent


def test_generate_response_without_records_requests_fallback(tmp_path) -> None:
    settings = build_settings(str(tmp_path))
    fake_client = FakeOpenAIClient()
    ai_client = AIClient(settings, client=fake_client)

    response = ai_client.generate_response("一般的な仕掛けは？", [])

    assert response.has_records is False
    sent = fake_client.responses.last_request["input"][1]["content"]
    assert "関連する釣行記録は見つかりませんでした" in sent


def test_generate_response_converts_openai_timeout_to_application_timeout(tmp_path, monkeypatch) -> None:
    settings = build_settings(str(tmp_path))
    ai_client = AIClient(settings, client=TimeoutOpenAIClient())
    monkeypatch.setattr("app.core.ai_client.OPENAI_TIMEOUT_EXCEPTIONS", (FakeTimeoutError,))

    try:
        ai_client.generate_response("次回の注意点は？", [])
    except AIClientTimeoutError as exc:
        assert "30 seconds" in str(exc)
    else:
        raise AssertionError("AIClientTimeoutError was not raised")
