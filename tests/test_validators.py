from __future__ import annotations

import pytest

from app.utils.validators import parse_record_filename


def test_valid_filename_returns_date_and_location() -> None:
    parsed_date, location = parse_record_filename("2026-02-15_日立港.md")

    assert parsed_date.year == 2026
    assert parsed_date.month == 2
    assert parsed_date.day == 15
    assert location == "日立港"


def test_valid_filename_with_ascii_location() -> None:
    parsed_date, location = parse_record_filename("2026-01-01_Kasumigaura.md")

    assert parsed_date.isoformat() == "2026-01-01"
    assert location == "Kasumigaura"


@pytest.mark.parametrize(
    "filename",
    [
        "invalid_name.md",
        "2026-02-15.md",
        "2026-02-15_日立港.txt",
        "20260215_日立港.md",
        "2026-2-15_日立港.md",
        "",
    ],
)
def test_invalid_filename_pattern_raises_value_error(filename: str) -> None:
    with pytest.raises(ValueError, match="Filename must match"):
        parse_record_filename(filename)


def test_location_whitespace_only_raises_value_error() -> None:
    with pytest.raises(ValueError):
        parse_record_filename("2026-02-15_ .md")


def test_invalid_date_value_raises_error() -> None:
    with pytest.raises(ValueError):
        parse_record_filename("2026-13-01_日立港.md")
