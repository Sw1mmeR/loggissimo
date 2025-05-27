from typing import Final
from enum import IntEnum

DEFAULT_LOGGER_NAME: Final[str] = "default"

START_LOGGER_TRACE: Final[str] = "[Start Loggissimo Trace]"
END_LOGGER_TRACE: Final[str] = "[End Loggissimo Trace]"

DEFAULT_FORMAT: Final[str] = "$name@ $time |$level| $stack: $text"


class Level(IntEnum):
    EXCESSIVE = 1
    TRACE = 5
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

    def __str__(self) -> str:
        return self.name
