from enum import Enum
from typing import Tuple, Dict
from collections import namedtuple

from constants import Level
from _colorizer import _Colors, _FontStyle


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
        inst_name_style: Tuple[Color, FontStyle, Color] = (
            Color.YELLOW,
            FontStyle.DEFAULT,
            Color.DEFAULT,
        ),
        time_style: Tuple[Color, FontStyle, Color] = (
            Color.GREEN,
            FontStyle.DEFAULT,
            Color.DEFAULT,
        ),
        levelname_fontstyle: FontStyle = FontStyle.BOLD,
        level_style: Dict[Level, Tuple[Color, FontStyle, Color]] = {},
        frame_style: Tuple[Color, FontStyle, Color] = (
            Color.CYAN,
            FontStyle.DEFAULT,
            Color.DEFAULT,
        ),
    ) -> None:
        """ """
        # namedtuple for style definitions
        style = namedtuple("style", ["text_color", "font_style", "background_color"])

        # instance name style
        self.inst_name = style(*inst_name_style)

        # time part style
        self.time = style(*time_style)

        # styles for each level
        self.level: Dict[Level, Tuple] = {}

        # styles for line with module, function, line number
        self.frame = style(*frame_style)

        _trace_style = level_style.get(
            Level.TRACE, (Color.CYAN, FontStyle.BOLD, Color.DEFAULT)
        )
        self.level[Level.TRACE] = style(*_trace_style)

        _debug_style = level_style.get(
            Level.DEBUG, (Color.BLUE, FontStyle.BOLD, Color.DEFAULT)
        )
        self.level[Level.DEBUG] = style(*_debug_style)

        _info_style = level_style.get(
            Level.INFO, (Color.WHITE, FontStyle.BOLD, Color.DEFAULT)
        )
        self.level[Level.INFO] = style(*_info_style)

        _success_style = level_style.get(
            Level.SUCCESS, (Color.GREEN, FontStyle.BOLD, Color.DEFAULT)
        )
        self.level[Level.SUCCESS] = style(*_success_style)

        _warn_style = level_style.get(
            Level.WARNING, (Color.YELLOW, FontStyle.BOLD, Color.DEFAULT)
        )
        self.level[Level.WARNING] = style(*_warn_style)

        _error_style = level_style.get(
            Level.ERROR, (Color.RED, FontStyle.BOLD, Color.DEFAULT)
        )
        self.level[Level.ERROR] = style(*_error_style)

        _crit_style = level_style.get(
            Level.CRITICAL, (Color.MAGENTA, FontStyle.BOLD, Color.RED)
        )
        self.level[Level.CRITICAL] = style(*_crit_style)

        # style for level name
        self.levelname_fstyle = levelname_fontstyle.value
