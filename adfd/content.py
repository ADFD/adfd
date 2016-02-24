# -*- coding: utf-8 -*-
import logging
import re
from collections import OrderedDict

from cached_property import cached_property

from adfd.conf import METADATA, PATH, PARSE
from adfd.cst import EXT, NAME
from adfd.utils import (
    dump_contents, ContentGrabber, get_paths, slugify_path, id2name, slugify)

log = logging.getLogger(__name__)


def prepare(srcPath, dstPath):
    for path in [p for p in srcPath.list() if p.isdir()]:
        log.info('prepare %s', path)
        TopicPreparator(path, dstPath).prepare()


class Finalizator:
    def __init__(self, structure):
        self.structure = structure

    def finalize(self):
        self._finalize(self.structure, '')

    def _finalize(self, desc, pathPrefix, weight=1):
        relPath = desc.name
        if pathPrefix:
            relPath = "%s/%s" % (pathPrefix, desc.name)
        log.info('main topic in "%s" is %s', relPath, desc.mainTopicId)
        TopicFinalizer(desc.mainTopicId, relPath, isCategory=True).finalize()
        self.dump_cat_md(desc.name, relPath,
                         mainTopicId=desc.mainTopicId, weight=weight)
        if isinstance(desc.contents, tuple):
            for idx, dsc in enumerate(desc.contents, start=1):
                self._finalize(dsc, relPath, weight + idx)
        else:
            assert isinstance(desc.contents, list), desc.contents
            for tWeight, topicId in enumerate(desc.contents, start=1):
                log.info('topic %s in %s is "%s"', tWeight, relPath, topicId)
                TopicFinalizer(topicId, relPath, tWeight).finalize()

    def dump_cat_md(self, name, relPath, **kwargs):
        relPath = slugify_path(relPath)
        kwargs.update(name=name)
        path = (PATH.CNT_FINAL / relPath / NAME.CATEGORY).with_suffix(EXT.META)
        CategoryMetadata(kwargs=kwargs).dump(path)


class TopicPreparator:
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


class TopicFinalizer:
    def __init__(self, topicId, relPath='', weight=0, isCategory=False):
        self.topicIdName = id2name(topicId)
        self.slugPath = slugify_path(relPath)
        self.mdKwargs = dict(weight=weight)
        assert self.md.exists, self.md._path
        dstPath = PATH.CNT_FINAL
        if self.slugPath:
            dstPath /= self.slugPath
        if not isCategory:
            dstPath /= slugify(self.md.title)
        dstPath /= NAME.INDEX
        self.htmlDstPath = dstPath.with_suffix(EXT.OUT)
        self.mdDstPath = dstPath.with_suffix(EXT.META)

    def finalize(self):
        dump_contents(self.htmlDstPath, self.outContent)
        self.md.dump(self.mdDstPath)

    @cached_property
    def md(self):
        path = (PATH.CNT_PREPARED / self.topicIdName).with_suffix(EXT.META)
        return PageMetadata(path, kwargs=self.mdKwargs)

    @cached_property
    def inContent(self):
        srcPath = (PATH.CNT_PREPARED / self.topicIdName).with_suffix(EXT.IN)
        return ContentGrabber(srcPath).grab()

    @cached_property
    def outContent(self):
        return PARSE.FUNC(self.inContent)


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


class TopicNotFound(Exception):
    """raise when the raw path of the topic is"""


class PathMissing(Exception):
    """raise if trying to dump a file without knowing the path"""


class NotAnAttribute(Exception):
    """raise if a key is not an attribute"""


class NotOverridable(Exception):
    """raise if a key mustn't be overriden (e.g. postId)"""
