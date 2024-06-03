import os
import time
import pytest

from typing import Callable
from loggissimo import logger

from package.module1.functions import do_module1
from package.module2.submodule1.functions import do_module2_sub1
from package.module2.submodule2 import do_module2_sub2

from constants import TMP_DIR


@pytest.fixture(params=[do_module1, do_module2_sub1, do_module2_sub2])
def get_function(request):
    yield request.param


@pytest.mark.parametrize("enabled", [False, True])
def test_logger_enable(get_function: Callable, enabled: bool):
    print(enabled)
    if enabled:
        logger.enable(get_function.__module__)

    path = f"{TMP_DIR}/enabled_{enabled}_{get_function.__name__}.log"

    logger.add(path)
    get_function()

    with open(path, "r") as file:
        line = file.readlines()

    assert bool(line) == enabled, logger._streams

    os.remove(path)
