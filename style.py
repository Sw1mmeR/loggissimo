from enum import Enum
from typing import Tuple, Dict
from collections import namedtuple

from _colorizer import _Colors, _FontStyle
from constants import Level


class Color(Enum):
    """
    Colors for text
    """

    BLACK = _Colors.BLACK
    RED = _Colors.RED
    GREEN = _Colors.GREEN
    BLUE = _Colors.BLUE
    MAGENTA = _Colors.MAGENTA
    CYAN = _Colors.CYAN
    YELLOW = _Colors.YELLOW
    WHITE = _Colors.WHITE
    DEFAULT = _Colors.DEFAULT


class FontStyle(Enum):
    """
    Font styles for text
    """

    BOLD = _FontStyle.BOLD
    FADED = _FontStyle.FADED
    ITALIC = _FontStyle.ITALIC
    UNDERLINE = _FontStyle.UNDERLINE
    DEFAULT = _FontStyle.DEFAULT


class Style:
    """
    Style for logger. Controls the color and style of each logger element
    and each level.
    """

    def __init__(
        self,
        inst_name_style: Tuple[Color, FontStyle] = (Color.YELLOW, FontStyle.DEFAULT),
        time_style: Tuple[Color, FontStyle] = (Color.BLUE, FontStyle.DEFAULT),
        levelname_fontstyle: FontStyle = FontStyle.BOLD,
        level_style: Dict[Level, Tuple[Color, FontStyle]] = {},
    ) -> None:
        style = namedtuple("style", ["color", "font_style"])

        self.inst_name = style(inst_name_style[0].value, inst_name_style[1].value)
        self.time = style(time_style[0].value, time_style[1].value)

        self.level: dict = {}

        _trace_style = level_style.get(Level.TRACE, (Color.CYAN, FontStyle.DEFAULT))
        self.level[Level.TRACE] = style(_trace_style[0].value, _trace_style[1].value)
        _debug_style = level_style.get(Level.DEBUG, (Color.BLUE, FontStyle.DEFAULT))
        self.level[Level.DEBUG] = style(_debug_style[0].value, _debug_style[1].value)
        _info_style = level_style.get(Level.INFO, (Color.WHITE, FontStyle.DEFAULT))
        self.level[Level.INFO] = style(_info_style[0].value, _info_style[1].value)
        _success_style = level_style.get(
            Level.SUCCESS, (Color.GREEN, FontStyle.DEFAULT)
        )
        self.level[Level.SUCCESS] = style(
            _success_style[0].value, _success_style[1].value
        )
        _warn_style = level_style.get(Level.WARNING, (Color.YELLOW, FontStyle.DEFAULT))
        self.level[Level.WARNING] = style(_warn_style[0].value, _warn_style[1].value)
        _error_style = level_style.get(Level.ERROR, (Color.RED, FontStyle.DEFAULT))
        self.level[Level.ERROR] = style(_error_style[0].value, _error_style[1].value)
        _crit_style = level_style.get(
            Level.CRITICAL, (Color.MAGENTA, FontStyle.DEFAULT)
        )
        self.level[Level.CRITICAL] = style(_crit_style[0].value, _crit_style[1].value)

        self.levelname_fstyle = levelname_fontstyle.value
