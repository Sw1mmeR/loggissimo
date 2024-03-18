import sys
import traceback

from datetime import datetime
from typing import IO, Callable, List, Optional, Self, Tuple, overload
from weakref import WeakValueDictionary
import multiprocessing
import threading
import inspect
import os
import random
import string
import tempfile

from style import Style
from _utils import print_trace, get_module_combinations
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
    _level = Level.INFO
    def __new__(cls, *args, **kwargs) -> Self:
        return super().__new__(cls)

    def __init__(
        self, stream: IO = sys.stdout, level: Level = Level.INFO, *args, **kwargs
    ) -> None:
        self._name_:str = kwargs.get("name", DEFAULT_LOGGER_NAME)
        self._tmp_path: str = kwargs.get("tmp_path", tempfile.gettempdir())
        self._lock = kwargs.get("lock", multiprocessing.Lock())
        self._disable_threads: bool = kwargs.get("disable_threads", False)
        self._force_colorize: bool = kwargs.get("force_colorize", False)
        self._format: str = kwargs.get("format", "[$instance_name] $time | $level | $program_line - $message")
        self._message_template = string.Template(f"{self._format}\n")
        self._style: Style = kwargs.get("style", Style())
        self._streams = [stream]
        self.level = level
        self._cache: dict = {}
        self._modules: dict = {}
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

            if _threading and not self._disable_threads:
                file_name = ''.join(random.choice(string.ascii_lowercase) for i in range(16))
                self._tmp_file_path = os.path.abspath(f"{self._tmp_path}" + \
                                                      f"{'' if self._tmp_path.endswith('/') else '/'}{file_name}")
                self._tmp_out_stream: IO = open(self._tmp_file_path, 'w+')

            return _threading
        
        except FileNotFoundError as ex:
            print_trace(traceback.format_tb(ex.__traceback__), ex, 
                        "Specify the correct path for temporary files with the argument 'tmp_path'")

        except PermissionError as ex:
            print_trace(traceback.format_tb(ex.__traceback__), ex, 
                        f"Probably a read-only path {self._tmp_path}")
            
        return False
        
    def _is_enabled(self, level: Level, module: str) -> bool:
        """
        Checking logging capability
        """
        try:
            cached_level = self._cache[level]
        except KeyError:
            self._cache[level] = self._valid_log_level(level)
            cached_level = self._cache[level]

        try:
            cached_module = self._modules[module]
            return cached_level and cached_module
        except KeyError:
            modules: List[str] = get_module_combinations(module)
            for mod in modules:
                cached_module = self._modules.get(mod, None)
                if cached_module is not None:
                    break
                self._modules[mod] = True
                cached_module = self._modules[mod]

        return cached_level and cached_module

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
                f"[{self._name_:<6}{' (' if self._proc_name else ''}{self._proc_name:<6}"+\
                    f"{')' if self._proc_name else ''}]",
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
            #return f"{inst_name if self._name_ != DEFAULT_LOGGER_NAME else ''} {time} | {levelname} | {frame_line} - {_message}\n"
            #[$instance_name] $time | $level | $program_line - $message
            return self._message_template.safe_substitute(
                instance_name = f"{inst_name if self._name_ != DEFAULT_LOGGER_NAME else ''}",
                time = time,
                level = levelname,
                program_line = frame_line,
                message = _message
            )
        
        dt = datetime.now()
        time = time_now = dt.strftime("%Y-%m-%d %H:%M:%S")
        # frame = inspect.stack()[3]
        frame = sys._getframe(3)

        try:
            module = frame.f_globals["__name__"]
        except KeyError:
            module = None

        if not self._is_enabled(level, module):
            return

        raw_frame_line = f"{module}:{frame.f_code.co_name}:{frame.f_lineno}"
        inst_name = f"[{self._name_:<12}]"
        levelname = str(level)
        _message = message
        msg = f"{inst_name if self._name_ != DEFAULT_LOGGER_NAME else ''} {time} | {levelname} | {raw_frame_line} - {_message}\n"
        if not self._streams:
            raise LoggissimoError(
                "No streams found. It could have happened that you cleared the list of streams and then did not add a stream."
            )
        # Если в потоке, то не пишем в наши стримы
        if self.in_thread and not self._disable_threads:
            self._write_msg_in_stream(self._tmp_out_stream, msg, True, colorize)
        else:
            for stream in self._streams:
                self._write_msg_in_stream(stream, 
                                          msg, self._force_colorize, colorize)

    def _write_msg_in_stream(self, 
                            stream: IO, 
                            msg: str, 
                            force_colorize: bool, 
                            colorizer,
                            thread: bool = False
                            ) -> None:
            msg2stream = msg
            if force_colorize:
                msg2stream = colorizer()
            elif stream.name == "<stdout>":
                if not thread or self._disable_threads:
                    msg2stream = colorizer()

            stream.write(msg2stream)

    def _change_module_status(self, module: Optional[str], action: bool):
        if not module:
            for key in self._modules.keys():
                self._modules[key] = action
        self._modules[module] = action

    def __repr__(self) -> str:
        return f"<loggissimo.logger streams={self._streams}>"

    def __del__(self) -> None:
        # Если были в потоках, то надо подчистить все за собой
        if self.in_thread and not self._disable_threads:
            self._tmp_out_stream.seek(0)
            self._lock.acquire()
            for line in self._tmp_out_stream:
                for stream in self._streams:
                    self._write_msg_in_stream(
                        stream,
                        line,
                        False,
                        None,
                        True
                    )
            
            self._tmp_out_stream.close()
            os.remove(self._tmp_file_path)
            self._lock.release()
        if not self.in_thread:
            for stream in self._streams:
                if stream.name != "<stdout>":
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
    
    @property
    def format(self) -> str:
        return self._format
    
    @format.setter
    def format(self, format: str) -> None:
        """
        Set logger format. Pass a line like this as input:
        '$instance_name $time | $level | $program_line - $message'
        Where optional parameters:
            $instance_name - name of logger instance;
            $time - message time;
            $level - log level;
            $program_line - the line in which the message is called;
            $message - log message;
        """
        self._format = format
        self._message_template = string.Template(f"{self._format}\n")

    @overload
    def enable(self) -> None: ...

    @overload
    def enable(self, module: str) -> None: ...

    def enable(self, module: Optional[str] = None) -> None:
        self._change_module_status(module, True)

    @overload
    def disable(self) -> None: ...

    @overload
    def disable(self, module: str) -> None: ...

    def disable(self, module: Optional[str] = None) -> None:
        self._change_module_status(module, False)

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
    def add(self, stream: IO | str, cache_path: str) -> None:
        """
        Add stream to logger instance output.

        Args
        ----
            stream (IO | str): IO object or filename.
            cache_path (str): path for creation temporary files
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