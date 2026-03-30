from __future__ import annotations

from pathlib import Path


class DocumentRepository:
    def __init__(self, records_dir: Path):
        self._records_dir = records_dir

    def list_markdown_files(self) -> list[Path]:
        return sorted(
            path
            for path in self._records_dir.iterdir()
            if path.is_file() and path.suffix.lower() == ".md"
        )
