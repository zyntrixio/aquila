import json
import logging


class JSONFormatter(logging.Formatter):
    def __init__(self) -> None:
        pass

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        return json.dumps(
            {
                "timestamp": record.created,
                "level": record.levelno,
                "levelname": record.levelname,
                "process": record.processName,
                "thread": record.threadName,
                "file": record.pathname,
                "line": record.lineno,
                "module": record.module,
                "function": record.funcName,
                "name": record.name,
                "message": record.getMessage(),
            }
        )
