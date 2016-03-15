import logging
import re
from collections import OrderedDict

from adfd.cst import METADATA
from adfd.exc import PathMissing, NotAnAttribute, NotOverridable
from adfd.utils import ContentGrabber, dump_contents, slugify

log = logging.getLogger(__name__)


class Metadata:
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
            log.info('no overrides found in "%s"[...]', text[:20])
            return

        metaLines = match.group(1).split('\n')
        for line in metaLines:
            assert isinstance(line, str)  # pycharm is strange sometimes
            if not line.strip():
                continue

            key, value = line.split(':', maxsplit=1)
            key = key.strip()
            if self.OVERRIDABLES and key not in self.OVERRIDABLES:
                raise NotOverridable('%s in %s' % (key, self._path))

            self.update(key, value.strip())

    def update(self, key, value):
        key = key.strip()
        value = str(value).strip()
        log.debug('%s: %s -> %s', self.__class__.__name__, key, value)
        setattr(self, key, value)

    def dump(self, path=None):
        path = path or self._path
        if not path:
            raise PathMissing(self.asFileContents)

        dump_contents(path, self.asFileContents)


class CategoryMetadata(Metadata):
    ATTRIBUTES = METADATA.CATEGORY.ATTRIBUTES

    def __init__(self, path=None, kwargs=None, text=None):
        self.name = None
        self.weight = None
        self.mainTopicId = None
        super().__init__(path, kwargs, text)


class PageMetadata(Metadata):
    ATTRIBUTES = METADATA.PAGE.ATTRIBUTES
    OVERRIDABLES = METADATA.PAGE.OVERRIDABLES

    def __init__(self, path=None, kwargs=None, text=None):
        self.allAuthors = None
        self.author = None
        self.authorId = None
        self.excludePosts = None
        self.includePosts = None
        self.lastUpdate = None
        self.weight = None
        self.postId = None
        self.postDate = None
        self.relPath = None  # set dynamically by web app
        self.title = None
        self.topicId = None
        self.useTitles = None
        super().__init__(path, kwargs, text)

    @property
    def slug(self):
        return slugify(self.title)