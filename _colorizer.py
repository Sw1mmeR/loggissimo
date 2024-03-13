from enum import Enum
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
    CYAN    = "36"
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

def _colorize(text: str,
              color: _Colors = _Colors.DEFAULT, 
              style: _FontStyle = _FontStyle.DEFAULT,
              background: _Colors = _Colors.DEFAULT) -> str:
    """
    Colorize text and return it

    Args:
        text: str - text for colorizing;
        color: Optional[_Colors] - Color for text;
        style: Optional[_FontStyle] - Font style for text;
    Return:
        str - colorized and styled text
    """
    # Определяем коды
    _color = color
    _style = style
    if background.value:
        _back = int(str(background)) + 10
    else:
        _back = ""

    # cобираем открывающий код
    code = "" 
    if _color != _style != _back:
        first = ''
        second = ''
        if _color and _style or _style and _back:
            first = ';'
        if _color and _back:
            second = ';'
        code = f"\u001b[{_style}{first}{_color}{second}{_back}m"

    ender = "\u001b[0m"
    return f"{code}{text}{ender}"