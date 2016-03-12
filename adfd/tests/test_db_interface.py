import os

import pytest

from adfd.db.lib import RawTopicsExporter
from adfd.db.phpbb_classes import Topic


def is_running_in_ci():
    """NOTE:
    needed in tox.ini:

        [testenv]
        passenv = CI
    """
    return os.getenv("CI") is not None


@pytest.mark.skipif("is_running_in_ci()")
def test_topic_export():
    # if this runs through everything is considered fine
    RawTopicsExporter([Topic(68)]).export()
