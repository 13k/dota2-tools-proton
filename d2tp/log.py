import logging
from enum import IntEnum


class Level(IntEnum):
    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    TRACE = 5
    NOTSET = logging.NOTSET


logging.addLevelName(Level.TRACE, "TRACE")
logging.basicConfig(level=Level.WARNING)


class Logger:
    logger: logging.Logger

    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def trace(self, *args, **kwargs):
        self.logger.log(Level.TRACE, *args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.logger, name)
