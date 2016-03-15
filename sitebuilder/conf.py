import plumbum


class APP:
    PORT = 5000


class EXT:
    META = '.meta'
    CNT = '.html'


class NAME:
    ROOT = '/'
    CONTENT = 'content'
    PAGES = 'pages'
    FINAL = 'final'
    OUTPUT = 'build'
    NODE_PAGE = 'index'
    NODE_PAGE_FILE = '%s%s' % (NODE_PAGE, EXT.CNT)


class PATH:
    PROJECT = plumbum.LocalPath(__file__).dirname.up()
    OUTPUT = PROJECT / NAME.OUTPUT
    CONTENT = PROJECT / NAME.CONTENT  # symlink to exported content
    PAGES = CONTENT / NAME.FINAL
    FRONTEND = PROJECT / 'foundation6'
    STATIC = FRONTEND / 'dist' / 'assets'
    TEMPLATES = FRONTEND / 'src' / 'templates'


class _Target:
    def __init__(self, name, path, prefix=None):
        self.name = name
        self.path = path
        self.prefix = prefix

    def __str__(self):
        return self.name


class TARGET:
    TEST = _Target('test', 'mj13.de:./www/privat/neu', 'privat/neu')
    LIVE = _Target('live', 'mj13.de:./www/inhalt', 'inhalt')
    ALL = [TEST, LIVE]

    @classmethod
    def get(cls, name):
        for target in cls.ALL:
            if name == target.name:
                return target
        raise ValueError('target %s not found' % (name))
