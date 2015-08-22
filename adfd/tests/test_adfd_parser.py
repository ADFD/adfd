from plumbum import LocalPath
import pytest
from adfd.adfd_parser import AdfdParser


def get_pairs():
    cnt = LocalPath(__file__).up() / 'data' / 'pairs'
    paths = [p for p in sorted(cnt.list())]
    idx = 0
    contents = []
    while idx + 1 < len(paths):
        fName = paths[idx].basename
        src = paths[idx].read('utf-8')
        exp = paths[idx + 1].read('utf-8')
        contents.append((fName, src, exp))
        idx += 2
    return contents


class TestAdfdParser(object):
    @pytest.mark.parametrize("fName,src,exp", get_pairs())
    def test_pairs(self, fName, src, exp):
        print fName
        parser = AdfdParser()
        result = parser.format(src)
        assert result.strip() == exp.strip()
