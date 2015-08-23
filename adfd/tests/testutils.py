from plumbum import LocalPath

from adfd.adfd_parser import AdfdPrimer


class DataGrabber(object):
    def __init__(self, relPath='.', absPath=None):
        if absPath:
            self.rootPath = absPath
        else:
            self.rootPath = LocalPath(__file__).up() / 'data' / relPath

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

    def get_text(self, fName, ext='.bb'):
        return self.grab(self.rootPath / (fName + ext))

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

    def grab(self, path=None):
        path = path or self.rootPath
        return path.read('utf-8')

