import pytest

from adfd.utils import DataGrabber, PairTester


class TestAdfdParser(object):
    ACCEPTANCE_PAIRS = DataGrabber('acceptance').get_pairs()
    TRANSFORM_PAIRS = DataGrabber('transform').get_pairs()

    @pytest.mark.parametrize("fName,src,exp", TRANSFORM_PAIRS)
    def test_transform_pairs(self, fName, src, exp):
        PairTester.test_pairs(fName, src, exp)

    @pytest.mark.parametrize("fName,src,exp", ACCEPTANCE_PAIRS)
    def test_acceptance_pairs(self, fName, src, exp):
        if fName in ['nested-quotes.bb']:
            pytest.xfail('nested quuotes is tricky and of qquestionable use')
        PairTester.test_pairs(fName, src, exp)
