# -*- coding: utf-8 -*-
import logging
from collections import OrderedDict

import re

from cached_property import cached_property

from adfd.bbcode import AdfdParser
from adfd.conf import METADATA, PATH, BBCODE
from adfd.cst import EXT
from adfd.utils import (
    dump_contents, ContentGrabber, get_paths, slugify, slugify_path)

log = logging.getLogger(__name__)


def prepare(srcPath, dstPath):
    for path in [p for p in srcPath.list() if p.isdir()]:
        log.info('prepare %s', path)
        TopicPreparator(path, dstPath).prepare()


def finalize(structure, pathPrefix=''):
    for weight, (relPath, item) in enumerate(structure):
        if isinstance(item, tuple):
            finalize(item, relPath)
        else:
            if pathPrefix and pathPrefix != 'root':
                relPath = "%s/%s" % (pathPrefix, relPath)
            for topicId in item:
                log.info('finalize %s at %s', topicId, relPath)
                TopicFinalizer(topicId, relPath, weight).process()


class TopicPreparator(object):
    """Take exported files of a topic and prepare them for HTML conversion"""

    def __init__(self, path, dstPath):
        self.path = path
        self.cntSrcPaths = get_paths(self.path, EXT.BBCODE)
        if not self.cntSrcPaths:
            raise TopicNotFound(self.path)

        self.mdSrcPaths = get_paths(self.path, EXT.META)
        self.md = self.prepare_metadata(self.mdSrcPaths)
        filename = '%05d' % (int(self.md.topicId))
        self.cntDstPath = dstPath / (filename + EXT.BBCODE)
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
                content += BBCODE.TITLE_PATTERN % (self.md.title)
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
            if not tmpMd.slug:
                tmpMd.slug = slugify(tmpMd.title or 'no title')
            tmpMd.linktext = tmpMd.linktext or tmpMd.title
            tmpMd.dump()
            md.populate_from_kwargs(tmpMd.asDict)
        md.allAuthors = ",".join(allAuthors)
        return md


class TopicFinalizer(object):
    def __init__(self, topicId, relPath='', weight=0):
        self.slugPath = slugify_path(relPath)
        self.order = weight
        topicId = ("%05d" % (topicId))
        self.cntPath = PATH.CNT_PREPARED / (topicId + EXT.BBCODE)
        relHtmlDstPathName = topicId + EXT.HTML
        if self.slugPath:
            relHtmlDstPathName = "%s/%s" % (self.slugPath, relHtmlDstPathName)
        kwargs = dict(relPath=relPath, weight=weight,
                      relFilePath=relHtmlDstPathName)
        mdSrcPath = PATH.CNT_PREPARED / (topicId + EXT.META)
        self.md = PageMetadata(mdSrcPath, kwargs=kwargs)
        self.htmlDstPath = PATH.CNT_FINAL / relHtmlDstPathName
        self.mdDstPath = PATH.CNT_FINAL / self.slugPath / (topicId + EXT.META)

    def process(self):
        dump_contents(self.htmlDstPath, (AdfdParser().to_html(self.content)))
        self.md.dump(self.mdDstPath)

    @cached_property
    def content(self):
        return ContentGrabber(self.cntPath).grab()


class PageMetadata(object):
    META_RE = re.compile(r'\[meta\](.*)\[/meta\]', re.MULTILINE | re.DOTALL)

    def __init__(self, path=None, kwargs=None, text=None):
        """WARNING: all public attributes are written as meta data"""
        self._path = path
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
        self.populate_from_file(path)
        self.populate_from_kwargs(kwargs)
        self.populate_from_text(text)

    def __repr__(self):
        return self.asFileContents

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

            if name not in METADATA.ATTRIBUTES:
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
        setattr(self, key.strip(), str(value).strip())

    def dump(self, path=None):
        path = path or self._path
        if not path:
            raise PathMissing(self.asFileContents)

        dump_contents(path, self.asFileContents)


class TopicNotFound(Exception):
    """raise when the raw path of the topic is"""


class PathMissing(Exception):
    """raise if trying to dump a file without knowing the path"""


class NotAnAttribute(Exception):
    """raise if a key is not an attribute"""


class NotOverridable(Exception):
    """raise if a key mustn't be overriden (e.g. postId)"""
