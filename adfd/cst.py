import logging
import re

import plumbum

log = logging.getLogger(__name__)

try:
    from adfd.secrets import DB
    REMOTE_HOST = DB.REMOTE_HOST
except ImportError:
    REMOTE_HOST = "adfd.org"
    log.error("use generic remote host %s", REMOTE_HOST)


class APP:
    PORT = 5000


class EXT:
    IN = '.bbcode'
    OUT = '.html'
    META = '.meta'


class DIR:
    RAW = 'raw'
    """folders containing topics one file per post + metadata for each post"""
    PREPARED = 'prepared'
    """merged single file raw articles and merged single file metadata"""
    FINAL = 'final'
    """rendered and structured result with additional category metadata"""


class NAME:
    CATEGORY = 'category'
    CONTENT = 'content'
    FINAL = 'final'
    INDEX = 'index'
    NODE_PAGE = 'index'
    NODE_PAGE_FILE = '%s%s' % (NODE_PAGE, EXT.OUT)
    OUTPUT = 'build'
    PAGE = 'page'
    PAGES = 'pages'
    ROOT = '/'


class PARSE:
    FUNC = None
    PYPHEN_LANG = 'de_de'
    TITLE_PATTERN = '[h2]%s[/h2]\n'


class PATH:
    PROJECT = plumbum.LocalPath(__file__).dirname.up()
    OUTPUT = PROJECT / NAME.OUTPUT
    CONTENT = PROJECT / NAME.CONTENT
    CNT_RAW = CONTENT / DIR.RAW
    """exported bbcode like it looks when edited - each posts in a single file.

    It is not raw in the sense that it has the same format like stored in DB
    as this is quite different from what one sees in the editor, but from
    an editors perspective that does not matter, so this is considered raw
    """
    CNT_PREPARED = CONTENT / DIR.PREPARED
    """prepared in a file pair - contents as bbcode in one file + metadata"""
    CNT_FINAL = CONTENT / DIR.FINAL
    """the final structure that makes the website"""

    PAGES = CONTENT / NAME.FINAL
    SITE = PROJECT / 'adfd' / 'site'
    TEMPLATES = SITE / 'templates'
    FOUNDATION = SITE / 'foundation'
    STATIC = FOUNDATION / 'dist' / 'assets'


class METADATA:
    """settings for the accompanying meta data used by the web generator

    For overriding this directly from post contents the bbcode tag
    ``meta`` has to be defined on the board.

    The following settings to be done in ``adm/index.php?i=acp_bbcodes``
    define the tag and make it invisible if the post is viewed directly.

    BBCODE use:

        [meta]{TEXT}[/meta]

    BBCODE replacement:

        <span style="display: none;">[meta]{TEXT}[/meta]</span>
    """
    class CATEGORY:
        ATTRIBUTES = [
            'name',
            'mainTopicId',
            'weight'
        ]

    class PAGE:
        OVERRIDABLES = [
            'allAuthors',
            'excludePosts',
            'includePosts',
            'linktext',
            'relFilePath',
            'relPath',
            'slug',
            'title',
            'weight',
        ]
        """can be overridden by metadata in post content"""
        ATTRIBUTES = OVERRIDABLES + [
            'author',
            'authorId',
            'lastUpdate',
            'postDate',
            'topicId',
            'postId',

            'useTitles',

            'relPath',
        ]
        """all allowed attributes in use, prevents shooting self in foot"""

    DATE_FORMAT = '%d.%m.%Y'
    """this format will be used for human readable dates in meta data"""


class RE:
    URL = re.compile(
        r'(?im)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)'
        r'(?:[^\s()<>]+|\([^\s()<>]+\))'
        r'+(?:\([^\s()<>]+\)|[^\s`!()\[\]{};:\'".,<>?]))')
    """
    from http://daringfireball.net/2010/07/improved_regex_for_matching_urls
    Only support one level of parentheses - was failing on some URLs.
    See http://www.regular-expressions.info/catastrophic.html
    """
    DOMAIN = re.compile(
        r'(?im)(?:www\d{0,3}[.]|[a-z0-9.\-]+[.]'
        r'(?:com|net|org|edu|biz|gov|mil|info|io|name|me|tv|us|uk|mobi))')
    """
    For the URL tag, try to be smart about when to append a missing http://.
    If the given link looks like a domain, add a http:// in front of it,
    otherwise leave it alone (be a relative path, a filename, etc.).
    """


class TARGET:
    class _Target:
        def __init__(self, name, path, prefix):
            self.name = name
            self.path = path
            self.prefix = prefix

        def __str__(self):
            return self.name

        def __eq__(self, other):
            return self.name == other.name

    TEST = _Target('test', '%s:./www/privat/neu' % REMOTE_HOST, 'privat/neu')
    LIVE = _Target('live', '%s:./www/inhalt' % REMOTE_HOST, 'inhalt')
    ALL = [TEST, LIVE]

    @classmethod
    def get(cls, wantedTarget):
        for target in cls.ALL:
            if isinstance(wantedTarget, cls._Target):
                wantedTarget = wantedTarget.name
            if target.name == wantedTarget:
                return target

        raise ValueError('target %s not found' % (wantedTarget))
