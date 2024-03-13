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
              color: Optional[_Colors] = None, 
              style: Optional[_FontStyle] = None) -> str:
    """
    Colorize text and return it

    Args:
        text: str - text for colorizing;
        color: Optional[_Colors] - Color for text;
        style: Optional[_FontStyle] - Font style for text;
    Return:
        str - colorized and styled text
    """
    _color = color if color else ""
    _style = style if style else ""
    code = "" if _color == _style else f"\u001b[{_style};{_color}m"
    ender = "\u001b[0m"
    return f"{code}{text}{ender}"