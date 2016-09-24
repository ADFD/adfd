import logging

import pytest
from adfd.parse import AdfdParser
from adfd.utils import DataGrabber

log = logging.getLogger(__name__)


class PairTester:
    _parser = AdfdParser(typogrify=False, hyphenate=False)

    @classmethod
    def test_pairs(cls, fName, src, exp):
        exp = exp.strip()
        if not exp:
            pytest.xfail(reason='no expectation for %s' % fName)
        log.info("file under test is %s", fName)
        html = cls._parser.to_html(src)
        print("\n## RESULT ##")
        print(html)
        print("\n## EXPECTED ##")
        print(exp)
        refPath = DataGrabber.DATA_PATH / ('%s.html' % (fName[:-7]))
        try:
            assert html == exp
            refPath.delete()
        except AssertionError:
            with open(str(refPath), 'w') as f:
                f.write(html)
            raise


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
