import sys
import traceback

from sys import stdout
from datetime import datetime
from colorama import Fore, init
from typing import IO, Callable, List, Literal, Self
from weakref import WeakValueDictionary

from ._utils import print_trace
from .exceptions import LoggissimoError
from .constants import DEFAULT_LOGGER_NAME, END_LOGGER_TRACE, START_LOGGER_TRACE, Level

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
        self._streams = [stream]

    @staticmethod
    def catch(func: Callable):
        def _decorator(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                print_trace(traceback.format_tb(ex.__traceback__))

        return _decorator

    def _log(self, level: Level, message: str):
        dt = datetime.now()
        msg = f"{Fore.YELLOW}[{self._name_:<12}] {Fore.GREEN}{dt.strftime('%Y-%m-%d %H:%M:%S'):10} {Fore.RESET}| {Fore.CYAN}{str(level):<8} {Fore.RESET}| {message}\n"
        if not self._streams:
            raise LoggissimoError(
                "No streams found. It could have happened that you cleared the list of streams and then did not add a stream."
            )
        for stream in self._streams:
            stream.write(msg)

    def __del__(self) -> None:
        for stream in self._streams:
            stream.close()


class Logger(_Logger):

    def __init__(self, file: str = "", *args, **kwargs) -> None:
        super().__init__(open(file, "a") if file else sys.stdout, *args, **kwargs)

    @_Logger.catch
    def info(self, message: str = "") -> None:
        self._log(Level.INFO, message)

    @_Logger.catch
    def debug(self, message: str = "") -> None:
        self._log(Level.DEBUG, message)

    @_Logger.catch
    def trace(self, message: str = "") -> None:
        self._log(Level.TRACE, message)

    @_Logger.catch
    def success(self, message: str = "") -> None:
        self._log(Level.SUCCESS, message)

    @_Logger.catch
    def warning(self, message: str = "") -> None:
        self._log(Level.WARNING, message)

    @_Logger.catch
    def error(self, message: str = "") -> None:
        self._log(Level.ERROR, message)

    @_Logger.catch
    def critical(self, message: str = "") -> None:
        self._log(Level.CRITICAL, message)

    @_Logger.catch
    def add(self, stream: IO | str) -> None:
        if isinstance(stream, str):
            stream = open(stream, "a")
        self._streams.append(stream)

    @_Logger.catch
    def remove(self, id: int) -> None:
        if len(self._streams) < id:
            raise LoggissimoError("No such stream!")
        del self._streams[id]

    @_Logger.catch
    def clear(self) -> None:
        self._streams.clear()
