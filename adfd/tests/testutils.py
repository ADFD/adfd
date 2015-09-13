from bs4 import BeautifulSoup
import pytest

from adfd.processing import AdfdProcessor
from adfd.utils import DataGrabber


class PairTester(object):
    @classmethod
    def test_pairs(cls, fName, src, exp):
        exp = exp.strip()
        if not exp:
            pytest.xfail(reason='no expectation for %s' % (fName))
        print(fName)
        result = AdfdProcessor(text=src).process()
        result = BeautifulSoup(result, "lxml").prettify()
        refPath = DataGrabber.DATA_PATH / ('%s.html' % (fName))
        try:
            assert result == exp
            refPath.delete()
        except AssertionError:
            with open(str(refPath), 'w') as f:
                f.write(result.encode('utf8'))
            raise
