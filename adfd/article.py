# -*- coding: utf-8 -*-
import logging
import re
import plumbum
from adfd.utils import ContentGrabber

log = logging.getLogger(__name__)


class ENC(object):
    OUT = 'utf-8'  # used to encode bytes


class Article(object):
    ARTICLES_PATH = plumbum.LocalPath(__file__).up(2) / 'content'
    PUNCT = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')

    def __init__(self, identifier):
        if isinstance(identifier, int):
            self.isImported = True
            self.identifier = "%05d" % (identifier)
            self.rootPath = self.ARTICLES_PATH / 'imported' / self.identifier
        else:
            self.isImported = False
            self.identifier = identifier
            self.rootPath = self.ARTICLES_PATH / 'static'

        # self.contentPath = self.ARTICLES_PATH / (identifier + '.bb')
        # self.metadataPath = self.ARTICLES_PATH / (identifier + '.meta')

    def __repr__(self):
        return u'<%s %s>' % (self.__class__.__name__, self.slug)

    @property
    def slug(self):
        try:
            return self.metadataDict['slug']

        except KeyError:
            title = self.metadataDict['title']
            result = []
            for word in self.PUNCT.split(title.lower()):
                word = word.encode('translit/long')
                if word:
                    result.append(word)
            return u'-'.join(result)

    @property
    def metadataDict(self):
        """only using first found metadata for now ..."""
        metadata = ContentGrabber(absPath=self.metadataPaths[0]).grab()
        metadataDict = {}
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
