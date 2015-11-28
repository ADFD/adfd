# -*- coding: utf-8 -*-
import logging
import re

from cached_property import cached_property

from adfd.conf import METADATA
from adfd.cst import EXT, DIR, PATH, FILENAME
from adfd.utils import dump_contents, slugify, ContentGrabber, get_paths

log = logging.getLogger(__name__)


class Article(object):
    def __init__(self, identifier, slugPrefix='', refresh=True):
        self.identifier = identifier
        self.isStatic = not isinstance(identifier, int)
        if self.isStatic:
            self.cntPaths = [PATH.STATIC / (self.identifier + EXT.BBCODE)]
            self.mdPaths = [PATH.STATIC / (self.identifier + EXT.META)]
            self.preppedCntPath = self.preppedMdPath = None
        else:
            self.topicPath = PATH.TOPICS / ("%05d" % (identifier))
            self.preppedCntPath = self.topicPath / FILENAME.CONTENT
            self.preppedMdPath = self.topicPath / FILENAME.META
            if refresh:
                self.remove_prepared_files()
            self.cntPaths, self.mdPaths = self._init_imported()
        if not self.cntPaths:
            raise ArticleNotFound(str(identifier))

        self.mm = MergedMetadata(self.mdPaths, slugPrefix=slugPrefix.lower())
        self.md = self.mm.mds[0]
        self.title = self.md.title
        self.linktext = self.md.linktext or self.md.title
        self.slug = self.md.slug or slugify(self.md.title)
        if not self.isStatic:
            self._dump_contents()

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.slug)

    def _init_imported(self):
        log.info('candidate: %s', self.preppedCntPath)
        if self.preppedCntPath.exists():
            log.info('prepared article found %s', self.preppedCntPath)
            cntPaths = [self.preppedCntPath]
            mdPaths = self.preppedMdPath
        else:
            rawPath = self.topicPath / DIR.RAW
            log.debug('candidate: %s', rawPath)
            cntPaths = get_paths(rawPath, EXT.BBCODE)
            mdPaths = get_paths(rawPath, EXT.META)
        return cntPaths, mdPaths

    def _dump_contents(self):
        if not self.isStatic:
            dump_contents(self.preppedCntPath, self.content)
            dump_contents(self.preppedMdPath, self.md.asFileContents)

    @property
    def structuralRepresentation(self):
        return tuple(["/%s/" % (self.slug), self.linktext])

    @cached_property
    def content(self):
        contents = []
        for path in self.cntPaths:
            contents.append(ContentGrabber(path).grab())
        return "\n\n".join(contents)

    def remove_prepared_files(self):
        for path in [self.preppedCntPath, self.preppedCntPath]:
            path.delete()


class ArticleNotFound(Exception):
    """raise when the article is nowhere to be found"""


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
        return "\n".join([".. %s: %s" % (k, v) for k, v in self._dict.items()
                          if v is not None])

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


class MergedMetadata(object):
    def __init__(self, paths, slugPrefix=''):
        """:type paths: list of paths to metadata files"""
        self.mds = [Metadata(path, slugPrefix=slugPrefix) for path in paths]

    @cached_property
    def lastUpdate(self):
        return sorted([md.lastUpdate for md in self.mds], reverse=True)[0]

    @staticmethod
    def get_all_metadata_paths(path):
        return get_paths(path, EXT.META)
