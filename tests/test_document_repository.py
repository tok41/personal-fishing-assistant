from __future__ import annotations

from app.repositories.document_repository import DocumentRepository


def test_list_markdown_files_returns_only_md_files(tmp_path) -> None:
    (tmp_path / "2026-01-01_A.md").write_text("本文", encoding="utf-8")
    (tmp_path / "2026-01-02_B.md").write_text("本文", encoding="utf-8")
    (tmp_path / "note.txt").write_text("テキスト", encoding="utf-8")

    files = DocumentRepository(tmp_path).list_markdown_files()

    assert len(files) == 2
    assert all(f.suffix == ".md" for f in files)


def test_list_markdown_files_excludes_directories(tmp_path) -> None:
    (tmp_path / "subdir.md").mkdir()
    (tmp_path / "2026-01-01_A.md").write_text("本文", encoding="utf-8")

    files = DocumentRepository(tmp_path).list_markdown_files()

    assert len(files) == 1
    assert files[0].name == "2026-01-01_A.md"


def test_list_markdown_files_returns_sorted_order(tmp_path) -> None:
    (tmp_path / "2026-03-01_C.md").write_text("本文", encoding="utf-8")
    (tmp_path / "2026-01-01_A.md").write_text("本文", encoding="utf-8")
    (tmp_path / "2026-02-01_B.md").write_text("本文", encoding="utf-8")

    files = DocumentRepository(tmp_path).list_markdown_files()

    names = [f.name for f in files]
    assert names == sorted(names)


def test_list_markdown_files_returns_empty_for_empty_directory(tmp_path) -> None:
    files = DocumentRepository(tmp_path).list_markdown_files()

    assert files == []
