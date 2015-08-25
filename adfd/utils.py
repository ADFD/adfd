from plumbum import LocalPath


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
