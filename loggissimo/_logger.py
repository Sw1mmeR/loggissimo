import sys
import inspect
import threading
import multiprocessing

from string import Template
from datetime import datetime
from weakref import WeakValueDictionary
from typing import IO, Callable, Dict, Optional, Self

from loggissimo._style import style
from loggissimo._utils import print_trace
from loggissimo.constants import DEFAULT_FORMAT, DEFAULT_LOGGER_NAME, Level


class LoggissimoIO:

    def __init__(self, stream: IO, level: Level | str = Level.GLOBAL, format: str = ""):
        self.stream = stream

        if isinstance(level, str):
            level = Level[level]
        self.level = level

        self.format = format
        self.name = stream.name


# def NewLoggissimoIO(
#     stream: IO, level: Level | str = Level.GLOBAL, format: str = ""
# ) -> LoggissimoIO:

#     if isinstance(level, str):
#         level = Level[level]

#     stream.format = format  # type: ignore
#     stream.level = level  # type: ignore

#     return stream  # type: ignore


class __LoggerMeta(type):
    _instances: WeakValueDictionary = WeakValueDictionary()
    lock = multiprocessing.Lock()

    def __call__(cls, name: str = DEFAULT_LOGGER_NAME, *args, **kwargs):
        if name not in cls._instances.keys():
            instance = super().__call__(*args, name=name, **kwargs)
            cls._instances[name] = instance
            return instance
        return cls._instances[name]

    def __del__(self):
        for instance in self._instances.values():
            for stream in instance._streams.values():
                if stream.name == "<stdout>":
                    continue
            stream.close()


