import pytest

from testutils import PairTester
from adfd.utils import DataGrabber
from adfd.adfd_parser import AdfdParser


class TestAdfdParser(object):
    ACCEPTANCE_PAIRS = DataGrabber('acceptance').get_pairs()
    WRAPPING_PAIRS = DataGrabber('wrapping').get_pairs()

    @pytest.mark.parametrize("fName,src,exp", WRAPPING_PAIRS)
    def test_p_wrap_pairs(self, fName, src, exp):
        PairTester.test_pairs(fName, src, exp)

    @pytest.mark.parametrize("fName,src,exp", ACCEPTANCE_PAIRS)
    def test_acceptance_pairs(self, fName, src, exp):
        PairTester.test_pairs(fName, src, exp)

    # noinspection PyUnusedLocal
    @pytest.mark.parametrize("fName,src,exp", ACCEPTANCE_PAIRS)
    def test_different_call_options(self, fName, src, exp):
        print(fName)
        dataFromInit = AdfdParser(data=src).to_html()
        dataFromCall = AdfdParser().to_html(src)
        assert dataFromInit == dataFromCall