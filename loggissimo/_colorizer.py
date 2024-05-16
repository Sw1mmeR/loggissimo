from datetime import datetime
from enum import Enum
from string import Template
from typing import Optional


# Colors and styles codes
class _Colors(Enum):
    """
    Codes for text colors
    """

    BLACK = "30"
    RED = "31"
    GREEN = "32"
    YELLOW = "33"
    BLUE = "34"
    MAGENTA = "35"
    CYAN = "36"
    WHITE = "37"
    DEFAULT = ""

    def __str__(self) -> str:
        return self.value


class _FontStyle(Enum):
    """
    Font styles for text
    """

    BOLD = "1"
    FADED = "2"
    ITALIC = "3"
    UNDERLINE = "4"
    DEFAULT = ""

    def __str__(self) -> str:
        return self.value


def _colorize(
    text: str,
    color: _Colors = _Colors.DEFAULT,
    style: _FontStyle = _FontStyle.DEFAULT,
    background: _Colors = _Colors.DEFAULT,
) -> str:
    """
    Colorize text and return it

    Args:
        text: str - text for colorizing;
        color: Optional[_Colors] - Color for text;
        style: Optional[_FontStyle] - Font style for text;
    Return:
        str - colorized and styled text
    """
    back: int | str = ""
    if str(background.value):
        back = int(background.value) + 10

    code = ""
    if color != style != back:
        code = f"\u001b[{style}{';' if color and style or style and back else ''}{color}{';' if color and back else ''}{back}m"

    ender = "\u001b[0m"
    return f"{code}{text}{ender}"


def colorize(
    name: str,
    time: str | datetime,
    levelname: str,
    frame_line: str,
    message: str,
    template: Template,
) -> str:
    name = _colorize(
        f"{name:24}",
        self._style.inst_name.text_color.value,
        self._style.inst_name.font_style.value,
        self._style.inst_name.background_color.value,
    )
    return template.safe_substitute(
        name=name, time=time, level=levelname, frame=frame_line, message=message
    )
