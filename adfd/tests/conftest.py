import logging
import pytest


@pytest.fixture(autouse=True)
def init_tests():
    logging.basicConfig(level=logging.DEBUG)
