import logging

import pytest

from adfd.cnf import PATH
from adfd.parse import ADFD_PARSER
from adfd.process import ContentGrabber

log = logging.getLogger(__name__)


class DataGrabber(ContentGrabber):
    DATA_PATH = PATH.PROJECT / "tests" / "data"

    def __init__(self, path):
        super().__init__(self.DATA_PATH / path)

    def get_chunks(self, fName):
        """separates chunks separated by empty lines

        :returns: list of list of str
        """
        chunks = []
        currentChunkLines = []
        for line in self.get_lines(fName):
            if line:
                currentChunkLines.append(line)
            else:
                chunks.append(currentChunkLines)
                currentChunkLines = []
        return chunks

    def get_boolean_tests(self, fName, good="good"):
        return [(line, good in line) for line in self.get_lines(fName)]

    def get_pairs(self):
        paths = [p for p in sorted(self.path.list())]
        idx = 0
        contents = []
        while idx + 1 < len(paths):
            fName = paths[idx].basename
            src = self.grab(paths[idx])
            exp = self.grab(paths[idx + 1])
            contents.append((fName, src, exp))
            idx += 2
        return contents


@pytest.mark.parametrize("fName,src,exp", DataGrabber("transform").get_pairs())
def test_transform_pairs(fName, src, exp):
    compare_results(fName, src, exp)


@pytest.mark.parametrize("fName,src,exp", DataGrabber("acceptance").get_pairs())
def test_acceptance_pairs(fName, src, exp):
    if fName in ["nested-quotes.bbcode"]:
        pytest.xfail("nested quotes is tricky and of questionable use")
    compare_results(fName, src, exp)


def compare_results(fName, src, exp):
    exp = exp.strip()
    if not exp:
        pytest.xfail(reason=f"no expectation for {fName}")

    log.info("file under test is %s", fName)
    html = ADFD_PARSER.to_html(src)
    print("\n## RESULT ##")
    print(html)
    print("\n## EXPECTED ##")
    print(exp)
    refPath = DataGrabber.DATA_PATH / ("%s.html" % (fName[:-7]))
    try:
        assert html == exp
        refPath.delete()
    except AssertionError:
        with open(str(refPath), "w") as f:
            f.write(html)
        raise
