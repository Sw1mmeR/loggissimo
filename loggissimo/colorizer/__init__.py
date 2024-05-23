from loggissimo.colorizer.colorizer import Color, Style, _cprint, basic, rgb

def black(text: str) -> None:
    _cprint(text, Color.Black)

def red(text: str) -> None:
    _cprint(text, Color.Red)

def green(text: str) -> None:
    _cprint(text, Color.Green)

def yellow(text: str) -> None:
    _cprint(text, Color.Yellow)

def blue(text: str) -> None:
    _cprint(text, Color.Blue)

def purple(text: str) -> None:
    _cprint(text, Color.Purple)

def cyan(text: str) -> None:
    _cprint(text, Color.Cyan)

def white(text: str) -> None:
    _cprint(text, Color.White)
