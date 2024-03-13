import inspect
import os
import sys
import traceback

from datetime import datetime
from typing import IO, Callable, List, Literal, Self
from weakref import WeakValueDictionary
from ._utils import print_trace
from style import Style
from _colorizer import _colorize
from style import Color, FontStyle
from _utils import print_trace
from _colorizer import _colorize
from style import Color, FontStyle
from exceptions import LoggissimoError
from constants import DEFAULT_LOGGER_NAME, Level


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
        self._style: Style = kwargs.get("style", Style())

    @staticmethod
    def catch(func: Callable):
        def _decorator(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                print_trace(traceback.format_tb(ex))

        return _decorator

    def _log(self, level: Level, message: str):
        dt = datetime.now()

        # Пропускаем 3 вызова - '_log()', 'info()', '_decorator()'
        frame = inspect.stack()[3]
        trace_line = f"{frame.filename.split('/')[-1]}:{frame.function}:{frame.lineno}"

        inst_name = _colorize(
            f"[{self._name_:<12}]",
            self._style.inst_name.color,
            self._style.inst_name.font_style,
        )
        time = _colorize(
            f"{dt.strftime('%Y-%m-%d %H:%M:%S'):10}",
            self._style.time.color,
            self._style.time.font_style,
        )
        levelname = _colorize(
            f"{str(level):<8}",
            self._style.level[level].color,
            self._style.levelname_fstyle,
        )
        _msg = _colorize(
            f"{message}",
            self._style.level[level].color,
            self._style.level[level].font_style,
        )
        msg = f"{inst_name} {time} | {levelname} | {trace_line} - {_msg}\n"
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
