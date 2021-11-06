import logging
import logging.config


def configure_logger(name, log_path):
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'default': {'format': '%(asctime)s - %(levelname)s - %(message)s', 'datefmt': '%Y-%m-%d %H:%M:%S'}
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'stream': 'ext://sys.stdout'
            },
            'splunk': {
                'level': 'INFO',
                'class': 'splunk_logging_handler.SplunkLoggingHandler',
                'url': 'splunk.blackcrow.int',
                'splunk_key': 'key',
                'splunk_index': 'trading',
                'formatter': 'simple',
                'filters': ['filterForSplunk']
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'filename': log_path,
                'maxBytes': 20000,
                'backupCount': 3
            }
        },
        'loggers': {
            'default': {
                'level': 'DEBUG',
                'handlers': ['console','splunk']
            }
        },
        'disable_existing_loggers': False
    })
    return logging.getLogger(name)


log = configure_logger('default', 'logfile.log')
