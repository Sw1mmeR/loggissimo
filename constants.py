from enum import IntEnum
from typing import Final

DEFAULT_LOGGER_NAME: Final[str] = "default"


class Level(IntEnum):
    TRACE = 5
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

    def __str__(self) -> str:
        return self.name
