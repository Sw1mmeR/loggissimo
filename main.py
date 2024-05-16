#!/bin/python3
from enum import Enum, IntEnum
from multiprocessing import Process
from loggissimo import logger, Logger
from loggissimo.constants import Level
from loggissimo._colorizer import _colorize, _Colors, _FontStyle

from multipledispatch import dispatch  # type: ignore

# sys.path.append(
#     os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
# )


# logger.level = Level.DEBUG


def logs():
    logger.info("1")
    logger.debug("2")
    logger.critical("3")


# "<background=green><font=red>test</font></background>"
# def parse_tags(tag):
#     tag_name = tag[1 : tag.find("=")]
#     tag_value = tag[tag.find("=") + 1 : tag.find(">")]
#     tag_text = tag[tag.find(">") + 1 : -7]
#     return tag_name, tag_value, tag_text


# def parse_tags(text):
#     tags = []
#     start_tag = "<"
#     end_tag = ">"

#     current_index = 0
#     while current_index < len(text):
#         tag = {}

#         open_tag_start = text.find(start_tag, current_index)
#         if open_tag_start == -1:
#             break

#         open_tag_end = text.find(end_tag, open_tag_start)
#         tag_name_value = text[open_tag_start + 1 : open_tag_end].split("=")

#         tag["tag_name"] = tag_name_value[0]
#         tag["value"] = tag_name_value[1].strip('"')

#         close_tag_start = text.find(start_tag + "/" + tag["tag_name"], open_tag_end)
#         if close_tag_start == -1:
#             break

#         tag["text"] = text[open_tag_end + 1 : close_tag_start]

#         tags.append(tag)
#         current_index = close_tag_start + len(tag["tag_name"]) + 3

#     return tags


def parse_tags(tag):
    tag_name = tag[1 : tag.find("=")]
    tag_value = tag[tag.find("=") + 1 : tag.find(">")]
    tag_text = tag[tag.find(">") + 1 : -len(tag_name) - 3]
    return tag_name, tag_value, tag_text


def parse_nested_tags(text):
    stack = []
    result = []
    current_tag = ""
    for char in text:
        if char == "<":
            if current_tag:
                stack.append(current_tag)
            current_tag = "<"
        elif char == ">":
            current_tag += ">"
            stack.append(current_tag)
            current_tag = ""
        else:
            current_tag += char

    for tag in stack:
        if tag.startswith("<"):
            result.append(parse_tags(tag))
        else:
            result[-1] = (result[-1][0], result[-1][1], result[-1][2] + tag)

    return result


class Color(Enum):
    black = (0, 30)
    red = (0, 31)
    green = (0, 32)
    yellow = (0, 33)
    blue = (0, 34)
    purple = (0, 35)
    cyan = (0, 36)
    gray = (0, 37)


ESCAPE_FONT = 38
ESCAPE_BACKGROUND = 48


class Colorizer:

    def __init__(self) -> None:
        pass

    @staticmethod
    @dispatch(str, Color)
    def font(text: str, color: Color) -> str:
        pass

    @dispatch(str, int, int, int)  # type: ignore
    @staticmethod
    def font(text: str, r: int, g: int, b: int, end="") -> str:
        return f"\033[{ESCAPE_FONT};2;{r};{g};{b}m{text}{end}"  # \033[0m

    @dispatch(str, Color)
    @staticmethod
    def background(text: str, color: Color):
        pass

    @dispatch(str, int, int, int)  # type: ignore
    @staticmethod
    def background(text: str, r: int, g: int, b: int, end=""):
        return f"\033[{ESCAPE_BACKGROUND};2;{r};{g};{b}m{text}{end}"  # \033[0m


def main():
    # tag = "<background=green><font=red>Hello, World!</font></background>"
    # tag_name, tag_value, tag_text = parse_tags(tag)
    # print("Tag Name:", tag_name)
    # print("Tag Value:", tag_value)
    # print("Tag Text:", tag_text)
    # Пример использования

    # print("\033[38;2;142;222;212mHello World!")
    font = Colorizer.font("Hello", 242, 255, 22, end="") + Colorizer.font(
        "World", 15, 2, 123
    )

    print(font)

    back = Colorizer.background(font, 255, 255, 255)
    print(back)
    print("test")
    print("test")
    print("test")

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
