from logging import DEBUG
import os

# Define the logs directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")

try:
    os.makedirs(LOG_DIR, exist_ok=True)
    if not os.access(LOG_DIR, os.W_OK):
        raise PermissionError(f"Log directory {LOG_DIR} is not writable.")
except Exception as e:
    raise RuntimeError(f"Failed to set up log directory: {e}")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    # Log formatters
    "formatters": {
    "verbose": {
        "format": "{levelname} {asctime} [{name}] {message} [User ID: {user_id}] [IP: {ip_address}]",
        "style": "{",
    },
    "simple": {
        "format": "{levelname} [{name}] {message}",
        "style": "{",
        },
    },

    # Filters
    "filters": {
        "user_context": {
            "()": "fintech.logging_filters.UserContextFilter",
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
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "accounts.log"),
            "maxBytes": 1024 * 1024 * 20,  
            "backupCount": 20,
            "formatter": "verbose",
        },
        "transactions_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "transactions.log"),
            "maxBytes": 1024 * 1024 * 20,  # 5 MB
            "backupCount": 20,
            "formatter": "verbose",
        },
        "admin_app_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "admin_app.log"),
            "maxBytes": 1024 * 1024 * 20,  # 5 MB
            "backupCount": 20,
            "formatter": "verbose",
        },
        "statement_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "statement.log"),
            "maxBytes": 1024 * 1024 * 20,  # 5 MB
            "backupCount": 20,
            "formatter": "verbose",
        },
        "rbac_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "rbac.log"),
            "maxBytes": 1024 * 1024 * 20,  # 5 MB
            "backupCount": 20,
            "formatter": "verbose",
        },
    },

    # Loggers for different apps
    "loggers": {
        "django": {
            "handlers": ["console"],
            # "level": "DEBUG" if DEBUG else "INFO",
            "level": "INFO",
            "propagate": True,
        },
        "django.utils.autoreload": {
            "handlers": ["console"],
            "level": "WARNING",  # reduce verbosity
            "propagate": False,
        },
        "accounts": {
            "handlers": ["accounts_file", "console"],
            "level": "DEBUG",
            "propagate": False,
            "filters": ["user_context"],
        },
        "transactions": {
            "handlers": ["transactions_file", "console"],
            "level": "DEBUG",
            "propagate": False,
            "filters": ["user_context"],
        },
        "admin_app": {
            "handlers": ["admin_app_file", "console"],
            "level": "DEBUG",
            "propagate": False,
            "filters": ["user_context"],
        },
        "statement": {
            "handlers": ["statement_file", "console"],
            "level": "DEBUG",
            "propagate": False,
            "filters": ["user_context"],
        },
        "rbac": {
            "handlers": ["rbac_file" ,"console"],
            "level": "DEBUG",
            "propagate": False,
            "filters": ["user_context"],
        },
    },
}
