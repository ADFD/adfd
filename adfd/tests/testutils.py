from plumbum import LocalPath

from adfd.adfd_parser import AdfdPrimer


class DataGrabber(object):
    def __init__(self, relPath='.', ext='.bb'):
        self.rootPath = LocalPath(__file__).up() / 'data' / relPath
        self.ext = ext

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

    def get_lines(self, fName):
        """get lines as list from file (without empty element at end)"""
        return AdfdPrimer(self.get_text(fName)).strippedLines

    def get_text(self, fName):
        return (self.rootPath / (fName + self.ext)).read()

    def get_pairs(self):
        paths = [p for p in sorted(self.rootPath.list())]
        idx = 0
        contents = []
        while idx + 1 < len(paths):
            fName = paths[idx].basename
            src = paths[idx].read('utf-8')
            exp = paths[idx + 1].read('utf-8')
            contents.append((fName, src, exp))
            idx += 2
        return contents
