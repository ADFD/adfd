# -*- coding: utf-8 -*-
from collections import OrderedDict
import logging
import re

# noinspection PyUnresolvedReferences
import translitcodec  # This registers new codecs for slugification

from plumbum import LocalPath
from adfd.utils import ContentGrabber


log = logging.getLogger(__name__)


class Article(object):
    ARTICLES_PATH = LocalPath(__file__).up(2) / 'content'
    PUNCT = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')

    def __init__(self, identifier, slugPrefix=None):
        if isinstance(identifier, int):
            self.isImported = True
            self.identifier = "%05d" % (identifier)
            self.rootPath = self.ARTICLES_PATH / 'imported' / self.identifier
        else:
            self.isImported = False
            self.identifier = identifier
            self.rootPath = self.ARTICLES_PATH / 'static'
        self.metadataDict = self.fetch_metadataDict()
        self.persist_slug_prefix(slugPrefix)

    def __repr__(self):
        return u'<%s %s>' % (self.__class__.__name__, self.slug)

    @property
    def slug(self):
        try:
            return self.metadataDict['slug']

        except KeyError:
            return self.slugify(self.metadataDict['title'])

    def slugify(self, title):
        result = []
        for word in self.PUNCT.split(title.lower()):
            word = word.encode('translit/long')
            if word:
                result.append(word)
        return u'-'.join(result)

    def persist_slug_prefix(self, slugPrefix):
        """writes changed slug back into the file"""
        dirty = False
        slug = self.slug
        if not slugPrefix:
            dirty = True
            slug = slug.split('/')[-1]
            self.metadataDict['slug'] = slug
        elif not slug.startswith(slugPrefix):
            dirty = True
            self.metadataDict['slug'] = "%s/%s" % (slugPrefix, slug)
        if dirty:
            newDict = "\n".join(
                [".. %s: %s" % (key, value) for key, value
                 in self.metadataDict.items()])
            self.metadataPaths[0].write(newDict)

    def fetch_metadataDict(self):
        """only using first found metadata for now ..."""
        metadata = ContentGrabber(absPath=self.metadataPaths[0]).grab()
        metadataDict = OrderedDict()
        for line in metadata.split('\n'):
            if not line.strip():
                break

            key, value = line[3:].split(': ')
            metadataDict[key.strip()] = value.strip()
        return metadataDict

    @property
    def content(self):
        contents = []
        for path in self.contentFilePaths:
            contents.append(ContentGrabber(absPath=path).grab())
        return "\n".join(contents)

    @property
    def contentFilePaths(self):
        if self.isImported:
            return [p for p in self._postPaths if str(p).endswith('.bb')]

        return [self.rootPath / (self.identifier + '.bb')]

    @property
    def metadataPaths(self):
        if self.isImported:
            return [p for p in self._postPaths if str(p).endswith('.meta')]

        return [self.rootPath / (self.identifier + '.meta')]

    @property
    def _postPaths(self):
        return sorted([p for p in self.rootPath.list()])
