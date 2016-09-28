import logging
import re
from collections import OrderedDict

from adfd.exc import NotAnAttribute, NotOverridable
from adfd.utils import ContentGrabber

log = logging.getLogger(__name__)


class Metadata:
    """
    For overriding this directly from post contents the bbcode tag
    ``meta`` has to be defined on the board.

    The following settings to be done in ``adm/index.php?i=acp_bbcodes``
    define the tag and make it invisible if the post is viewed directly.

    BBCODE use:

        [meta]{TEXT}[/meta]

    BBCODE replacement:

        <span style="display: none;">[meta]{TEXT}[/meta]</span>
    """
    ATTRIBUTES = None
    OVERRIDABLES = None
    META_RE = re.compile(r'\[meta\](.*)\[/meta\]', re.MULTILINE | re.DOTALL)

    def __init__(self, path=None, kwargs=None, text=None):
        """WARNING: all public attributes are written as meta data"""
        self._path = path
        self.populate_from_file(path)
        self.populate_from_kwargs(kwargs)
        self.populate_from_text(text)

    def __repr__(self):
        return str(self.asDict)

    @property
    def exists(self):
        return self._path and self._path.exists()

    @property
    def asFileContents(self):
        return "\n".join([".. %s: %s" % (k, v) for k, v in self.asDict.items()
                          if v is not None])

    @property
    def asDict(self):
        dict_ = OrderedDict()
        for name in sorted(vars(self)):
            if name.startswith('_'):
                continue

            if self.ATTRIBUTES and name not in self.ATTRIBUTES:
                raise NotAnAttribute(name)

            attr = getattr(self, name)
            if not attr:
                continue

            if attr in ['True', 'False']:
                attr = True if attr == 'True' else False

            dict_[name] = attr
        return dict_

    def populate_from_file(self, path):
        if not path or not path.exists():
            return

        for line in ContentGrabber(path).grab().split('\n'):
            if not line.strip():
                continue

            key, value = line[3:].split(': ', 1)
            log.debug('%s -> %s from "%s"', key, value, line)
            self.update(key.strip(), value.strip())

    def populate_from_kwargs(self, kwargs):
        if not kwargs:
            return

        for key, value in kwargs.items():
            self.update(key, str(value))

    def populate_from_text(self, text):
        if not text:
            return

        match = self.META_RE.search(text)
        if not match:
            return

        metaLines = match.group(1).split('\n')
        for line in metaLines:
            assert isinstance(line, str)  # pycharm is strange sometimes
            if not line.strip():
                continue

            key, value = line.split(':', maxsplit=1)
            key = key.strip()
            if self.OVERRIDABLES and key not in self.OVERRIDABLES:
                raise NotOverridable('%s in %s' % (key, self))

            self.update(key, value.strip())

    def update(self, key, value):
        key = key.strip()
        value = str(value).strip()
        log.debug('%s: %s -> %s', self.__class__.__name__, key, value)
        setattr(self, key, value)


# FIXME this is a bit fuzzy still. There should be Post and Topic metadata
class PageMetadata(Metadata):
    OVERRIDABLES = [
        'allAuthors',
        'isExcluded',
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
    ]
    """all allowed attributes in use, prevents shooting self in foot"""
    def __init__(self, path=None, kwargs=None, text=None):
        self.allAuthors = None
        self.author = None
        self.authorId = None
        self.isExcluded = False
        self.lastUpdate = None
        self.postDate = None
        self.postId = None
        self.slug = None
        self.title = None
        self.topicId = None
        self.useTitles = True
        self.weight = None
        super().__init__(path, kwargs, text)
