from bs4 import BeautifulSoup
import pytest

from adfd.adfd_parser import AdfdParser
from adfd.utils import DataGrabber


class PairTester(object):
    @classmethod
    def test_pairs(cls, fName, src, exp):
        exp = exp.strip()
        if not exp:
            pytest.xfail(reason='no expectation for %s' % (fName))
        result = AdfdParser(data=src).to_html()
        soup = BeautifulSoup(result, "lxml")
        result = soup.prettify()
        try:
            assert result == exp
        except AssertionError:
            p = DataGrabber.DATA_PATH / ('%s.html' % (fName))
            with open(str(p), 'w') as f:
                f.write(result.encode('utf8'))
            raise
