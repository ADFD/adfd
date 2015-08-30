import pytest

from testutils import DataGrabber, PairTester


class TestAdfdParser(object):
    ACCEPTANCE_PAIRS = DataGrabber('acceptance').get_pairs()
    P_WRAP_PAIRS = DataGrabber('p-wrap').get_pairs()

    @pytest.mark.parametrize("fName,src,exp", P_WRAP_PAIRS)
    def test_p_wrap_pairs(self, fName, src, exp):
        PairTester.test_pairs(fName, src, exp)

    @pytest.mark.parametrize("fName,src,exp", ACCEPTANCE_PAIRS)
    def test_acceptance_pairs(self, fName, src, exp):
        PairTester.test_pairs(fName, src, exp)
