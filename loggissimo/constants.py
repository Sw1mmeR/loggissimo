from typing import Final
from enum import IntEnum

DEFAULT_LOGGER_NAME: Final[str] = "default"

START_LOGGER_TRACE = "[Start Loggissimo Trace]"
END_LOGGER_TRACE = "[End Loggissimo Trace]"


class Level(IntEnum):
    TRACE = 5
    DEBUG = 10
    INFO = 20
    DELETE = 24
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

    def __str__(self) -> str:
        return self.name
