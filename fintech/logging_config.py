import os

# Define the logs directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)


if not os.access(LOG_DIR, os.W_OK):
    raise PermissionError(f"Log directory {LOG_DIR} is not writable.")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    # Log formatters
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} [{name}] {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} [{name}] {message}",
            "style": "{",
        },
    },

    # Handlers for different logs
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "accounts_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "accounts.log"),
            "formatter": "verbose",
        },
        "transactions_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "transactions.log"),
            "formatter": "verbose",
        },
        "payments_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "payments.log"),
            "formatter": "verbose",
        },
    },

    # Loggers for different apps
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "accounts": {
            "handlers": ["accounts_file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "transactions": {
            "handlers": ["transactions_file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "payments": {
            "handlers": ["payments_file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
