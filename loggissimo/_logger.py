import sys
import traceback

from datetime import datetime
from typing import IO, Callable, Self
from weakref import WeakValueDictionary


from .style import Style
from ._utils import print_trace
from ._colorizer import _colorize
from .style import Color, FontStyle
from .exceptions import LoggissimoError
from .constants import DEFAULT_LOGGER_NAME, Level


class __LoggerMeta(type):
    _instances: WeakValueDictionary = WeakValueDictionary()

    def __call__(cls, name: str = DEFAULT_LOGGER_NAME, *args, **kwargs):
        if name not in cls._instances.keys():
            instance = super().__call__(*args, name=name, **kwargs)
            cls._instances[name] = instance
            return instance
        return cls._instances[name]


class _Logger(metaclass=__LoggerMeta):
    _level = Level.INFO

    def __new__(cls, *args, **kwargs) -> Self:
        return super().__new__(cls)

    def __init__(
        self, stream: IO = sys.stdout, level: Level = Level.INFO, *args, **kwargs
    ) -> None:
        self._name_ = kwargs.get("name", DEFAULT_LOGGER_NAME)
        self._force_colorize: bool = False
        self._streams = [stream]
        self.level = level
        self._style: Style = kwargs.get("style", Style())
        self._cache: dict = {}

    def _is_enabled(self, level: Level) -> bool:
        """
        Checking logging capability
        """
        try:
            return self._cache[level]
        except KeyError:
            self._cache[level] = self._valid_log_level(level)
            return self._cache[level]

    def _valid_log_level(self, level: Level):
        return level >= self._level

    @staticmethod
    def catch(func: Callable):
        def _decorator(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                print_trace(traceback.format_tb(ex.__traceback__), ex)

        return _decorator

    def _log(self, level: Level, message: str):
        def colorize():
            inst_name = _colorize(
                f"[{self._name_:<12}]",
                self._style.inst_name.text_color.value,
                self._style.inst_name.font_style.value,
                self._style.inst_name.background_color.value,
            )
            time = _colorize(
                f"{time_now:10}",
                self._style.time.text_color.value,
                self._style.time.font_style.value,
                self._style.time.background_color.value,
            )
            levelname = _colorize(
                f"{str(level):<8}",
                self._style.level[level].text_color.value,
                self._style.levelname_fstyle.value,
                self._style.level[level].background_color.value,
            )
            frame_line = _colorize(
                raw_frame_line,
                self._style.frame.text_color.value,
                self._style.frame.font_style.value,
                self._style.frame.background_color.value,
            )
            _message = _colorize(
                f"{message}",
                self._style.level[level].text_color.value,
                self._style.level[level].font_style.value,
                self._style.level[level].background_color.value,
            )
            return f"{inst_name if self._name_ != DEFAULT_LOGGER_NAME else ''} {time} | {levelname} | {frame_line} - {_message}\n"

        dt = datetime.now()
        time = time_now = dt.strftime("%Y-%m-%d %H:%M:%S")

        # frame = inspect.stack()[3]
        frame = sys._getframe(3)
        raw_frame_line = (
            f"{frame.f_globals['__name__']}:{frame.f_code.co_name}:{frame.f_lineno}"
        )
        inst_name = f"[{self._name_:<12}]"
        levelname = str(level)
        _message = message
        msg = f"{inst_name if self._name_ != DEFAULT_LOGGER_NAME else ''} {time} | {levelname} | {raw_frame_line} - {_message}\n"
        if not self._streams:
            raise LoggissimoError(
                "No streams found. It could have happened that you cleared the list of streams and then did not add a stream."
            )
        for stream in self._streams:
            msg2stream = msg
            if self._force_colorize:
                msg2stream = colorize()
            elif stream.name == "<stdout>":
                msg2stream = colorize()
            stream.write(msg2stream)

    def __repr__(self) -> str:
        return f"<loggissimo.logger streams={self._streams}>"

    def __del__(self) -> None:
        for stream in self._streams:
            stream.close()


class Logger(_Logger):

    def __init__(
        self, file: str = "", level: Level = Level.INFO, *args, **kwargs
    ) -> None:
        super().__init__(
            open(file, "a") if file else sys.stdout,
            level,
            *args,
            **kwargs,
        )
        self.level = level

    @property
    def level(self) -> Level:
        return self._level

    @level.setter
    def level(self, level: Level) -> None:
        if hasattr(self, "_cache"):
            self._cache.clear()
        self._level = level

    @_Logger.catch
    def info(self, message: str = "") -> None:
        if not super()._is_enabled(Level.INFO):
            return
        self._log(Level.INFO, message)

    @_Logger.catch
    def debug(self, message: str = "") -> None:
        if not super()._is_enabled(Level.DEBUG):
            return
        self._log(Level.DEBUG, message)

    @_Logger.catch
    def trace(self, message: str = "") -> None:
        if not super()._is_enabled(Level.TRACE):
            return
        self._log(Level.TRACE, message)

    @_Logger.catch
    def success(self, message: str = "") -> None:
        if not super()._is_enabled(Level.SUCCESS):
            return
        self._log(Level.SUCCESS, message)

    @_Logger.catch
    def warning(self, message: str = "") -> None:
        if not super()._is_enabled(Level.WARNING):
            return
        self._log(Level.WARNING, message)

    @_Logger.catch
    def error(self, message: str = "") -> None:
        if not super()._is_enabled(Level.ERROR):
            return
        self._log(Level.ERROR, message)

    @_Logger.catch
    def critical(self, message: str = "") -> None:
        if not super()._is_enabled(Level.CRITICAL):
            return
        self._log(Level.CRITICAL, message)

    @_Logger.catch
    def add(self, stream: IO | str) -> None:
        """
        Add stream to logger instance output.

        Args
        ----
            stream (IO | str): IO object or filename.
        """
        if isinstance(stream, str):
            stream = open(stream, "a")
        self._streams.append(stream)

    @_Logger.catch
    def remove(self, id: int) -> None:
        """
        Remove output stream from logger instance output streams.

        Args
        ----
            id (int): Stream index in logger streams list (streams are added in the order of calls of the add method).

        Raises
        ------
            LoggissimoError: Stream not found
        """
        if len(self._streams) < id:
            raise LoggissimoError("Stream not found")
        del self._streams[id]

    @_Logger.catch
    def clear(self) -> None:
        """
        Clear logger instance output streams list.
        """
        self._streams.clear()
