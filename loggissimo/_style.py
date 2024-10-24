import re
from string import Template
from typing import Callable, Dict, List

from loggissimo.constants import Level
from colorcall import Color, FontStyle, rgb, basic


level_colors_rgb = {
    Level.INFO: [(255, 255, 255), (-1, -1, -1)],
    Level.SUCCESS: [(40, 170, 90), (-1, -1, -1)],
    Level.WARNING: [(225, 255, 0), (-1, -1, -1)],
    Level.ERROR: [(255, 50, 50), (-1, -1, -1)],
    Level.CRITICAL: [
        (0, 0, 0),
        (255, 0, 20),
    ],
    Level.DEBUG: [(20, 100, 250), (-1, -1, -1)],
    Level.TRACE: [(1, 210, 255), (-1, -1, -1)],
    Level.DELETE: [(85, 90, 120), (-1, -1, -1)],
}

level_colors_basic = {
    Level.INFO: [Color.white, Color.default],
    Level.SUCCESS: [Color.green, Color.default],
    Level.WARNING: [Color.yellow, Color.default],
    Level.ERROR: [Color.red, Color.default],
    Level.CRITICAL: [
        Color.black,
        Color.red,
    ],
    Level.DEBUG: [Color.blue, Color.default],
    Level.TRACE: [Color.cyan, Color.default],
    Level.DELETE: [Color.purple, Color.default],
}


def style(
    format: str,
    level: Level,
    basic_colors: bool = False,
    only_remove_tags: bool = False,
) -> str:
    style_format = re.findall(
        r"(\<.*?>).*?(\$\w*)",
        format,
    )
    callback: Callable = basic if basic_colors else rgb  # type: ignore
    level_colors: Dict[Level, tuple] = (
        level_colors_basic if basic_colors else level_colors_rgb  # type: ignore
    )
    styled: Dict[str, str] = {
        "name": callback(
            "$name",
            Color.yellow if basic_colors else (255, 208, 5),
            style=FontStyle.italic,
        ),
        "time": callback("$time", Color.green if basic_colors else (40, 115, 40)),
        "level": callback(
            "$level",
            level_colors[level][0],
            bgcolor=level_colors[level][1],
            style=FontStyle.bold,
        ),
        "stack": callback(
            "$stack",
            Color.cyan if basic_colors else (20, 100, 110),
            style=FontStyle.underline,
        ),
        "text": callback(
            "$text",
            level_colors[level][0],
            bgcolor=level_colors[level][1],
            style=FontStyle.bold,
        ),
    }

    for style, value in style_format:
        format = format.replace(style, "")
        tag = Tag(style, value)
        styled[value[1:]] = tag.colorized

    if only_remove_tags:
        return format

    return Template(format).safe_substitute(**styled)


class Tag:
    def __init__(self, tag: str, text: str, *args, **kwargs) -> None:
        def rgb_str2int(rgb_str: str) -> List[int]:
            color_rgb_str = rgb_str.split(",")
            color_rgb = [int(number) for number in color_rgb_str]
            return color_rgb

        self.values: Dict[str, str] = dict()
        self.text = text
        if tag:
            splitted = tag.split(" ")
            for raw_tag in splitted:
                key_val = raw_tag.split("=")
                key = key_val[0].lstrip("<")
                self.values[key] = key_val[1].rstrip(">")

            self.font_color = self.values.get("font", "")
            self.bg_color = self.values.get("bg", "")
            self.style = getattr(FontStyle, self.values.get("style", "default"))

            font = (255, 255, 255)
            bg = (-1, -1, -1)
            try:
                if self.font_color:
                    font = rgb_str2int(self.font_color)  # type: ignore

                if self.bg_color:
                    bg = rgb_str2int(self.bg_color)  # type: ignore

                self.colorized = rgb(self.text, font, bg, self.style)
            except:
                self.colorized = basic(
                    self.text,
                    getattr(Color, self.font_color),
                    getattr(Color, self.bg_color, Color.default),
                    self.style,
                )

    def __str__(self) -> str:
        return self.colorized

    def __repr__(self) -> str:
        _repr = "<"
        for key, val in self.values.items():
            _repr += f"{key}={val} "
        return _repr.rstrip(" ") + ">"
