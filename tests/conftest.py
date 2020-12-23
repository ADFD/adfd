import logging

import pytest


@pytest.fixture(scope="session", autouse=True)
def init_tests():
    logging.basicConfig(level=logging.INFO)
