import sys
from enum import IntEnum

class Color(IntEnum):
    Black = 0
    Red = 1
    Green = 2
    Yellow = 3
    Blue = 4
    Purple = 5
    Cyan = 6
    White = 7


class Style(IntEnum):
    Default = 0
    Bold = 1
    Dim = 2
    Italic = 3
    Underline = 4
    Blink = 5
    Reverse = 7
    Hide = 8

def _cprint(text: str, color: Color) -> None:
    sys.stdout.write(basic(text, color, end="\n"))

def basic(text: str, color: Color, style: Style = Style.Default, end="") -> str:
    return f"\x1b[{style};3{color.value}m{text}{end}\x1b[{style.Default}m"

def rgb(text: str, r: int = 255, g: int = 255, b: int = 255, style: Style = Style.Default, end=""):
    return f"\x1b[{style};38;2;{r};{g};{b}m{text}{end}\x1b[{Style.Default}m"
    