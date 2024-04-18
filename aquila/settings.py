import secrets
import sys
from logging import NOTSET
from logging.config import dictConfig

import sentry_sdk
from decouple import Choices, config
from sentry_sdk.integrations.flask import FlaskIntegration


def check_testing(value: bool) -> bool:
    command = sys.argv[0]
    if command == "poetry":
        command = sys.argv[2] if len(sys.argv) > 2 else "None"

    if "test" in command:
        return True

    return value


SECRET_KEY = secrets.token_hex()
ALLOWED_LOG_LEVELS = Choices(["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"])

PROJECT_NAME: str = config("PROJECT_NAME", default="aquila")
PROJECT_PORT: int = config("PROJECT_PORT", default=5000, cast=int)
DEBUG: bool = config("DEBUG", default=False, cast=bool)
ROOT_LOG_LEVEL: str = config("ROOT_LOG_LEVEL", default="ERROR", cast=ALLOWED_LOG_LEVELS)
LOG_FORMATTER: str = config("LOG_FORMATTER", default="json", cast=Choices(["brief", "json"]))
TESTING: bool = check_testing(config("TESTING", default=False, cast=bool))

POLARIS_HOST: str = config("POLARIS_HOST", default="http://polaris-api")
POLARIS_PREFIX: str = config("POLARIS_PREFIX", default="/loyalty")
POLARIS_BASE_URL = POLARIS_HOST + POLARIS_PREFIX
COSMOS_HOST: str = config("COSMOS_HOST", default="http://cosmos-public-api")
COSMOS_PREFIX: str = config("COSMOS_PREFIX", default="/api/public")
COSMOS_BASE_URL = COSMOS_HOST + COSMOS_PREFIX


BLOB_STORAGE_DSN: str = config("BLOB_STORAGE_DSN")
BLOB_CONTAINER: str = config("BLOB_CONTAINER", default="aquila-templates")
BLOB_LOGGING_LEVEL: str = config("BLOB_LOGGING_LEVEL", default="ERROR", cast=ALLOWED_LOG_LEVELS)

METRICS_DEBUG: bool = config("METRICS_DEBUG", default=False, cast=bool)
PROMETHEUS_MULTIPROC_DIR: str | None = config("PROMETHEUS_MULTIPROC_DIR", default=None)

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
                "stream": sys.stderr,
                "formatter": LOG_FORMATTER,
            },
            "stdout": {
                "level": NOTSET,
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
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
