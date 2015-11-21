# -*- coding: utf-8 -*-
import codecs
import logging
from collections import OrderedDict

# noinspection PyUnresolvedReferences
import translitcodec  # register new codec for slugification
from cached_property import cached_property

from adfd import cst
from adfd.cst import DIR
from adfd.utils import ContentGrabber, ContentDumper


log = logging.getLogger(__name__)


class Article(object):
    SRC_PATH = cst.PATH.CONTENT
    PREPARED_PATH = SRC_PATH / DIR.PREPARED

    def __init__(self, identifier, slugPrefix=''):
        self.PREPARED_PATH.mkdir()
        self.slugPrefix = slugPrefix.lower()
        if isinstance(identifier, int):
            originalIdentifer = identifier
            self.isImported = True
            self.identifier = "%05d" % (identifier)
            self.srcPath = self.SRC_PATH / DIR.RAW / self.identifier
            self.ensure_is_imported(originalIdentifer)
        else:
            self.isImported = False
            self.identifier = identifier
            self.srcPath = self.SRC_PATH / DIR.STATIC
        log.debug("id: %s source: %s", self.srcPath, self.identifier)
        self.md = self.fetch_metadata_dict()

    def __repr__(self):
        return u'<%s %s>' % (self.__class__.__name__, self.slug)

    @property
    def structuralRepresentation(self):
        return tuple(["/%s/" % (self.slug), self.linktext])

    @property
    def title(self):
        return self.md['title']

    @property
    def linktext(self):
        try:
            return self.md['linktext']

        except KeyError:
            return self.md['title']

    @property
    def slug(self):
        try:
            return self.md['slug']

        except KeyError:
            return self.slugify(self.md['title'])

    def slugify(self, title):
        words = []
        for word in cst.SLUG.PUNCT.split(title.lower()):
            word = codecs.encode(word, 'translit/long')
            if word:
                words.append(word)
        return u'-'.join(words)

    # fixme
    def fetch_metadata_dict(self):
        """only using first found metadata for now ...
        todo: merge into one dict and e.g always set last update
        to newest update of all posts the article consists of
        """
        metadata = ContentGrabber(absPath=self.metadataPaths[0]).grab()
        metadataDict = OrderedDict()
        for line in metadata.split('\n'):
            if not line.strip():
                break

            log.debug('process "%s"', line)
            key, value = line[3:].split(': ', 1)
            metadataDict[key.strip()] = value.strip()
        return metadataDict

    @cached_property
    def content(self):
        contents = []
        for path in self.contentFilePaths:
            contents.append(ContentGrabber(absPath=path).grab())
        return "\n".join(contents)

    @property
    def contentFilePaths(self):
        if self.isImported:
            return [p for p in self._postPaths if str(p).endswith('.bb')]

        return [self.srcPath / (self.identifier + '.bb')]

    @property
    def metadataPaths(self):
        if self.isImported:
            return [p for p in self._postPaths if str(p).endswith('.meta')]

        return [self.srcPath / (self.identifier + '.meta')]

    @property
    def _postPaths(self):
        return sorted([p for p in self.srcPath.list()])

    def ensure_is_imported(self, identifier):
        try:
            if not len(self.contentFilePaths):
                raise Exception("article folder for %s empty", identifier)

        except OSError:
            raise Exception(
                "article %s not found at %s", identifier, self.srcPath)

    def finalize_slug(self):
        """writes changed slug back into the file"""
        if self.slugPrefix:
            self.md['slug'] = "%s/%s" % (self.slugPrefix, self.slug)
        newDict = "\n".join(
            [".. %s: %s" % (key, value) for key, value
             in self.md.items()])
        metadataDstPath = self.PREPARED_PATH / (self.identifier + '.meta')
        ContentDumper(metadataDstPath, newDict).dump()
        articleDstPath = self.PREPARED_PATH / (self.identifier + '.bb')
        ContentDumper(articleDstPath, self.content).dump()
