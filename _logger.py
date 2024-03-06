import sys

from typing import IO, Self
from datetime import datetime
from weakref import WeakValueDictionary

from colorama import Fore, init

from constants import DEFAULT_LOGGER_NAME, Level
from exceptions import LoggissimoError

init(autoreset=True)


class __LoggerMeta(type):
    _instances: WeakValueDictionary = WeakValueDictionary()

    def __call__(cls, name: str = DEFAULT_LOGGER_NAME, *args, **kwargs):
        if name not in cls._instances.keys():
            instance = super().__call__(*args, name=name, **kwargs)
            cls._instances[name] = instance
            return instance
        return cls._instances[name]


class _Logger(metaclass=__LoggerMeta):
    def __new__(cls, *args, **kwargs) -> Self:
        return super().__new__(cls)

    def __init__(self, stream: IO = sys.stdout, *args, **kwargs) -> None:
        self._name_ = kwargs["name"]
        self._stream = stream

    def add(self, name: str):
        pass

    def remove(self, name: str):
        pass

    def _log(self, level: Level, message: str):
        dt = datetime.now()
        msg = f"{Fore.YELLOW}[{self._name_:^12}] {Fore.GREEN}{dt.strftime('%Y-%m-%d %H:%M:%S'):10} {Fore.RESET}| {Fore.CYAN}{str(level):<8} {Fore.RESET}| {message}\n"
        self._stream.write(msg)


class Logger(_Logger):
    def info(self, message: str = ""):
        self._log(Level.INFO, message)

    def debug(self, message: str = ""):
        self._log(Level.DEBUG, message)

    def trace(self, message: str = ""):
        self._log(Level.TRACE, message)

    def success(self, message: str = ""):
        self._log(Level.SUCCESS, message)

    def warning(self, message: str = ""):
        self._log(Level.WARNING, message)

    def error(self, message: str = ""):
        self._log(Level.ERROR, message)

    def critical(self, message: str = ""):
        self._log(Level.CRITICAL, message)
