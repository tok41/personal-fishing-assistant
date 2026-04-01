from __future__ import annotations

import re
from datetime import date


RECORD_FILENAME_PATTERN = re.compile(r"^(?P<date>\d{4} \d{2} \d{2})_(?P<location>.+)\.md$")


def parse_record_filename(filename: str) -> tuple[date | None, str | None]:
    match = RECORD_FILENAME_PATTERN.match(filename)
    if not match:
        raise ValueError(
            "Filename must match YYYY MM DD_場所名.md"
        )

    parsed_date = date.fromisoformat(match.group("date").replace(" ", "-"))
    location = match.group("location").strip()
    if not location:
        raise ValueError("Location in filename must not be empty")

    return parsed_date, location
