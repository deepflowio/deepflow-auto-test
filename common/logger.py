import sys
import logging
from logging import FileHandler
from logging import StreamHandler
from common import common_config

LOG_LEVEL_MAP = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARN,
    "error": logging.ERROR,
}

LOGGER_WORKER = None
LOGGER_INITED = 1


class LoggerManager(object):

    LOGGER = logging.getLogger('root')

    def __init__(self, model_name, log_level, log_file):
        self.model_name = model_name
        self.log_level = LOG_LEVEL_MAP[log_level]
        self.log_file = log_file

    @property
    def file_handler(self):
        file_handler = FileHandler(self.log_file)
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s T%(thread)d-%(threadName)s '
                '%(levelname)s %(module)s.'
                '%(funcName)s.%(lineno)s: %(message)s'
            )
        )
        return file_handler

    @property
    def stdout_handler(self):
        stdout_handler = StreamHandler(sys.stdout)
        stdout_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s T%(thread)d-%(threadName)s '
                '%(levelname)s %(module)s.'
                '%(funcName)s.%(lineno)s: %(message)s'
            )
        )
        return stdout_handler

    @classmethod
    def get_logger(cls):
        return cls.LOGGER

    def init_logger(self):
        self.LOGGER.setLevel(self.log_level)
        self.LOGGER.addHandler(self.file_handler)
        self.LOGGER.addHandler(self.stdout_handler)


class LoggerWorker(LoggerManager):

    LOGGER = logging.getLogger('worker')

    def __init__(self, prefix, log_level="debug"):
        self.log_level = LOG_LEVEL_MAP[log_level]
        self.log_file = f"/root/df-test/log/{prefix}.log"

    def init_logger(self):
        if get_logger_init(self.LOGGER) == False:
            self.LOGGER.setLevel(self.log_level)
            self.LOGGER.addHandler(self.file_handler)
            self.LOGGER.addHandler(self.stdout_handler)
            self.LOGGER.init = LOGGER_INITED


def getLogger(worker=1):
    if not worker:
        return LoggerManager.get_logger()
    else:
        if common_config.test_logger_prefix and get_logger_init(
            LoggerWorker.LOGGER
        ) == False:
            logger_worker = LoggerWorker(common_config.test_logger_prefix)
            logger_worker.init_logger()
        return LoggerWorker.get_logger()


def get_logger_init(logger):
    return hasattr(logger, "init") and logger.init == LOGGER_INITED


deploy_logger = None


def init_deploy_logger(prefix):
    global deploy_logger
    logger_worker = LoggerWorker(prefix)
    logger_worker.init_logger()
    deploy_logger = logger_worker.get_logger()
