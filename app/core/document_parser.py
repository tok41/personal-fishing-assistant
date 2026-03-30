from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from app.config.settings import Settings
from app.models.domain import Document, ImportWarningDetail
from app.utils.validators import parse_record_filename


@dataclass(slots=True)
class ParsedDocument:
    document: Document
    warning: ImportWarningDetail | None = None


class DocumentParser:
    def __init__(self, app_settings: Settings):
        self._settings = app_settings

    def parse_file(self, path: Path) -> ParsedDocument:
        parsed_date, location = parse_record_filename(path.name)
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            raise ValueError("Markdown file is empty")

        warning = None
        if len(content) > self._settings.max_document_chars_before_warning:
            warning = ImportWarningDetail(
                filename=path.name,
                reason=(
                    f"Document exceeds {self._settings.max_document_chars_before_warning} "
                    "characters; imported as a single vector"
                ),
            )

        document = Document(
            id=path.stem,
            filename=path.name,
            content=content,
            date=parsed_date,
            location=location,
            created_at=datetime.now(UTC),
        )
        return ParsedDocument(document=document, warning=warning)
