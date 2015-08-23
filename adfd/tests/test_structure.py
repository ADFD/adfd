import pytest
import yaml

from plumbum import LocalPath
from testutils import DataGrabber


@pytest.mark.xfail(reason='WIP')
class TestStructure(object):
    def test_tree(self):
        path = LocalPath(__file__).up(3) / 'content' / 'structure.yml'
        dg = DataGrabber(absPath=path)
        # use safe_load instead load
        dataMap = yaml.safe_load(dg.grab())
        print dataMap
        assert 0
