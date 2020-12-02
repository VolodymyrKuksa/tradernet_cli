import logging.config
import logging.handlers
import os
from pathlib import Path


def get_logs_directory():
    return Path(os.path.split(__file__)[0] + '/logs')


def configure_logging():
    logs_directory = get_logs_directory()
    if not logs_directory.exists():
        logs_directory.mkdir()

    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'generic': {
                'format': '[%(asctime)s][%(levelname)s][%(module)s]: %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'generic',
                'level': 'INFO',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'generic',
                'level': 'INFO',
                'filename': f'{logs_directory}/tradernet_cli.log',
                'maxBytes': 8192,
                'backupCount': 5,
            },
        },
        'root': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'disable_existing_loggers': False,
    })
