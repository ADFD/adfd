# -*- coding: utf-8 -*-
import logging
import re
from collections import OrderedDict

from cached_property import cached_property

from adfd.conf import METADATA, PATH, STRUCTURE, PARSE
from adfd.cst import EXT, NAME
from adfd.utils import (
    dump_contents, ContentGrabber, get_paths, slugify_path, id2name)

log = logging.getLogger(__name__)


def prepare(srcPath, dstPath):
    for path in [p for p in srcPath.list() if p.isdir()]:
        log.info('prepare %s', path)
        TopicPreparator(path, dstPath).prepare()


def finalize(structure, pathPrefix=''):
    for cWeight, (nameMainTopic, rest) in enumerate(structure):
        log.info("%s | %s", nameMainTopic, rest)
        name, mainTopicId = nameMainTopic
        if pathPrefix and name:
            relPath = "%s/%s" % (pathPrefix, name)
        else:
            relPath = name
        TopicFinalizer(mainTopicId, relPath, isMain=True).finalize()
        dump_cat_md(name, relPath, mainTopicId=mainTopicId, weight=cWeight)
        if isinstance(rest, tuple):
            finalize(rest, name)
        else:
            for topicWeight, topicId in enumerate(rest):
                log.info('finalize %s at %s', topicId, relPath)
                TopicFinalizer(topicId, relPath, topicWeight).finalize()


class TopicPreparator(object):
    """Take exported files of a topic and prepare them for HTML conversion"""

    def __init__(self, path, dstPath):
        self.path = path
        self.cntSrcPaths = get_paths(self.path, EXT.IN)
        if not self.cntSrcPaths:
            raise TopicNotFound(self.path)

        self.mdSrcPaths = get_paths(self.path, EXT.META)
        self.md = self.prepare_metadata(self.mdSrcPaths)
        filename = id2name(self.md.topicId)
        self.cntDstPath = dstPath / (filename + EXT.IN)
        self.mdDstPath = dstPath / (filename + EXT.META)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.path)

    @property
    def content(self):
        """merge contents from topic files into one file"""
        contents = []
        for path in self.cntSrcPaths:
            content = ''
            if self.md.useTitles:
                content += PARSE.TITLE_PATTERN % (self.md.title)
            content += ContentGrabber(path).grab()
            contents.append(content)
        return "\n\n".join(contents)

    def prepare(self):
        dump_contents(self.cntDstPath, self.content)
        self.md.dump(self.mdDstPath)

    @staticmethod
    def prepare_metadata(paths):
        """
        * add missing data and write back
        * return merged metadata newest to oldest (first post wins)

        :returns: PageMetadata
        """
        md = PageMetadata()
        allAuthors = set()
        for path in reversed(paths):
            tmpMd = PageMetadata(path)
            allAuthors.add(tmpMd.author)
            tmpMd.dump()
            md.populate_from_kwargs(tmpMd.asDict)
        md.allAuthors = ",".join(allAuthors)
        return md


def dump_cat_md(name, relPath, **kwargs):
    name = name
    relPath = slugify_path(relPath)
    kwargs.update(name=name)
    path = PATH.CNT_FINAL / relPath / (NAME.CATEGORY + EXT.META)
    CategoryMetadata(kwargs=kwargs).dump(path)


class TopicFinalizer(object):
    PARSEFUNC = PARSE.FUNC

    def __init__(self, topicId, relPath='', weight=0, isMain=False):
        self.slugPath = slugify_path(relPath)
        topicId = id2name(topicId)
        self.cntPath = PATH.CNT_PREPARED / (topicId + EXT.IN)
        if isMain:
            relPath = 'main' + EXT.OUT
        else:
            relPath = "%02d-%s" % (weight, topicId + EXT.OUT)
        if self.slugPath:
            relPath = "%s/%s" % (self.slugPath, relPath)
        self.dstPath = PATH.CNT_FINAL / relPath

    def finalize(self):
        dump_contents(self.dstPath, self.outContent)

    @cached_property
    def inContent(self):
        return ContentGrabber(self.cntPath).grab()

    @cached_property
    def outContent(self):
        return self.PARSEFUNC(self.inContent)


class Metadata(object):
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
                raise NotOverridable('key')

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
        self.linktext = None
        self.weight = None
        self.postId = None
        self.postDate = None
        self.relPath = None
        self.relFilePath = None
        self.slug = None
        self.title = None
        self.topicId = None
        self.useTitles = None
        super().__init__(path, kwargs, text)


class TopicNotFound(Exception):
    """raise when the raw path of the topic is"""


class PathMissing(Exception):
    """raise if trying to dump a file without knowing the path"""


class NotAnAttribute(Exception):
    """raise if a key is not an attribute"""


class NotOverridable(Exception):
    """raise if a key mustn't be overriden (e.g. postId)"""

if __name__ == '__main__':
    finalize(STRUCTURE, '')
