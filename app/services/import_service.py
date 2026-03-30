from __future__ import annotations

from app.core.ai_client import AIClient
from app.core.document_parser import DocumentParser
from app.models.domain import ImportErrorDetail, ImportResult
from app.repositories.document_repository import DocumentRepository
from app.repositories.vector_store_repository import VectorStoreRepository
from app.utils.logger import get_logger


class ImportService:
    def __init__(
        self,
        document_repository: DocumentRepository,
        document_parser: DocumentParser,
        vector_store_repository: VectorStoreRepository,
        ai_client: AIClient,
    ):
        self._document_repository = document_repository
        self._document_parser = document_parser
        self._vector_store_repository = vector_store_repository
        self._ai_client = ai_client
        self._logger = get_logger(__name__)

    def import_documents(self) -> ImportResult:
        files = self._document_repository.list_markdown_files()
        if not files:
            self._vector_store_repository.clear()
            return ImportResult(
                imported_count=0,
                skipped_count=0,
                total_files=0,
                message="0件です。data/records/ に対象の Markdown ファイルがありません。",
            )

        parsed_documents = []
        errors: list[ImportErrorDetail] = []
        warnings = []

        for path in files:
            try:
                parsed = self._document_parser.parse_file(path)
            except Exception as exc:
                self._logger.exception("Failed to parse %s", path.name)
                errors.append(ImportErrorDetail(filename=path.name, reason=str(exc)))
                continue

            try:
                embedding = self._ai_client.embed_texts([parsed.document.content])[0]
            except Exception as exc:
                self._logger.exception("Failed to embed %s", path.name)
                errors.append(ImportErrorDetail(filename=path.name, reason=str(exc)))
                continue

            parsed_documents.append((parsed.document, embedding))
            if parsed.warning is not None:
                warnings.append(parsed.warning)
                self._logger.warning("%s: %s", parsed.warning.filename, parsed.warning.reason)

        if not parsed_documents:
            self._vector_store_repository.clear()
            return ImportResult(
                imported_count=0,
                skipped_count=len(errors),
                total_files=len(files),
                message="インポート可能なファイルがありませんでした。",
                errors=errors,
                warnings=warnings,
            )

        documents = [item[0] for item in parsed_documents]
        embeddings = [item[1] for item in parsed_documents]
        self._vector_store_repository.replace_documents(documents, embeddings)
        self._vector_store_repository.save()

        return ImportResult(
            imported_count=len(documents),
            skipped_count=len(errors),
            total_files=len(files),
            message=f"{len(documents)}件インポート完了（{len(errors)}件スキップ）",
            errors=errors,
            warnings=warnings,
        )
