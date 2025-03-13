from os import getenv

ADMIN_EMAIL = getenv("ADMIN_EMAIL")
MAIL_DEFAULT_SENDER = getenv("MAIL_DEFAULT_SENDER", "")
MAIL_DEFAULT_USER = getenv("MAIL_DEFAULT_USER", "")
MAIL_PASSWORD = getenv("MAIL_PASSWORD", "")
MAIL_SERVER = getenv("MAIL_SERVER", "")
MAIL_PORT = getenv("MAIL_PORT", 25)
MAIL_USERNAME = getenv("MAIL_USERNAME", "")
MAIL_USE_SSL = getenv("MAIL_USE_SSL", False)
MAIL_USE_TLS = getenv("MAIL_USE_TLS", False)

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "loggers": {
        "": {  # root logger
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "alembic.runtime.migration": {
            "handlers": ["console", "file"],
            "level": "WARN",
            "propagate": False,
        },
        "urllib3.connectionpool": {
            "handlers": ["console", "file"],
            "level": "WARN",
            "propagate": False,
        },
        "elasticsearch": {
            "handlers": ["console", "file"],
            "level": "WARN",
            "propagate": False,
        },
        "ElasticIndex": {
            "handlers": ["console", "file"],
            "level": "WARN",
            "propagate": False,
        },
    },
    "formatters": {
        "simple": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
    },
    "root": {"level": "DEBUG", "handlers": ["console", "file", "email"]},
    "handlers": {
        "console": {"propagate": False},
        "urllib3.connectionpool": {
            "handlers": ["console", "file"],
            "level": "WARN",
            "propagate": False,
        },
        "elasticsearch": {
            "handlers": ["console", "file"],
            "level": "WARN",
            "propagate": False,
        },
        "ElasticIndex": {
            "handlers": ["console", "file"],
            "level": "WARN",
            "propagate": False,
        },
    },
    "formatters": {
        "simple": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
    },
    "root": {"level": "DEBUG", "handlers": ["console", "file", "email"]},
    "handlers": {
        "console": {
            "formatter": "simple",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "level": "DEBUG",
        },
        "file": {
            "level": "DEBUG",
            "formatter": "simple",
            "class": "logging.FileHandler",
            "filename": "star_drive.log",
        },
        "email": {
            "level": "ERROR",
            "formatter": "simple",
            "class": "logging.handlers.SMTPHandler",
            "mailhost": [MAIL_SERVER, MAIL_PORT],
            "fromaddr": ADMIN_EMAIL,
            "toaddrs": [ADMIN_EMAIL],
            "subject": "Autism DRIVE FAILURE",
            "credentials": (
                (MAIL_USERNAME, MAIL_PASSWORD)
                if MAIL_USERNAME and MAIL_PASSWORD
                else None
            ),
        },
    },
}
