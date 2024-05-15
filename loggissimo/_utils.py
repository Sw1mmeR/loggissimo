import math
import shutil

import traceback
from typing import List

from .constants import END_LOGGER_TRACE, START_LOGGER_TRACE


def print_trace(ex: Exception, advice: str = "", line_char: str = "=") -> None:
    columns = shutil.get_terminal_size().columns

    half_start_columns = math.ceil((columns - len(START_LOGGER_TRACE)) / 2)
    half_end_columns = math.ceil((columns - len(END_LOGGER_TRACE)) / 2)

    start_trace_line = (
        line_char * half_start_columns
        + START_LOGGER_TRACE
        + line_char * half_start_columns
    )
    end_trace_line = (
        line_char * half_end_columns + END_LOGGER_TRACE + line_char * half_end_columns
    )

    for _ in range(columns):
        if len(start_trace_line) > columns:
            start_trace_line = start_trace_line[:-1]
        if len(end_trace_line) > columns:
            end_trace_line = end_trace_line[:-1]
        if len(end_trace_line) == columns and len(start_trace_line) == columns:
            break

    print(start_trace_line.center(columns), end="\n\n")
    traces = traceback.format_tb(ex.__traceback__)
    [print(trace) for trace in traces]
    print(ex)
    print(advice)
    print(end_trace_line.center(columns))


def get_module_combinations(input_string: str) -> List[str]:
    words = input_string.split(".")
    combinations = []
    current = ""
    for word in words:
        if current:
            current += "."
        current += word
        combinations.append(current)
    return combinations
