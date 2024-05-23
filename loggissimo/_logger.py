import sys

import string
import inspect
import tempfile
import threading
import multiprocessing

from datetime import datetime
from weakref import WeakValueDictionary
from typing import IO, Callable, Dict, List, Optional, Self, Tuple

from .exceptions import LoggissimoError
from .constants import DEFAULT_LOGGER_NAME, Level
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
    _aggregated_streams: Dict[str, IO] = dict()

    def __new__(cls, *args, **kwargs) -> Self:
        return super().__new__(cls)

    def __init__(self, stream: IO = sys.stdout, *args, **kwargs) -> None:
        self._name_: str = kwargs.get("name", DEFAULT_LOGGER_NAME)
        self._tmp_path: str = kwargs.get("tmp_path", tempfile.gettempdir())
        self._lock = kwargs.get("lock", _Logger.lock)
        self._force_colorize: bool = kwargs.get("force_colorize", False)
        self._format: str = kwargs.get(
            "format", "$instance_name @ $time | $level | $program_line :$message"
        )
        self._message_template = string.Template(f"{self._format}\n")
        self._style: Style = kwargs.get("style", Style())
        self._trace_file_path: str = kwargs.get("tracefile", None)
        self._streams = {stream.name: stream}
        self._proc_name = ""
        self.in_thread: bool = self._check_threading()

    def _check_threading(self) -> bool:
        """
        Determine whether the logger is in a thread
        """
        try:
            _threading = False
            if multiprocessing.current_process().name != "MainProcess":
                _threading = True
                self._proc_name = multiprocessing.current_process().name

            if threading.current_thread().name != "MainThread":
                _threading = True
                self._proc_name = threading.current_thread().name

            return _threading

        except FileNotFoundError as ex:
            print_trace(
                ex,
                "Specify the correct path for temporary files with the argument 'tmp_path'",
            )

        except PermissionError as ex:
            print_trace(
                ex,
                f"Probably a read-only path {self._tmp_path}",
            )

        return False

    def _is_enabled(self, level: Level, module: str) -> bool:
        """
        Checking logging capability
        """
        try:
            cached_level = _Logger._cached_level[level]
        except KeyError:
            _Logger._cached_level[level] = self._valid_log_level(level)
            cached_level = _Logger._cached_level[level]
        try:
            is_module, cached_module = _Logger._modules[module]
            return cached_level and cached_module
        except KeyError:
            modules: List[str] = get_module_combinations(module)
            for mod in modules:
                is_module, cached_module = _Logger._modules.get(mod, (False, None))
                if cached_module is not None:
                    # print(f"module {mod}; {cached_module}", cached_level)
                    return cached_module and cached_level
                cached_module = _Logger._modules[mod] = (is_module, True)
        # print(f"module {mod}; {cached_module}", cached_level)
        return cached_level and cached_module

    def _valid_log_level(self, level: Level):
        return level >= _Logger._level

    @staticmethod
    def catch(func: Callable):
        def _decorator(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                print_trace(ex)

        return _decorator

    def _log(self, level: Level, message: str):
        def colorize():
            inst_name = _colorize(
                f"{name:24}",
                self._style.inst_name.text_color.value,
                self._style.inst_name.font_style.value,
                self._style.inst_name.background_color.value,
            )

            time = _colorize(
                (
                    f"{'.'*8}"
                    if level == Level.DELETE
                    else f"{time_now.strftime('%H:%M:%S'):8}"
                ),
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
                f"{raw_frame_line:32}",
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
            return self._message_template.safe_substitute(
                instance_name=f"{inst_name if self._name_ != DEFAULT_LOGGER_NAME else ''}",
                time=time,
                level=levelname,
                program_line=frame_line,
                message=_message,
            ).lstrip()

        self.in_thread = self._check_threading()
        time_now = datetime.now()
        # (
        #   ""
        #  if level == Level.DELETE
        # else   # .strftime("%Y-%m-%d %H:%M:%S")
        # )
        frame = sys._getframe(3)

        try:
            module = frame.f_globals["__name__"]
        except KeyError:
            module = None

        # Если не задан трейсфайл и не проходим условия выдачи, то выходим
        if not self._is_enabled(level, module):
            return

        raw_frame_line = f"{module}:{frame.f_code.co_name}:{frame.f_lineno}"
        name = (
            f"{self._name_ + f' ({self._proc_name})':24}"
            if self._proc_name
            else f"{self._name_:12}"
        )

        levelname = str(level)
        _message = message
        msg = self._message_template.safe_substitute(
            instance_name=f"{name if self._name_ != DEFAULT_LOGGER_NAME else ''}".format(),
            time=(
                f"{'.' * 19}"
                if level == Level.DELETE
                else f"{time_now.strftime('%Y-%m-%d %H:%M:%S'):19}"
            ),
            level=f"{levelname:<8}",
            program_line=f"{raw_frame_line:52}",
            message=_message,
        ).lstrip()

        # Если не проходим по условию, то выходим
        if not self._is_enabled(level, module):
            return

        if not self._streams:
            raise LoggissimoError(
                "No streams found. It could have happened that you cleared the list of streams and then did not add a stream."
            )
        for stream in self._streams.values():
            self._write_msg_in_stream(stream, msg, self._force_colorize, colorize)

    def _write_msg_in_stream(
        self,
        stream: IO,
        msg: str,
        force_colorize: bool,
        colorizer,
    ) -> None:
        msg2stream = msg
        if force_colorize or stream.name == "<stdout>":
            msg2stream = colorizer()

        stream.write(msg2stream)

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
        for stream in self._streams.values():
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

        for stream in _Logger._aggregated_streams.values():
            self.add(stream)

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
        """
        Set logger format. String of the form:
        '$instance_name $time | $level | $program_line - $message'
        Where optional parameters:
            $instance_name - name of logger instance;
            $time - message time;
            $level - log level;
            $program_line - the line in which the message is called;
            $message - log message;
        """
        return self._format

    @format.setter
    def format(self, format: str) -> None:
        self._format = format
        self._message_template = string.Template(f"{self._format}\n")

    @property
    def style(self) -> Style:
        """
        An object of the style class, on the basis of which the log
        messages are styled
        """
        return self._style

    @style.setter
    def style(self, style: Style) -> None:
        self._style = style

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
    def destructor(self, message: str = "") -> None:
        self._log(Level.DELETE, message)

    @classmethod
    @_Logger.catch
    def addall(cls, stream: IO | str) -> None:
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

        cls._aggregated_streams[stream.name] = stream

        for instance in cls._instances.values():
            instance._streams[stream.name] = stream

    @_Logger.catch
    def add(self, stream: IO | str) -> None:
        """
        Add stream to logger instance output.

        Args
        ----
            stream (IO | str): IO object or filename.
        """
        if isinstance(stream, str):
            if not self._streams.get(stream, False):
                return
            stream = open(stream, "w+", buffering=1)
        self._streams[stream.name] = stream

    @_Logger.catch
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

    @_Logger.catch
    def clear(self) -> None:
        """
        Clear logger instance output streams list.
        """
        self._streams.clear()
