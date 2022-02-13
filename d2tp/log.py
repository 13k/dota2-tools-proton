import logging
from typing import Final

CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG
TRACE: Final = 5
NOTSET = logging.NOTSET

logging.addLevelName(TRACE, "TRACE")
logging.basicConfig(level=WARNING)


class Logger:
    logger: logging.Logger

    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def trace(self, *args, **kwargs):
        self.logger.log(TRACE, *args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.logger, name)
