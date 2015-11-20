import pytest
from bs4 import BeautifulSoup
from plumbum import LocalPath

from adfd.bbcode import AdfdParser
from adfd.processing import AdfdProcessor


class ContentGrabber(object):
    def __init__(self, relPath='.', absPath=None):
        if absPath:
            self.rootPath = absPath
        else:
            self.rootPath = LocalPath(__file__).up(2) / relPath

    def get_lines(self, fName):
        """get lines as list from file (without empty element at end)"""
        return self.strip_whitespace(self.get_text(fName))

    def get_text(self, fName, ext='.bb'):
        return self.grab(self.rootPath / (fName + ext))

    def grab(self, path=None):
        path = path or self.rootPath
        return path.read('utf-8')

    def strip_whitespace(self, content):
        """lines stripped of surrounding whitespace and last empty line"""
        lines = [t.strip() for t in content.split('\n')]
        if not lines[-1]:
            lines.pop()
        return lines


class ContentDumper(object):
    def __init__(self, path, content):
        self.path = path
        self.content = content

    def dump(self):
        self.path.write(self.content, encoding='utf-8')


class DataGrabber(ContentGrabber):
    DATA_PATH = LocalPath(__file__).up() / 'tests' / 'data'

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
    _parser = AdfdParser()

    @classmethod
    def test_pairs(cls, fName, src, exp):
        exp = exp.strip()
        if not exp:
            pytest.xfail(reason='no expectation for %s' % (fName))
        print(fName)
        # rawHtml = AdfdProcessor(text=src).process()
        rawHtml = cls._parser.to_html(src)
        print("\n## RAW ##")
        print(rawHtml)
        prettified = BeautifulSoup(rawHtml, "html.parser").prettify()
        print("\n## PRETTIFIED ##")
        print(prettified)
        print("\n## EXPECTED ##")
        print(exp)
        refPath = DataGrabber.DATA_PATH / ('%s.html' % (fName))
        try:
            if prettified != exp:
                pytest.fail('no match')

            refPath.delete()
        except AssertionError:
            with open(str(refPath), 'w') as f:
                f.write(prettified)
            raise
