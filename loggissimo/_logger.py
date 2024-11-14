import sys
import inspect
import threading
import multiprocessing

from string import Template
from datetime import datetime
from weakref import WeakValueDictionary
from typing import IO, Callable, Dict, List, Optional, Self, Tuple

from ._style import style
from .exceptions import LoggissimoError
from .constants import DEFAULT_FORMAT, DEFAULT_LOGGER_NAME, Level
from ._utils import print_trace, get_module_combinations


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
    _level = Level.INFO
    _modules: Dict[str, Tuple[bool, bool]] = {"__main__": (True, True)}
    _cached_level: dict = {}
    _aggregated_streams: Dict[str, Tuple[IO, str]] = dict()
    _rgb: bool = True
    _streams: dict = {}

    def __new__(cls, *args, **kwargs) -> Self:
        return super().__new__(cls)

    def __init__(self, stream: IO = sys.stdout, *args, **kwargs) -> None:
        self._name_: str = kwargs.get("name", DEFAULT_LOGGER_NAME)
        self._force_colorize: bool = kwargs.get("force_colorize", False)
        self._format: str = kwargs.get("format", DEFAULT_FORMAT)
        self._time_format = kwargs.get("time", "%H:%M:%S")  # %Y-%m-%d
        try:
            self._streams = {stream.name: (stream, self._format, self._level)}
        except:
            pass
        self._proc_name = ""

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

    def _is_enabled(self, stream, level: Level, module: str) -> bool:
        """
        Checking logging capability
        """
        try:
            cached_level = _Logger._cached_level[(stream, level)]
        except KeyError:
            _Logger._cached_level[(stream, level)] = self._valid_log_level(
                stream, level
            )
            cached_level = _Logger._cached_level[(stream, level)]
        try:
            is_module, cached_module = _Logger._modules[module]
            return cached_level and cached_module
        except KeyError:
            modules: List[str] = get_module_combinations(module)
            for mod in modules:
                is_module, cached_module = _Logger._modules.get(mod, (False, None))  # type: ignore
                if cached_module is not None:
                    return cached_module and cached_level
                cached_module = _Logger._modules[mod] = (is_module, True)
        return cached_level and cached_module

    def _valid_log_level(self, stream, level: Level):
        return level >= self._streams[stream.name][2]

    @staticmethod
    def _catch(func: Callable):
        def _decorator(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                print_trace(ex)

        return _decorator

    def _log(self, level: Level, message: str) -> str:
        def colorize(do_not_colorize: bool, format_: str):
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
                    level=f"{level.name:<8}",
                    stack=f"{stack}",
                    text=f"{message}",
                )
                + "\n"
            )

        self.in_thread = self._check_threading()
        time_now = datetime.now()
        frame = sys._getframe(3)

        try:
            module = frame.f_globals["__name__"]
        except KeyError:
            module = None

        # if not self._is_enabled(level, module):
        #     return

        formatted_time = time_now.strftime(self._time_format)
        time = (
            f"{'.' * len(formatted_time)}"
            if level == Level.DELETE
            else f"{formatted_time}"
        )

        stack = f"{module.replace('.', '/')}:{frame.f_lineno} {frame.f_code.co_name}"
        name = (
            f"{self._name_:8} {f'({self._proc_name})':8}"
            if self._proc_name
            else f"{self._name_:12}"
        )
        name = name if self._name_ != DEFAULT_LOGGER_NAME else ""

        if not self._streams:
            raise LoggissimoError(
                "No streams found. It could have happened that you cleared the list of streams and then did not add a stream."
            )

        for stream, stream_format, stream_level in self._streams.values():
            colorize_ = True
            if not self._is_enabled(stream, level, module):
                continue
            if self._force_colorize or stream.name == "<stdout>":
                colorize_ = False
            stream.write(colorize(colorize_, stream_format))

        return message

    def _change_module_status(
        self, module: Optional[str], action: bool, path: str = ""
    ):
        if module in _Logger._modules.keys():
            _Logger._modules[module] = (_Logger._modules[module][0], action)
            return

        if module:
            _Logger._modules[module] = (path == "__init__.py", action)
            return

        _Logger._modules = dict.fromkeys(
            _Logger._modules.keys(), (path == "__init__.py", action)
        )
        return

    def __repr__(self) -> str:
        return f"<loggissimo.logger level={Logger.level} streams={self._streams}>"

    def __del__(self) -> None:
        for stream, format, level in self._streams.values():
            try:
                _Logger._aggregated_streams[stream.name]
                continue
            except KeyError:
                pass
            if stream.name == "<stdout>":
                continue
            stream.close()


class Logger(_Logger):

    def __init__(
        self, file: str = "", level: Level = Level.INFO, *args, **kwargs
    ) -> None:
        super().__init__(
            open(file, "w") if file else sys.stdout,
            *args,
            **kwargs,
        )

        for stream, format in _Logger._aggregated_streams.values():
            self.add(stream, format)

        if isinstance(level, str):
            level = Level[level]

        if level < self.level:  # type: ignore
            self.level = level

    @property
    def level(self) -> Level | str:
        return _Logger._level

    @level.setter
    def level(self, level: Level | str) -> None:
        if hasattr(self, "_cached_level"):
            _Logger._cached_level.clear()
        if isinstance(level, str):
            level = Level[level]
        _Logger._level = level

    @property
    def format(self) -> str:
        return self._format

    @format.setter
    def format(self, new_format: str) -> None:
        self._format = new_format

    @property
    def rgb(self) -> bool:
        return _Logger._rgb

    @rgb.setter
    def rgb(self, value: bool) -> None:
        _Logger._rgb = value

    def enable(self, module: Optional[str] = None) -> None:
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

        self._change_module_status(module.__name__, False, path=file)

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
    def destructor(self, message: str = "") -> str:
        return self._log(Level.DELETE, message)

    @classmethod
    @_Logger._catch
    def addall(cls, stream: IO | str, format: str = "") -> None:
        """
        Add stream to ALL logger instances.

        Args
        ----
            stream (IO | str): IO object or filename.
        """
        if isinstance(stream, str):
            try:
                _Logger._aggregated_streams[stream]
                return
            except KeyError:
                stream = open(stream, "w+", buffering=1)

        cls._aggregated_streams[stream.name] = (stream, format)

        for instance in cls._instances.values():
            instance._streams[stream.name] = (stream, format)

    @_Logger._catch
    def add(
        self, stream: IO | str, format: str = "", level: Level | str | None = None
    ) -> None:
        """
        Add stream to logger instance output.

        Args
        ----
            stream (IO | str): IO object or filename.
        """
        if isinstance(stream, str):
            if self._streams.get(stream, False):
                return
            stream = open(stream, "w+", buffering=1)

        if level is None:
            level = self.level
        elif isinstance(level, str):
            level = Level[level]

        self._streams[stream.name] = (stream, format, level)

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
        del self._streams[name]

    @_Logger._catch
    def clear(self) -> None:
        """
        Clear logger instance output streams list.
        """
        self._streams.clear()

    @classmethod
    @_Logger._catch
    def delete(cls, name: str) -> None:
        """
        Remove logger instance by name.

        Args
        ----
            name (str): Instance name.
        """
        del cls._instances[name]
