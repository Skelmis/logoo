from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Literal, Any

from logoo.data import data_queue

LevelT = (
    Literal[50, 40, 30, 20, 10, 0]
    | Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]
    | int  # We do this catch all for logging.XXX to work :(
)


class Logger:
    def __init__(self, name: str, extra_metadata: dict[Any, Any] | None = None):
        self.name: str = name
        self.extra_metadata: dict[Any, Any] | None = extra_metadata

    def debug(self, message, *args, extra_metadata: dict[Any, Any] | None = None):
        self.log(message, logging.DEBUG, *args, extra_metadata=extra_metadata)

    def info(self, message, *args, extra_metadata: dict[Any, Any] | None = None):
        self.log(message, logging.INFO, *args, extra_metadata=extra_metadata)

    def warning(self, message, *args, extra_metadata: dict[Any, Any] | None = None):
        self.log(message, logging.WARNING, *args, extra_metadata=extra_metadata)

    def error(self, message, *args, extra_metadata: dict[Any, Any] | None = None):
        self.log(message, logging.ERROR, *args, extra_metadata=extra_metadata)

    def critical(self, message, *args, extra_metadata: dict[Any, Any] | None = None):
        self.log(message, logging.CRITICAL, *args, extra_metadata=extra_metadata)

    def log(
        self,
        message: str,
        level: LevelT,
        *args,
        extra_metadata: dict[Any, Any] | None = None,
    ):
        # We always want to log as strings for readability in open observe
        level = logging.getLevelName(level) if isinstance(level, int) else level
        created_at = datetime.now(timezone.utc)

        # Means it's a drop in replacement for logging
        message = message % args

        log = {
            "level": level,
            "message": message,
            "source": self.name,
            "_timestamp.timezone": "UTC",
            # We do this twice as OpenObserve will convert
            # _timestamp to microseconds within their UI
            "_timestamp": created_at.isoformat(),
            "_timestamp.iso_format": created_at.isoformat(),
        }
        if self.extra_metadata is not None:
            log = {**log, **self.extra_metadata}
        if extra_metadata is not None:
            log = {**log, **extra_metadata}

        data_queue.put_nowait(log)
