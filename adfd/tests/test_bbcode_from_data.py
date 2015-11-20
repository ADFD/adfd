import pytest

from adfd.bbcode import AdfdParser
from adfd.utils import DataGrabber, PairTester


class TestAdfdParser(object):
    ACCEPTANCE_PAIRS = DataGrabber('acceptance').get_pairs()
    TRANSFORM_PAIRS = DataGrabber('transform').get_pairs()

    @pytest.mark.parametrize("fName,src,exp", TRANSFORM_PAIRS)
    def test_transform_pairs(self, fName, src, exp):
        PairTester.test_pairs(fName, src, exp)

    @pytest.mark.parametrize("fName,src,exp", ACCEPTANCE_PAIRS)
    def test_acceptance_pairs(self, fName, src, exp):
        PairTester.test_pairs(fName, src, exp)

    # # noinspection PyUnusedLocal
    # @pytest.mark.parametrize("fName,src,exp", ACCEPTANCE_PAIRS)
    # def test_different_call_options(self, fName, src, exp):
    #     print(fName)
    #     dataFromInit = AdfdParser(data=src).to_html()
    #     dataFromCall = AdfdParser().to_html(src)
    #     assert dataFromInit == dataFromCall
