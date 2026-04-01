from __future__ import annotations

import logging
from pathlib import Path

from app.config.settings import settings


def get_logger(name: str, *, log_file: Path | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(_resolve_log_level(settings.log_level))
    if logger.handlers:
        return logger

    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(log_file or settings.logs_dir / "app.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def _resolve_log_level(log_level: str) -> int:
    resolved_level = getattr(logging, log_level.upper(), None)
    if isinstance(resolved_level, int):
        return resolved_level
    return logging.INFO
