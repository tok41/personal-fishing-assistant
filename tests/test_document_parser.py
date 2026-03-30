from __future__ import annotations

from pathlib import Path

import pytest

from app.config.settings import Settings
from app.core.document_parser import DocumentParser


def build_settings(root: Path, max_chars: int = 3000) -> Settings:
    return Settings(
        openai_api_key="test-key",
        chat_model="gpt-5-mini",
        embedding_model="text-embedding-3-small",
        openai_timeout_seconds=30,
        search_top_k=5,
        records_dir=root / "records",
        vector_store_dir=root / "vector_store",
        logs_dir=root / "logs",
        max_document_chars_before_warning=max_chars,
    )


def test_parse_valid_file_returns_correct_document(tmp_path) -> None:
    settings = build_settings(tmp_path)
    path = tmp_path / "2026-02-15_日立港.md"
    path.write_text("風が強く、重めのオモリが有効だった。", encoding="utf-8")

    result = DocumentParser(settings).parse_file(path)

    assert result.document.id == "2026-02-15_日立港"
    assert result.document.filename == "2026-02-15_日立港.md"
    assert result.document.date.isoformat() == "2026-02-15"
    assert result.document.location == "日立港"
    assert "重めのオモリ" in result.document.content
    assert result.warning is None


def test_parse_empty_file_raises_value_error(tmp_path) -> None:
    settings = build_settings(tmp_path)
    path = tmp_path / "2026-02-15_日立港.md"
    path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        DocumentParser(settings).parse_file(path)


def test_parse_large_file_attaches_warning(tmp_path) -> None:
    settings = build_settings(tmp_path, max_chars=10)
    path = tmp_path / "2026-03-01_那珂湊.md"
    path.write_text("あ" * 11, encoding="utf-8")

    result = DocumentParser(settings).parse_file(path)

    assert result.warning is not None
    assert result.warning.filename == "2026-03-01_那珂湊.md"


def test_parse_file_exactly_at_limit_has_no_warning(tmp_path) -> None:
    settings = build_settings(tmp_path, max_chars=10)
    path = tmp_path / "2026-03-01_那珂湊.md"
    path.write_text("あ" * 10, encoding="utf-8")

    result = DocumentParser(settings).parse_file(path)

    assert result.warning is None


def test_parse_invalid_filename_raises_value_error(tmp_path) -> None:
    settings = build_settings(tmp_path)
    path = tmp_path / "invalid_name.md"
    path.write_text("本文", encoding="utf-8")

    with pytest.raises(ValueError):
        DocumentParser(settings).parse_file(path)
