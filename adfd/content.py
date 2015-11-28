# -*- coding: utf-8 -*-
import logging
import re

from adfd.conf import METADATA
from adfd.cst import EXT, PATH
from adfd.utils import dump_contents, ContentGrabber, get_paths, slugify


log = logging.getLogger(__name__)


class Article(object):
    def __init__(self, identifier):
        self.identifier = ("%05d" % (identifier))
        self.cntPath = PATH.CNT_PREPARED / (self.identifier + EXT.BBCODE)
        self.content = ContentGrabber(self.cntPath).grab()
        self.md = Metadata(PATH.CNT_PREPARED / (self.identifier + EXT.META))
        self.title = self.md.title
        self.linktext = self.md.linktext or self.md.title
        self.slug = self.md.slug

    @property
    def structuralRepresentation(self):
        return tuple(["/%s/" % (self.slug), self.linktext])


def prepare_all(containerPath):
    for path in [p for p in containerPath.list() if p.isdir()]:
        log.info('prepare %s', path)
        TopicPreparator(path).prepare()


class TopicPreparator(object):
    """Take exported files of a topic and prepare them for HTML conversion"""
    def __init__(self, path, slugPrefix=None):
        self.slugPrefix = slugPrefix
        self.path = path
        self.cntSrcPaths = get_paths(self.path, EXT.BBCODE)
        if not self.cntSrcPaths:
            raise TopicNotImported(self.path)

        self.mdSrcPaths = get_paths(self.path, EXT.META)
        self.md = prepare_metadata(self.mdSrcPaths, self.slugPrefix)
        filename = '%05d' % (int(self.md.topicId))
        self.cntDstPath = PATH.CNT_PREPARED / (filename + EXT.BBCODE)
        self.mdDstPath = PATH.CNT_PREPARED / (filename + EXT.META)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.path)

    @property
    def content(self):
        """merge contents from topic files into one file"""
        contents = []
        for path in self.cntSrcPaths:
            content = ''
            if self.md.useTitles:
                content += self.md.title + '\n'
            content += ContentGrabber(path).grab()
            contents.append(content)
        return "\n\n".join(contents)

    def prepare(self):
        dump_contents(self.cntDstPath, self.content)
        self.md.dump(self.mdDstPath)


class TopicNotImported(Exception):
    """raise when the raw path of the topic is"""


def prepare_metadata(paths, slugPrefix=None):
    """
    * add missing data and write back
    * return merged metadata newest to oldest (first post wins)

    :returns: Metadata
    """
    md = Metadata(slugPrefix=slugPrefix)
    allAuthors = set()
    for path in reversed(paths):
        tmpMd = Metadata(path)
        allAuthors.add(tmpMd.author)
        if not tmpMd.slug:
            tmpMd.slug = slugify(tmpMd.title or 'no title')
        tmpMd.linktext = tmpMd.linktext or tmpMd.title
        tmpMd.dump()
        md.populate_from_kwargs(tmpMd.asDict)
    md.allAuthors = ",".join(allAuthors)
    return md


class Metadata(object):
    """For overriding this directly from post contents the bbcode tag
    ``meta`` has to be defined on the board.

    The following settings to be done in ``adm/index.php?i=acp_bbcodes``
    define the tag and make it invisible if the post is viewed directly.

    BBCODE use:

        [meta]{TEXT}[/meta]

    BBCODE replacement:

        <span style="display: none;">[meta]{TEXT}[/meta]</span>
    """
    META_RE = re.compile(r'\[meta\](.*)\[/meta\]', re.MULTILINE | re.DOTALL)

    def __init__(self, path=None, kwargs=None, text=None, slugPrefix=None):
        """WARNING: all public attributes will coerced to strings if written"""
        self._path = path

        self.author = None
        self.title = None
        self.slug = None
        self.linktext = None

        self.authorId = None
        self.lastUpdate = None
        self.postDate = None
        self.topicId = None
        self.postId = None

        self.allAuthors = None
        self.useTitles = None
        self.excludePosts = None
        self.includePosts = None

        self.populate_from_file(path)
        self.populate_from_kwargs(kwargs)
        self.populate_from_text(text)
        if slugPrefix:
            self.slug = "%s%s" % (slugPrefix.lower(), self.slug)

    def __repr__(self):
        return self.asFileContents

    @property
    def asFileContents(self):
        return "\n".join([".. %s: %s" % (k, v) for k, v in self.asDict.items()
                          if v is not None])

    @property
    def asDict(self):
        dict_ = {}
        for name in vars(self):
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

            log.debug('export_all "%s"', line)
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

    def dump(self, path=None):
        path = path or self._path
        if not path:
            raise PathMissing(self.asFileContents)

        dump_contents(path, self.asFileContents)


class PathMissing(Exception):
    """raise if trying to dump a file without knowing the path"""


class NotAnAttribute(Exception):
    """raise if a key is not an attribute"""


class NotOverridable(Exception):
    """raise if a key mustn't be overriden (e.g. postId)"""
