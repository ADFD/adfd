# -*- coding: utf-8 -*-
import logging

from cached_property import cached_property

from adfd.cst import EXT, DIR, PATH, FILENAME
from adfd.utils import ContentGrabber, ContentDumper, slugify


log = logging.getLogger(__name__)


class Article(object):
    def __init__(self, identifier, slugPrefix=''):
        self.slugPrefix = slugPrefix.lower()
        isPrepared = self._init_paths(identifier)
        self.md = Metadata(path=self.mdSrcPath, slugPrefix=self.slugPrefix)
        self.title = self.md.title
        self.linktext = self.md.linktext or self.md.title
        self.slug = self.md.slug or slugify(self.md.title)
        if not isPrepared:
            ContentDumper(self.prepContentDstPath, self.content).dump()
            ContentDumper(self.prepMdDstPath, self.md.asFileContents).dump()

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.slug)

    def _init_paths(self, identifier):
        isPrepared = True
        log.error('get article from %s', identifier)
        if isinstance(identifier, int):
            dirname = "%05d" % (identifier)
            topicPath = PATH.TOPICS / dirname
            assert topicPath.exists(), topicPath
            self.prepContentDstPath = topicPath / FILENAME.CONTENT
            self.prepMdDstPath = topicPath / FILENAME.META
            log.debug('candidate: %s', self.prepContentDstPath)
            if self.prepContentDstPath.exists():
                log.info('prepared article found %s', self.prepContentDstPath)
                self.paths = [self.prepContentDstPath]
                self.mdSrcPath = topicPath / FILENAME.META
            else:
                isPrepared = False
                rawPath = topicPath / DIR.RAW
                log.debug('candidate: %s', rawPath)
                paths = sorted([p for p in rawPath.list()])
                self.paths = [p for p in paths if str(p).endswith(EXT.BBCODE)]
                self.mdSrcPath = rawPath / FILENAME.META
        else:
            log.debug('try to get static article %s', identifier)
            self.identifier = identifier
            paths = PATH.STATIC.list()
            self.paths = [p for p in paths if identifier in str(p)]
            self.mdSrcPath = PATH.STATIC / (identifier + EXT.META)
        if not self.paths:
            raise ArticleNotFound(str(identifier))

        return isPrepared

    @property
    def structuralRepresentation(self):
        return tuple(["/%s/" % (self.slug), self.linktext])

    @cached_property
    def content(self):
        contents = []
        for path in self.paths:
            contents.append(ContentGrabber(path).grab())
        return "\n".join(contents)

    def remove_prepared_files(self):
        for path in [self.prepContentDstPath, self.prepMdDstPath]:
            path.delete()


class ArticleNotFound(Exception):
    """raise when the article is nowhere to be found"""


class Metadata(object):
    _OVERRIDABLES = ['author', 'linktext', 'slug', 'title']
    """those can be overridden by metadata in post content"""

    def __init__(self, path=None, data=None, slugPrefix=None):
        self.title = None
        self.author = None
        self.slug = None
        self.linktext = None

        self.authorId = None
        self.lastUpdate = None
        self.postDate = None
        self.topicId = None
        self.postId = None

        self._populate_from_file(path)
        self._populate_from_data(data)
        if slugPrefix:
            self.slug = "%s%s" % (slugPrefix, self.slug)
        log.debug(str(self._dict))

    @property
    def asFileContents(self):
        return "\n".join([".. %s: %s" % (k, v) for k, v in self._dict.items()])

    @property
    def _dict(self):
        return {name: getattr(self, name) for name in vars(self)
                if not name.startswith('_')}

    def _populate_from_file(self, path):
        if not path:
            return

        for line in ContentGrabber(path).grab().split('\n'):
            if not line.strip():
                continue

            log.debug('process "%s"', line)
            key, value = line[3:].split(': ', 1)
            log.debug('self.%s = %s', key, value)
            setattr(self, key.strip(), value.strip())

    def _populate_from_data(self, data):
        for key in data or {}:
            setattr(self, key, data[key])

    def override(self, overrideMap):
        for key, value in overrideMap.items():
            if key not in self._OVERRIDABLES:
                raise NotOverridable('key')

            setattr(self, key, value)


class NotOverridable(Exception):
    """raise if a key mustn't be overriden (e.g. postId)"""
