# -*- coding: utf-8 -*-
import logging
import re
import plumbum


log = logging.getLogger(__name__)


class ENC(object):
    OUT = 'utf-8'  # used to encode bytes


class Article(object):
    ARTICLES_PATH = plumbum.LocalPath(__file__).up(2) / 'content' / 'static'
    PUNCT = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')

    def __init__(self, identifier):
        if isinstance(identifier, int):
            identifier = "imported/%05d" % (identifier)
        self.contentPath = self.ARTICLES_PATH / (identifier + '.bb')
        self.metadataPath = self.ARTICLES_PATH / (identifier + '.meta')

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
            return unicode(u'-'.join(result))

    @property
    def metadataDict(self):
        metadata = self.metadataPath.read().decode(ENC.OUT)
        metadataDict = {}
        for line in metadata.split('\n'):
            if not line.strip():
                break

            key, value = line[3:].split(': ')
            metadataDict[key.strip()] = value.strip()
        return metadataDict

    @property
    def content(self):
        text = self.contentPath.read().decode(ENC.OUT)
        return text

    @property
    def contentFiles(self):
        return
