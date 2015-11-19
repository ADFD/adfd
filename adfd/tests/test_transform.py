import pytest

from adfd.utils import DataGrabber, PairTester


class TestAdfdParser(object):
    TRANSFORMATION_PAIRS = DataGrabber('transform').get_pairs()

    @pytest.mark.parametrize("fName,src,exp", TRANSFORMATION_PAIRS)
    def test_wrapping_pairs(self, fName, src, exp):
        PairTester.test_pairs(fName, src, exp)
