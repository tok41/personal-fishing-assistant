from __future__ import annotations

import pytest

from app.core.ai_client import AIClientTimeoutError
from app.frontend.main import process_chat_prompt


class FakeChatService:
    def __init__(self, result=None, error: Exception | None = None):
        self._result = result
        self._error = error

    def process_message(self, prompt: str):
        if self._error is not None:
            raise self._error
        return self._result


def test_process_chat_prompt_logs_timeout(monkeypatch) -> None:
    logged = {}

    class FakeLogger:
        def warning(self, message, *args):
            logged["warning"] = message % args

        def exception(self, message, *args):
            logged["exception"] = message % args

    monkeypatch.setattr("app.frontend.main.logger", FakeLogger())

    with pytest.raises(AIClientTimeoutError):
        process_chat_prompt(FakeChatService(error=AIClientTimeoutError("timeout")), "仕掛けを教えて")

    assert "timed out" in logged["warning"]
    assert "exception" not in logged


def test_process_chat_prompt_logs_unexpected_error(monkeypatch) -> None:
    logged = {}

    class FakeLogger:
        def warning(self, message, *args):
            logged["warning"] = message % args

        def exception(self, message, *args):
            logged["exception"] = message % args

    monkeypatch.setattr("app.frontend.main.logger", FakeLogger())

    with pytest.raises(RuntimeError):
        process_chat_prompt(FakeChatService(error=RuntimeError("boom")), "日立港の傾向は？")

    assert "Chat processing failed for prompt: 日立港の傾向は？" == logged["exception"]
    assert "warning" not in logged
