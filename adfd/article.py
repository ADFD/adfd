# -*- coding: utf-8 -*-
import logging
import re
import plumbum

log = logging.getLogger(__name__)


class ENC(object):
    IN = 'cp1252'  # used to decode input to bytes
    OUT = 'utf-8'  # used to encode bytes
    ALL = [IN, OUT]


class Article(object):
    HERE = plumbum.LocalPath(__file__).up()
    ARTICLES_PATH = HERE / 'sources' / 'articles'
    PUNCT = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')

    def __init__(self, relPath):
        self.path = self.ARTICLES_PATH / relPath

    # fixme know completely oboslete?
    def url_refers_to_this(self, url):
        # fixme ambivalent - use relPath without extension instead od slug
        return self.slug in url

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

    # fixme fetch from extra meta file instead now
    @property
    def metadataDict(self):
        metadataDict = {}
        for line in self.content.split('\n'):
            if not line.strip():
                break

            key, value = line[3:].split(': ')
            metadataDict[key.strip()] = value.strip()
        return metadataDict

    @property
    def content(self):
        text = self.path.read().decode(ENC.OUT)
        return text

    @property
    def target(self):
        return str(self.fileName).split('.')[-1]

    @property
    def fileName(self):
        return self.path.basename
