# -*- coding: utf-8 -*-
from collections import OrderedDict
import logging
import os
import re

# noinspection PyUnresolvedReferences
import translitcodec  # register new codec for slugification
from cached_property import cached_property
from plumbum import LocalPath
from adfd.utils import ContentGrabber, ContentDumper

log = logging.getLogger(__name__)


class Article(object):
    CONTENTS_PATH = LocalPath(__file__).up(2) / 'content'
    SRC_PATH = CONTENTS_PATH
    PROCESSED_PATH = CONTENTS_PATH / 'processed'
    PUNCT = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')

    def __init__(self, identifier, slugPrefix=''):
        self.slugPrefix = slugPrefix.lower()
        if isinstance(identifier, int):
            originalIdentifer = identifier
            self.isImported = True
            self.identifier = "%05d" % (identifier)
            self.srcPath = self.SRC_PATH / 'imported' / self.identifier
            self.ensure_is_imported(originalIdentifer)
        else:
            self.isImported = False
            self.identifier = identifier
            self.srcPath = self.SRC_PATH / 'static'
        log.debug("article %s/%s", self.srcPath, self.identifier)
        self.metadataDict = self.fetch_metadata_dict()

    def __repr__(self):
        return u'<%s %s>' % (self.__class__.__name__, self.slug)

    @property
    def structuralRepresentation(self):
        return tuple(["/%s/" % (self.slug), self.linktext])

    @property
    def linktext(self):
        try:
            return self.metadataDict['linktext']

        except KeyError:
            return self.metadataDict['title']

    @property
    def slug(self):
        try:
            return self.metadataDict['slug']

        except KeyError:
            return self.slugify(self.metadataDict['title'])

    def slugify(self, title):
        words = []
        for word in self.PUNCT.split(title.lower()):
            word = word.encode('translit/long')
            if word:
                words.append(word)
        return u'-'.join(words)

    def fetch_metadata_dict(self):
        """only using first found metadata for now ..."""
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
        content = "\n".join(contents)
        return ArticleContent(content).asHTml

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
            raise Exception("article %s not found", identifier)

    def process(self):
        """writes changed slug back into the file"""
        if self.slugPrefix:
            self.metadataDict['slug'] = "%s/%s" % (self.slugPrefix, self.slug)

        newDict = "\n".join(
            [".. %s: %s" % (key, value) for key, value
             in self.metadataDict.items()])
        try:
            os.makedirs(str(self.PROCESSED_PATH))
        except OSError:
            pass
        metadataDstPath = (self.PROCESSED_PATH / (self.identifier + '.meta'))
        ContentDumper(metadataDstPath, newDict).dump()
        articleDstPath = (self.PROCESSED_PATH / (self.identifier + '.bb'))
        ContentDumper(articleDstPath, self.content).dump()


class ArticleContent(object):
    def __init__(self, rawBbcode):
        self.rawBbcode = rawBbcode

    @cached_property
    def toc(self):
        raise NotImplementedError

    @cached_property
    def structure(self):
        raise NotImplementedError

    @cached_property
    def sections(self):
        pass

    @cached_property
    def asHTml(self):
        raise NotImplementedError
