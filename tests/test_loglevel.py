import os
import pytest

from loggissimo import logger
from constants import TMP_DIR


@pytest.mark.parametrize(
    "loglevel,length",
    [
        ("CRITICAL", 1),
        ("ERROR", 2),
        ("WARNING", 3),
        ("SUCCESS", 4),
        ("INFO", 5),
        ("DEBUG", 6),
        ("TRACE", 7),
    ],
)
def test_loglevel(loglevel, length):
    logger.level = loglevel
    path = f"{TMP_DIR}/{loglevel}.log"
    logger.add(path)

    logger.critical("critical")
    logger.error("error")
    logger.warning("warning")
    logger.success("success")
    logger.info("info")
    logger.debug("debug")
    logger.trace("trace")

    with open(path, "r") as file:
        assert len(file.readlines()) == length

    os.remove(path)
