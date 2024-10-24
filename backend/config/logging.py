logging_config = {
  'version': 1,
  'disable_existing_loggers': False,
  "loggers": {
    '': {  # root logger
      'handlers': ['console', 'file'],
      'level': 'INFO',
      'propagate': True
    },
    'alembic.runtime.migration': {
      'handlers': ['console', 'file'],
      'level': 'WARN',
      'propagate': False
    },
    'urllib3.connectionpool': {
      'handlers': ['console', 'file'],
      'level': 'WARN',
      'propagate': False
    },
    'elasticsearch': {
      'handlers': ['console', 'file'],
      'level': 'WARN',
      'propagate': False
    },
    'ElasticIndex': {
      'handlers': ['console', 'file'],
      'level': 'WARN',
      'propagate': False
    },
  },
  "formatters": {
    "simple": {
      "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
  },
  "root": {
    "level": "DEBUG",
    "handlers": [
      "console",
      "file",
      "email"
    ]
  },
  "handlers": {
    "console": {
      "formatter": "simple",
      "class": "logging.StreamHandler",
      "stream": "ext://sys.stdout",
      "level": "DEBUG"
    },
    "file": {
      "level": "DEBUG",
      "formatter": "simple",
      "class": "logging.FileHandler",
      "filename": "star_drive.log"
    },
    "email": {
      "level": "ERROR",
      "formatter": "simple",
      "class": "logging.handlers.SMTPHandler",
      "mailhost": ["smtp.mail.virginia.edu", 25],
      "fromaddr": "ajl2j@virginia.edu",
      "toaddrs": ["ajl2j@virginia.edu"],
      "subject": "Autism DRIVE FAILURE",
    }
  }
}

