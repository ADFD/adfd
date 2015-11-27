import os

import pytest

from adfd.cst import DB_URL
from adfd.db.export import export


def is_running_in_ci():
    """NOTE:
    needed in tox.ini:

        [testenv]
        passenv = CI
    """
    return os.getenv("CI") is not None


def test_db_connection_sets_encoding():
    """This has bitten me and it's not in VCS, so I check it here"""
    assert DB_URL.endswith('?charset=utf8')


@pytest.mark.skipif("is_running_in_ci()")
def test_export():
    # if this runs through everything is considered fine
    export()
