#!/bin/python3
from enum import Enum, IntEnum
from multiprocessing import Process
import os
import re
import sys
from typing import Any, Dict, List
# from loggissimo import logger, Logger
# from loggissimo.constants import Level

from multipledispatch import dispatch

from loggissimo.colorizer.colorizer import Style, rgb

# from loggissimo import Color, Colorizer, Style  # type: ignore

# sys.path.append(
#     os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
# )


# logger.level = Level.DEBUG

from loggissimo.colorizer import red, black, blue, Color


class Tag:
    def __init__(self, name: str, value: str, text: str = "") -> None:
        self.name = name
        self.value = value
        self._closed = False
        self.text = text

    @property
    def closed(self) -> bool:
        return self._closed
    
    @closed.setter
    def closed(self, value: bool) -> None:
        self._closed = value

    def __repr__(self) -> str:
        return str({'name': self.name, 'value': self.value, 'text': self.text, 'closed': self.closed})
    
    def __str__(self) -> str:
        return f"{self.name}={self.value}"

def parse_tags(tag):
    tag_name = tag[1:tag.find('=')]
    tag_value = tag[tag.find('=')+1:tag.find('>')]
    tag_text = tag[tag.find('>')+1:-len(tag_name)-3]
    return tag_name, tag_value, tag_text

def parse_nested_tags(text):
    stack = []
    result = []
    current_tag = ""
    for char in text:
        if char == '<':
            if current_tag:
                stack.append(current_tag)
            current_tag = char
        elif char == '>':
            current_tag += char
            if current_tag.startswith("</"):
                print("curr", current_tag[2:-1])
                print("stack", stack)
                closing_tag = current_tag[2:-1]
                while stack and not stack[-1].endswith(closing_tag):
                    result.append((result[-1][0], result[-1][1], result[-1][2] + stack.pop()))
                    # stack.pop()
                    print("res", result)
                if stack and stack[-1].endswith(closing_tag):
                    if result:
                        result[-1] = (result[-1][0], result[-1][1], result[-1][2] + stack.pop())
                    else:
                        stack.pop()
                    if not stack:
                        break
                else:
                    pass
                    # print("Missing closing tag: </{}>".format(closing_tag))
                    # raise Exception("Missing closing tag: </{}>".format(closing_tag))
            else:
                stack.append(current_tag)
            current_tag = ""
        else:
            current_tag += char
        # print(stack)

    if len(stack) > 0:
        raise Exception("Unclosed tags: {}".format(stack))

    for tag in stack:
        if tag.startswith("<"):
            result.append(parse_tags(tag))
        else:
            result[-1] = (result[-1][0], result[-1][1], result[-1][2] + tag)

    return result

# def parse_tag_value(tags: Dict[str, Tag], tag_str, closing, inner_text):
#     tag = tag_str.strip(">/<")
#     if closing:
#         current_tag = tags.get(tag, None)
#         if not current_tag:
#             raise KeyError(f"No openning tag for {tag}")
#         tags[tag].closed = True
#         return
#     if "=" not in tag:
#         raise ValueError(f"Can't find value. {tag}")
#     tag_name, value = tag.split("=")
#     tags[tag_name] = Tag(tag_name, value, inner_text)
#     return tag_name

# def parse_tags(text: str):
#     tags: Dict[str, Tag] = dict()
#     tag = ""
#     inner_text = ""
#     closing = False
#     for ch in text:
#         if inner_text:
#             print("pre", inner_text)
#             inner_text += ch
#             print("appended:", inner_text)

#         if ch == "<":
#             tag = ch
#         elif ch == ">":
#             if tag:
#                 tag += ch
#                 tag_name = parse_tag_value(tags, tag, closing, inner_text)
#                 inner_text = "."
#         elif ch == "/":
#             closing = True
#             tag += ch
#         else:
#             if tag:
#                 tag += ch
#         print(tag)
#         print(inner_text)
#     return tags

def main():
    text = "<bg=red><font=green>Hello </font></bg><font=blue>World!</font>"
    tags = parse_nested_tags(text)
    print(tags)
    for tag in tags:
        print(tag[2], "font =", tag[0], ", bg =", tag[1])
    # red("red")
    # black("black")
    # blue("blue")
    # print(rgb("hi"))
    # print(rgb("Hello World", 155, 150, 15, Style.Underline))
    # print()
    # # text = "<background=green><font=red>Hello, World!</font></background>"
    # text = "<font=yellow><bg=red>Hello, World!</bg></font>"
    # # colors = '|'.join(['.' + color.name[1:] for color in Color])
    # # regul = r"(\<font=.*\>).*"
    # # print(regul)
    # # res = re.findall(regul, text)
    # print(parse_tags(text))
    # print(parse_nested_tags(text))
    # print(text.find("<>"))
    # tag = "<background=green><font=red>Hello, World!</font></background>"
    # tag_name, tag_value, tag_text = parse_tags(tag)
    # print("Tag Name:", tag_name)
    # print("Tag Value:", tag_value)
    # print("Tag Text:", tag_text)
    # Пример использования

    # print("\033[38;2;142;222;212mHello World!")
    # cl = Colorizer()
    # print()
    # Colorizer.Red("test")
    # Colorizer.colorize("test", Color.Red)
    # Colorizer.Green("tesxt")
    # print(cl.green("test"))
    # print(cl.red("t"))
    # print(Colorizer.font("test2", Color.Green))
    # print("testtest")
    # print("testtest")
    # print(Colorizer.background("Hello", Color.Blue))
    # print(Colorizer.font("Hello World!", Color.Black, Style.Blink))
    # print("testtest")
    # print("testtest")

    # font = Colorizer.font("Hello", 242, 255, 22, end="") + Colorizer.font(
    #     "World", 15, 2, 123
    # )

    # print(font)

    # back = Colorizer.background(font, 255, 255, 255)
    # print(back)
    # print("test")
    # print("test")
    # print("test")

    # Colorizer.font(Color.red)

    # text = "<background=green><font=red>Hello, World!</font></background>"
    # tags = parse_nested_tags(text)
    # for tag in tags:
    #     print("Tag Name:", tag[0])
    #     print("Tag Value:", tag[1])
    #     print("Tag Text:", tag[2])

    # text = (
    #     "<background=green><font=red>Hello</font><font=blue>World</font></background>"
    # )
    # parsed_tags = parse_tags(text)

    # for tag in parsed_tags:
    #     print(tag)
    # print(_colorize("test msg", _Colors.BLACK, _FontStyle.BOLD, _Colors.BLUE))
    # Logger.addall("test.log")
    # logger.level = "DEBUG"
    # proc = Process(target=logs, name="Access Point 212")
    # proc.start()
    # proc.join()
    # logger.info("test1")
    # logger.destructor("test")
    # log1 = Logger("my_logger")

    # log2 = Logger("my_logger2")

    # # logger.add("my_test.log")
    # log1.info("test")
    # logger.debug("test2")
    # log2.critical("Test")

    # for st in logger._streams.values():
    #     print(st.closed)

    # del log1

    # log1 = Logger("my_logger")
    # print()
    # print(Logger._aggregated_streams["test.log"].closed)
    # for st in logger._streams.values():
    #     print(st.closed)

    # log1.info("end")
    # log1.info("end")
    # log1.info("end")
    # log1.info("end")

    # del log1

    # log1 = Logger("test1")
    # log1.info("!!!!!!!!!!!")


if __name__ == "__main__":
    main()
