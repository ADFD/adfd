import pytest

from testutils import PairTester
from adfd.utils import DataGrabber


class TestAdfdParser(object):
    ACCEPTANCE_PAIRS = DataGrabber('acceptance').get_pairs()
    WRAPPING_PAIRS = DataGrabber('wrapping').get_pairs()

    @pytest.mark.parametrize("fName,src,exp", WRAPPING_PAIRS)
    def test_p_wrap_pairs(self, fName, src, exp):
        PairTester.test_pairs(fName, src, exp)

    @pytest.mark.parametrize("fName,src,exp", ACCEPTANCE_PAIRS)
    def test_acceptance_pairs(self, fName, src, exp):
        PairTester.test_pairs(fName, src, exp)
