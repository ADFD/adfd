# -*- coding: utf-8 -*-
import logging
import re

from cached_property import cached_property

from adfd.conf import METADATA
from adfd.cst import EXT, DIR, PATH, FILENAME
from adfd.utils import ContentGrabber, ContentDumper, slugify


log = logging.getLogger(__name__)


class Article(object):
    def __init__(self, identifier, slugPrefix='', refresh=True):
        self.isStatic = not isinstance(identifier, int)
        topicPath = self._init_paths(identifier, refresh)
        if not self.paths:
            raise ArticleNotFound(str(identifier))

        self.md = Metadata(path=self.mdSrcPath, slugPrefix=slugPrefix.lower())
        if topicPath:
            self._dump_contents()

        self.md.populate_from_text(self.content)
        self.title = self.md.title
        self.linktext = self.md.linktext or self.md.title
        self.slug = self.md.slug or slugify(self.md.title)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.slug)

    def _init_paths(self, identifier, refresh):
        log.info('get article from %s', identifier)
        if self.isStatic:
            log.debug('try to get static article %s', identifier)
            self.identifier = identifier
            paths = PATH.STATIC.list()
            self.paths = [p for p in paths if identifier in str(p)]
            self.mdSrcPath = PATH.STATIC / (identifier + EXT.META)
            return

        topicPath = PATH.TOPICS / ("%05d" % (identifier))
        self.prepContentDstPath = topicPath / FILENAME.CONTENT
        self.prepMdDstPath = topicPath / FILENAME.META
        if refresh:
            self.prepContentDstPath.delete()
            self.prepMdDstPath.delete()
        log.debug('candidate: %s', self.prepContentDstPath)
        if not self.prepContentDstPath.exists():
            rawPath = topicPath / DIR.RAW
            log.debug('candidate: %s', rawPath)
            paths = sorted([p for p in rawPath.list()])
            self.paths = [p for p in paths if str(p).endswith(EXT.BBCODE)]
            self.mdSrcPath = rawPath / FILENAME.META
            return topicPath

        log.info('prepared article found %s', self.prepContentDstPath)
        assert self.mdSrcPath.exists(), self.mdSrcPath
        self.paths = [self.prepContentDstPath]
        self.mdSrcPath = topicPath / FILENAME.META

    def _dump_contents(self):
        ContentDumper(self.prepContentDstPath, self.content).dump()
        ContentDumper(self.prepMdDstPath, self.md.asFileContents).dump()

    @property
    def structuralRepresentation(self):
        return tuple(["/%s/" % (self.slug), self.linktext])

    @cached_property
    def content(self):
        contents = []
        for path in self.paths:
            contents.append(ContentGrabber(path).grab())
        return "\n\n".join(contents)

    def remove_prepared_files(self):
        for path in [self.prepContentDstPath, self.prepMdDstPath]:
            path.delete()


class ArticleNotFound(Exception):
    """raise when the article is nowhere to be found"""


class Metadata(object):
    META_RE = re.compile(r'\[meta\](.*)\[/meta\]', re.MULTILINE | re.DOTALL)

    def __init__(self, path=None, kwargs=None, text=None, slugPrefix=None):
        self.title = None
        self.author = None
        self.slug = None
        self.linktext = None

        self.authorId = None
        self.lastUpdate = None
        self.postDate = None
        self.topicId = None
        self.postId = None

        self.populate_from_file(path)
        self.populate_from_kwargs(kwargs)
        self.populate_from_text(text)
        if slugPrefix:
            self.slug = "%s%s" % (slugPrefix, self.slug)

    def __repr__(self):
        return self.asFileContents

    @property
    def asFileContents(self):
        return "\n".join([".. %s: %s" % (k, v) for k, v in self._dict.items()])

    @property
    def _dict(self):
        return {name: getattr(self, name) for name in vars(self)
                if not name.startswith('_')}

    def populate_from_file(self, path):
        if not path:
            return

        for line in ContentGrabber(path).grab().split('\n'):
            if not line.strip():
                continue

            log.debug('process "%s"', line)
            key, value = line[3:].split(': ', 1)
            self.update(key, value)

    def populate_from_kwargs(self, kwargs):
        if not kwargs:
            return

        for key, value in kwargs.items():
            self.update(key, value)

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
            if key not in METADATA.OVERRIDABLES:
                raise NotOverridable('key')

            self.update(key, value)

    def update(self, key, value):
        log.debug('self.%s = %s', key, value)
        setattr(self, key.strip(), value.strip())


class NotOverridable(Exception):
    """raise if a key mustn't be overriden (e.g. postId)"""
