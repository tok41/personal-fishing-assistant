from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass(slots=True)
class Document:
    id: str
    filename: str
    content: str
    date: date | None
    location: str | None
    created_at: datetime


@dataclass(slots=True)
class SearchResult:
    document: Document
    distance: float


@dataclass(slots=True)
class ChatMessage:
    role: str
    content: str


@dataclass(slots=True)
class ChatResponse:
    message: str
    has_records: bool
    record_count: int


@dataclass(slots=True)
class ImportErrorDetail:
    filename: str
    reason: str


@dataclass(slots=True)
class ImportWarningDetail:
    filename: str
    reason: str


@dataclass(slots=True)
class ImportResult:
    imported_count: int
    skipped_count: int
    total_files: int
    message: str
    errors: list[ImportErrorDetail] = field(default_factory=list)
    warnings: list[ImportWarningDetail] = field(default_factory=list)
