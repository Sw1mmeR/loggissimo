import re
import os
import time
import pytest

from typing import Final
from random import randint
from threading import Thread
from multiprocessing import Process

from loggissimo import Logger
from constants import TMP_DIR

PROC_COUNT: Final[int] = 25

LOGGER_NAME: Final[str] = "log-"
PROCESS_NAME: Final[str] = "proc-"


def target(name: str):
    log = Logger(name)
    log.add(f"{TMP_DIR}/{name}.log")

    log.info(f"Target {name} start")
    time.sleep(randint(1, 3))
    log.success(f"Target {name} exit")


@pytest.mark.parametrize("ProcTh", [(Process), (Thread)])
def test_process(ProcTh: Process | Thread):
    processes = [
        ProcTh(  # type: ignore
            target=target,
            args=(f"{LOGGER_NAME}{_}",),
            daemon=True,
            name=f"{PROCESS_NAME}{_}",
        )
        for _ in range(PROC_COUNT)
    ]
    [proc.start() for proc in processes]
    [proc.join() for proc in processes]

    for _ in range(PROC_COUNT):
        path = f"{TMP_DIR}/{LOGGER_NAME}{_}.log"
        try:
            with open(path, "r") as file:
                find = re.findall(
                    rf"{LOGGER_NAME}[0-9]+\s*\({PROCESS_NAME}[0-9]+\)",
                    " ".join(file.readlines()),
                )
                print(find)

            assert find, f"Can't find processes line in file {path}"
        finally:
            os.remove(path)
