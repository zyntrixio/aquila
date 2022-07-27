from logging import NOTSET
from logging.config import dictConfig
from sys import argv, stderr, stdout

import sentry_sdk

from decouple import Choices, config
from sentry_sdk.integrations.flask import FlaskIntegration

ALLOWED_LOG_LEVELS = Choices(["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"])

PROJECT_NAME: str = config("PROJECT_NAME", default="aquila")
PROJECT_PORT: int = config("PROJECT_PORT", default=5000, cast=int)
DEBUG: bool = config("DEBUG", default=False, cast=bool)
ROOT_LOG_LEVEL: str = config("ROOT_LOG_LEVEL", default="ERROR", cast=ALLOWED_LOG_LEVELS)
LOG_FORMATTER: str = config("LOG_FORMATTER", default="json", cast=Choices(["brief", "json"]))
TESTING: bool = config("TESTING", default=True, cast=bool)

POLARIS_HOST: str = config("POLARIS_HOST", default="http://polaris-api")
POLARIS_PREFIX: str = config("POLARIS_PREFIX", default="/loyalty")
POLARIS_BASE_URL = POLARIS_HOST + POLARIS_PREFIX


BLOB_STORAGE_DSN: str = config("BLOB_STORAGE_DSN")
BLOB_CONTAINER: str = config("BLOB_CONTAINER", default="aquila-templates")
BLOB_LOGGING_LEVEL: str = config("BLOB_LOGGING_LEVEL", default="ERROR", cast=ALLOWED_LOG_LEVELS)

SENTRY_DSN: str | None = config("SENTRY_DSN", default=None)
if SENTRY_DSN:  # pragma: no cover
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            FlaskIntegration(),
        ],
    )


dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "brief": {"format": "%(levelname)s:     %(asctime)s - %(message)s"},
            "json": {"()": "aquila.reporting.JSONFormatter"},
        },
        "handlers": {
            "stderr": {
                "level": NOTSET,
                "class": "logging.StreamHandler",
                "stream": stderr,
                "formatter": LOG_FORMATTER,
            },
            "stdout": {
                "level": NOTSET,
                "class": "logging.StreamHandler",
                "stream": stdout,
                "formatter": LOG_FORMATTER,
            },
        },
        "loggers": {
            "root": {
                "level": ROOT_LOG_LEVEL,
                "handlers": ["stdout"],
            },
            "template-loader": {
                "level": BLOB_LOGGING_LEVEL,
                "handlers": ["stdout"],
                "propagate": False,
            },
        },
    }
)


command = argv[0]
args = argv[1:] if len(argv) > 1 else []

if "pytest" in command or any("test" in arg for arg in args):
    TESTING = True
