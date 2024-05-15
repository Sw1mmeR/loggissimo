import os
import pytest

from constants import TMP_DIR


@pytest.fixture(scope="session", autouse=True)
def create_test_dirs():
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)