class _Logger(metaclass=__LoggerMeta):
    streams_shared: dict = {}  # STDOUT: (sys.stdout, DEFAULT_FORMAT, None)
    _rgb: bool = True
    _level_global = Level.EXCESSIVE
    _modules: Dict[str, bool] = {"__main__": True}

    def __new__(cls, *args, **kwargs) -> Self:
        return super().__new__(cls)

    def __init__(self, stream: IO = sys.stdout, level: Level | str = Level.INFO, *args, **kwargs) -> None:  # type: ignore
        self.streams: dict[str, LoggissimoIO] = {}

        self._name_: str = kwargs.get("name", DEFAULT_LOGGER_NAME)

        self._force_colorize: bool = kwargs.get("force_colorize", False)
        self._format: str = kwargs.get("format", DEFAULT_FORMAT)
        self._time_format = kwargs.get("time", "%H:%M:%S")  # %Y-%m-%d

        try:
            self.streams = {stream.name: LoggissimoIO(stream)}
        except:
            pass
        self._proc_name = ""

        self.level = level
        self._cached_level: dict = {}

    @property
    def level(self) -> Level | str:
        if list(self.streams.values())[0].level == Level.GLOBAL:
            return self.global_level
        return list(self.streams.values())[0].level

    @level.setter
    def level(self, level: Level | str) -> None:
        if hasattr(self, "_cached_level"):
            self._cached_level.clear()

        if not level:
            level = Level.GLOBAL
        else:
            if isinstance(level, str):
                try:
                    level = Level[level]
                except KeyError:
                    raise NotImplementedError(
                        f"level '{level}' is not implemented"
                    ) from None
        list(self.streams.values())[0].level = level

    @property
    def global_level(self) -> Level | str:
        return _Logger._level_global

    @global_level.setter
    def global_level(self, level: Level | str) -> None:
        if hasattr(self, "_cached_level"):
            self._cached_level.clear()

        if isinstance(level, str):
            level = Level[level]

        _Logger._level_global = level

    @property
    def format(self) -> str:
        return self._format

    @format.setter
    def format(self, new_format: str) -> None:
        self._format = new_format
        list(self.streams.values())[0].format = new_format

    @property
    def rgb(self) -> bool:
        return _Logger._rgb

    @rgb.setter
    def rgb(self, value: bool) -> None:
        _Logger._rgb = value

    def _check_threading(self) -> bool:
        """
        Determine whether the logger is in a thread
        """
        _threading = False
        if multiprocessing.current_process().name != "MainProcess":
            _threading = True
            self._proc_name = multiprocessing.current_process().name

        if threading.current_thread().name != "MainThread":
            _threading = True
            self._proc_name = threading.current_thread().name

        return _threading

    def _name(self) -> str:
        name = (
            f"{self._name_:8} {f'({self._proc_name})':8}"
            if self._proc_name
            else f"{self._name_:12}"
        )
        return name if self._name_ != DEFAULT_LOGGER_NAME else ""

    def _time(self) -> str:
        return datetime.now().strftime(self._time_format)

    def _log(self, level: Level, message: str) -> str:
        self.in_thread = self._check_threading()

        frame = sys._getframe(3)

        try:
            module = frame.f_globals["__name__"]
        except KeyError:
            module = None

        stack = f"{module.replace('.', '/')}:{frame.f_lineno} {frame.f_code.co_name}"
        self._write2streams(message, level, module, stack)

        return message

    def _is_enabled(self, stream, level, module):
        stream_level = (
            self.global_level if stream.level == Level.GLOBAL else stream.level
        )
        # Module
        module_enabled = False
        module_unknown = True
        for key in self._modules:
            if module.startswith(key):
                module_unknown = False
                module_enabled = self._modules[key]
                break

        if module_unknown:
            # Если модуля нет в словаре, значить он по-умолчанию включен
            module_enabled = self._modules[module] = True

        if not module_enabled:
            return False

        # Level
        try:
            cached_level = self._cached_level[(stream, level)]
        except KeyError:
            cached_level = self._cached_level[(stream, level)] = self._check_level(
                level, stream_level
            )
            return cached_level

        return self._check_level(level, stream_level)

    def _check_level(self, level: Level, stream_level: Level) -> bool:
        enabled = False

        if self.global_level < self.level:  # type: ignore
            return level >= self.global_level  # type: ignore

        # Фильтр вывода ВСЕХ логгеров
        enabled = level >= self.global_level  # type: ignore

        # Фильтр вывода логгера
        enabled = level >= self.level  # type: ignore

        # Фильтр вывода в поток
        enabled = level >= stream_level
        return enabled

    def _write2streams(self, message: str, level, module, stack) -> None:
        streams = self.streams.copy()

        for stream_name, values in _Logger.streams_shared.items():
            streams[stream_name] = values

        for stream in streams.values():
            colorize_ = True
            enabled = self._is_enabled(stream, level, module)

            if not enabled:
                continue

            if self._force_colorize or stream.name == "<stdout>":
                colorize_ = False

            stream.stream.write(
                self.colorize(
                    self._name(),
                    self._time(),
                    level,
                    stack,
                    message,
                    colorize_,
                    stream.format,
                )
            )

    def colorize(
        self, name, time, level, stack, message, do_not_colorize: bool, format_: str
    ):
        msg_t = style(
            format_ if format_ else self._format,
            level,
            not _Logger._rgb,
            do_not_colorize,
        )

        return (
            Template(msg_t).safe_substitute(
                name=f"{name:30}",
                time=f"{time}",
                level=f"{level.name:<9}",
                stack=f"{stack}",
                text=f"{message}",
            )
            + "\n"
        )

    def _change_module_status(self, module: str, action: bool) -> None:
        if module in self._modules.keys():
            self._modules[module] = action
            return

        for key in self._modules.keys():
            if key.startswith(module):
                self._modules[key] = action

        if module:
            self._modules[module] = action
            return

        self._modules = dict.fromkeys(self._modules.keys(), action)

    @staticmethod
    def _catch(func: Callable):
        def _decorator(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                print_trace(ex)

        return _decorator


class Logger(_Logger):
    @_Logger._catch
    def info(self, message: str = "") -> str:
        return self._log(Level.INFO, message)

    @_Logger._catch
    def debug(self, message: str = "") -> str:
        return self._log(Level.DEBUG, message)

    @_Logger._catch
    def trace(self, message: str = "") -> str:
        return self._log(Level.TRACE, message)

    @_Logger._catch
    def success(self, message: str = "") -> str:
        return self._log(Level.SUCCESS, message)

    @_Logger._catch
    def warning(self, message: str = "") -> str:
        return self._log(Level.WARNING, message)

    @_Logger._catch
    def error(self, message: str = "") -> str:
        return self._log(Level.ERROR, message)

    @_Logger._catch
    def critical(self, message: str = "") -> str:
        return self._log(Level.CRITICAL, message)

    @_Logger._catch
    def excessive(self, message: str = "") -> str:
        return self._log(Level.EXCESSIVE, message)

    def enable(self, module: str = "__main__") -> None:
        self._change_module_status(module, True)

    def disable(self) -> None:
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])

        if not module:
            return
        path = module.__file__

        if not path:
            return
        file = path.split("/")[-1]

        self._change_module_status(module.__name__, False)

    def __init__(
        self, file: str = "", level: Level | str = Level.INFO, *args, **kwargs
    ) -> None:
        super().__init__(
            open(file, "w", buffering=1) if file else sys.stdout,  # type: ignore
            level=level,
            *args,
            **kwargs,
        )

        for stream in _Logger.streams_shared.values():
            self.add(stream, stream.level, stream.format)  # type: ignore

    @classmethod
    @_Logger._catch
    def addall(
        cls, stream: IO | str, level: Level | str = Level.GLOBAL, format: str = ""
    ) -> None:
        """
        Add stream to ALL logger instances.

        Args
        ----
            stream (IO | str): IO object or filename.
        """
        if isinstance(stream, str):
            try:
                _Logger.streams_shared[stream]
                return
            except KeyError:
                stream = open(stream, "w+", buffering=1)

        cls.streams_shared[stream.name] = LoggissimoIO(stream, level, format)

    @_Logger._catch
    def add(
        self,
        stream: IO | str,
        level: Level | str | None = None,
        format: str = "",
    ) -> None:
        """
        Add stream to logger instance output.

        Args
        ----
            stream (IO | str): IO object or filename.
        """
        if isinstance(stream, str):
            if self.streams.get(stream, False):
                return
            stream = open(stream, "w+", buffering=1)

        if level is None:
            level = self.level
        elif isinstance(level, str):
            level = Level[level]

        self.streams[stream.name] = LoggissimoIO(stream, level, format)

    @_Logger._catch
    def remove(self, name: str) -> None:
        """
        Remove output stream from logger instance output streams.

        Args
        ----
            id (int): Stream index in logger streams list (streams are added in the order of calls of the add method).

        Raises
        ------
            LoggissimoError: Stream not found
        """
        if name in self.streams.keys():
            del self.streams[name]

    @_Logger._catch
    def clear(self) -> None:
        """
        Clear logger instance output streams list.
        """
        self.streams.clear()

    @classmethod
    @_Logger._catch
    def remove_all(cls, name: str) -> None:
        """
        Remove output stream from logger instance output streams.

        Args
        ----
            id (int): Stream index in logger streams list (streams are added in the order of calls of the add method).

        Raises
        ------
            LoggissimoError: Stream not found
        """
        if name in cls.streams_shared.keys():
            del cls.streams_shared[name]

    @classmethod
    @_Logger._catch
    def clear_all(cls) -> None:
        """
        Clear logger instance output streams list.
        """
        cls.streams_shared.clear()
