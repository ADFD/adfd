from plumbum import LocalPath
import pytest
from adfd.adfd_parser import AdfdParser

from adfd.utils import ContentGrabber


class DataGrabber(ContentGrabber):
    DATA_PATH = LocalPath(__file__).up() / 'data'

    def __init__(self, relPath='.', absPath=None):
        super(DataGrabber, self).__init__(relPath, absPath)
        if not absPath:
            self.rootPath = self.DATA_PATH / relPath

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

    def get_boolean_tests(self, fName, good='good'):
        return [(l, good in l) for l in self.get_lines(fName)]

    def get_pairs(self):
        paths = [p for p in sorted(self.rootPath.list())]
        idx = 0
        contents = []
        while idx + 1 < len(paths):
            fName = paths[idx].basename
            src = self.grab(paths[idx])
            exp = self.grab(paths[idx + 1])
            contents.append((fName, src, exp))
            idx += 2
        return contents


class PairTester(object):
    @classmethod
    def test_pairs(cls, fName, src, exp):
        exp = exp.strip()
        if not exp:
            pytest.xfail(reason='no expectation for %s' % (fName))
        result = AdfdParser().format(src).strip()
        try:
            assert result == exp
        except AssertionError:
            p = DataGrabber.DATA_PATH / ('%s.html' % (fName))
            with open(str(p), 'w') as f:
                f.write(result.encode('utf8'))
            raise
