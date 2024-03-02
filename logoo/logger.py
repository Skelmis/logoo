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

    def debug(self, message, extra_metadata: dict[Any, Any] | None = None):
        self.log(message, logging.DEBUG, extra_metadata=extra_metadata)

    def info(self, message, extra_metadata: dict[Any, Any] | None = None):
        self.log(message, logging.INFO, extra_metadata=extra_metadata)

    def warning(self, message, extra_metadata: dict[Any, Any] | None = None):
        self.log(message, logging.WARNING, extra_metadata=extra_metadata)

    def error(self, message, extra_metadata: dict[Any, Any] | None = None):
        self.log(message, logging.ERROR, extra_metadata=extra_metadata)

    def critical(self, message, extra_metadata: dict[Any, Any] | None = None):
        self.log(message, logging.CRITICAL, extra_metadata=extra_metadata)

    def log(
        self,
        message: str,
        level: LevelT,
        *,
        extra_metadata: dict[Any, Any] | None = None
    ):
        # We always want to log as strings for readability in open observe
        level = logging.getLevelName(level) if isinstance(level, int) else level
        created_at = datetime.now(timezone.utc)

        log = {
            "level": level,
            "message": message,
            "source": self.name,
            "created_at.timezone": "UTC",
            "created_at.timestamp": created_at.timestamp(),
            "created_at.iso_format": created_at.isoformat(),
        }
        if self.extra_metadata is not None:
            log = {**log, **self.extra_metadata}
        if extra_metadata is not None:
            log = {**log, **extra_metadata}

        data_queue.put_nowait(log)
