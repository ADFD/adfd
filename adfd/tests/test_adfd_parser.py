import pytest

from adfd.adfd_parser import AdfdParser
from testutils import DataGrabber


class TestAdfdParser(object):
    @pytest.mark.parametrize("fName,src,exp", DataGrabber('pairs').get_pairs())
    def test_pairs(self, fName, src, exp):
        if not exp:
            pytest.xfail(reason='no expectation set for %s yet' % (fName))
        parser = AdfdParser()
        result = parser.format(src)
        assert result.strip() == exp.strip()
