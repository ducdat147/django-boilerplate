import sys

from configurations.settings.base import *  # noqa

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
        },
        "json": {
            "()": "configurations.logging.JSONFormatter",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "stdout": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": sys.stdout,
        },
    },
    "root": {"level": "INFO", "handlers": ["stdout"]},
    "loggers": {
        "django": {
            "handlers": ["stdout"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
