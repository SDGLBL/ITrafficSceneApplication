import logging
import logging.config
import logging.config
import platform
from multiprocessing import Process

config_info_for_windows = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'concurrent_log_handler.ConcurrentRotatingFileHandler',
            # 当达到10MB时分割日志
            'maxBytes': 1024 * 1024 * 10,
            # 最多保留50份文件
            'backupCount': 50,
            # If delay is true,
            # then file opening is deferred until the first call to emit().
            'delay': True,
            'filename': 'main.log',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console','file'],
            'level': 'INFO',
        },
    }
}

config_info_for_linux = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'cloghandler.ConcurrentRotatingFileHandler',
            # 当达到10MB时分割日志
            'maxBytes': 1024 * 1024 * 10,
            # 最多保留50份文件
            'backupCount': 50,
            # If delay is true,
            # then file opening is deferred until the first call to emit().
            'delay': True,
            'filename': 'logs/main.log',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'default': {
            'handlers': ['console','file'],
            'level': 'INFO',
        },
    }
}



def get_logger(filename='logs/main.log'):
    config_info_for_windows['handlers']['file']['filename'] = filename
    config_info_for_linux['handlers']['file']['filename'] = filename
    if platform.system() is 'Windows':
        logging.config.dictConfig(config_info_for_windows)
    elif platform.system() is 'Linux':
        logging.config.dictConfig(config_info_for_linux)
    else:
        raise EnvironmentError('运行环境错误，该程序不能在{0}上运行'.format(platform.system()))
    return logging.getLogger(__name__)

def t1():
    logger = get_logger(filename='test1.txt')
    for _ in range(10):
        logger.info('process 1 1')
def t2():
    logger = get_logger(filename='test2.txt')
    for _ in range(10):
        logger.info('process 2 2')

if __name__ == '__main__':
    x = Process(target=t1)
    y = Process(target=t2)
    x.start()
    y.start()
    x.join()
    y.join()