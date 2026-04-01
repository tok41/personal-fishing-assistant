from __future__ import annotations

from typing import Any

from app.config.settings import Settings
from app.models.domain import ChatResponse, Document
from app.utils.logger import get_logger

try:
    from openai import APITimeoutError, OpenAI
except ImportError:  # pragma: no cover - optional dependency
    APITimeoutError = None
    OpenAI = None


OPENAI_TIMEOUT_EXCEPTIONS: tuple[type[BaseException], ...] = (
    (APITimeoutError,) if APITimeoutError is not None else ()
)


class AIClientTimeoutError(TimeoutError):
    """Raised when an OpenAI request exceeds the configured timeout."""


class AIClient:
    def __init__(self, app_settings: Settings, client: Any | None = None):
        self._settings = app_settings
        self._client = client
        self._logger = get_logger(__name__)

    def has_api_key(self) -> bool:
        return bool(self._settings.openai_api_key)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        client = self._get_client()
        response = client.embeddings.create(
            model=self._settings.embedding_model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    def generate_response(self, query: str, documents: list[Document]) -> ChatResponse:
        client = self._get_client()
        messages = self._build_messages(query, documents)
        self._logger.info(
            "Calling OpenAI Responses API model=%s records=%d",
            self._settings.chat_model,
            len(documents),
        )
        self._logger.debug(
            "Prompt lengths system=%d user=%d",
            len(messages[0]["content"]),
            len(messages[1]["content"]),
        )
        try:
            response = client.responses.create(
                model=self._settings.chat_model,
                input=messages,
                timeout=self._settings.openai_timeout_seconds,
            )
        except OPENAI_TIMEOUT_EXCEPTIONS as exc:
            raise AIClientTimeoutError(
                f"OpenAI API request timed out after {self._settings.openai_timeout_seconds} seconds."
            ) from exc
        self._logger.info("OpenAI Responses API call completed successfully.")
        message = self._extract_text(response)
        return ChatResponse(
            message=message,
            has_records=bool(documents),
            record_count=len(documents),
        )

    def _get_client(self) -> Any:
        if not self.has_api_key():
            raise RuntimeError("OpenAI API key is not set.")
        if self._client is not None:
            return self._client
        if OpenAI is None:
            raise RuntimeError("openai package is not installed.")
        self._client = OpenAI(
            api_key=self._settings.openai_api_key,
            timeout=self._settings.openai_timeout_seconds,
        )
        return self._client

    @staticmethod
    def _extract_text(response: Any) -> str:
        if hasattr(response, "output_text") and response.output_text:
            return response.output_text
        raise RuntimeError("OpenAI response did not contain output_text")

    def _build_messages(self, query: str, documents: list[Document]) -> list[dict[str, str]]:
        system_prompt = (
            "You are a fishing assistant. Answer in Japanese. "
            "Use retrieved fishing records when they are available. "
            "If no records are available, say that no related records were found "
            "and then answer with general fishing knowledge."
        )

        if documents:
            records_text = "\n\n".join(
                f"[{document.filename}]\n{document.content}" for document in documents
            )
            user_prompt = (
                "以下の釣行記録を参考にして質問へ回答してください。\n\n"
                f"{records_text}\n\n"
                f"質問: {query}"
            )
        else:
            user_prompt = (
                "関連する釣行記録は見つかりませんでした。"
                "一般的な知識に基づいて回答してください。\n\n"
                f"質問: {query}"
            )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
