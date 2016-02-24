import pytest

from adfd.tests.utils import PairTester
from adfd.utils import DataGrabber


class TestFromDataAcceptance:
    ACCEPTANCE_PAIRS = DataGrabber('acceptance').get_pairs()
    TRANSFORM_PAIRS = DataGrabber('transform').get_pairs()

    @pytest.mark.parametrize("fName,src,exp", TRANSFORM_PAIRS)
    def test_transform_pairs(self, fName, src, exp):
        PairTester.test_pairs(fName, src, exp)

    @pytest.mark.parametrize("fName,src,exp", ACCEPTANCE_PAIRS)
    def test_acceptance_pairs(self, fName, src, exp):
        if fName in ['nested-quotes.bbcode']:
            pytest.xfail('nested quuotes is tricky and of qquestionable use')
        PairTester.test_pairs(fName, src, exp)


# fixme provide directory with fakefiles, when stable
# class TestPage:
#     def test_metadata(self):
#         p = Page(689)
#         print(obj_attr(p))
