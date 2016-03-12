# -*- coding: utf-8 -*-
import logging

from cached_property import cached_property

from adfd.bbcode import AdfdParser
from adfd.conf import PATH, PARSE
from adfd.cst import EXT, NAME, DB_URL
from adfd.db.phpbb_classes import Topic
from adfd.exc import TopicDoesNotExist, TopicNotFound
from adfd.metadata import CategoryMetadata, PageMetadata
from adfd.utils import (
    dump_contents, ContentGrabber, get_paths, slugify_path, id2name, slugify)

log = logging.getLogger(__name__)


class GlobalFinalizer:
    @classmethod
    def finalize(cls, siteDescription):
        cls._finalize_recursive(siteDescription)

    @classmethod
    def _finalize_recursive(cls, desc, pathPrefix='', weight=1):
        relPath = desc.name
        if pathPrefix:
            relPath = "%s/%s" % (pathPrefix, desc.name)
        log.info('main topic in "%s" is %s', relPath, desc.mainTopicId)
        TopicFinalizer(desc.mainTopicId, relPath, isCategory=True).finalize()
        cls.dump_cat_md(desc.name, relPath,
                        mainTopicId=desc.mainTopicId, weight=weight)
        if isinstance(desc.contents, tuple):
            for idx, dsc in enumerate(desc.contents, start=1):
                cls._finalize_recursive(dsc, relPath, weight + idx)
        else:
            assert isinstance(desc.contents, list), desc.contents
            for tWeight, topicId in enumerate(desc.contents, start=1):
                log.info('topic %s in %s is "%s"', tWeight, relPath, topicId)
                TopicFinalizer(topicId, relPath, tWeight).finalize()

    @staticmethod
    def dump_cat_md(name, relPath, **kwargs):
        relPath = slugify_path(relPath)
        kwargs.update(name=name)
        path = (PATH.CNT_FINAL / relPath / NAME.CATEGORY).with_suffix(EXT.META)
        CategoryMetadata(kwargs=kwargs).dump(path)


def prepare_topics(srcPath, dstPath):
    for path in [p for p in srcPath.list() if p.isdir()]:
        log.info('prepare %s', path)
        TopicPreparator(path, dstPath).prepare()


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
        parse_func = PARSE.FUNC or AdfdParser(
            hyphenate=False, typogrify=False).to_html
        return parse_func(self.inContent)


class ContentWrangler:
    @classmethod
    def wrangle(cls):
        cls.export_topics_from_db()
        cls.prepare_topics()
        cls.finalize_articles()

    @staticmethod
    def export_topics_from_db():
        from adfd.site_description import SITE_DESCRIPTION

        PATH.CNT_RAW.delete()
        log.debug('use db at %s', DB_URL)
        RawTopicsExporter(siteDescription=SITE_DESCRIPTION).export()

    @staticmethod
    def prepare_topics():
        PATH.CNT_PREPARED.delete()
        prepare_topics(PATH.CNT_RAW, PATH.CNT_PREPARED)

    @staticmethod
    def finalize_articles():
        from adfd.site_description import SITE_DESCRIPTION

        PATH.CNT_FINAL.delete()
        GlobalFinalizer.finalize(SITE_DESCRIPTION)


class RawTopicsExporter:
    """Read all given topics from DB into raw file"""

    def __init__(self, topicIds=None, siteDescription=None):
        self.allTopicIds = set(topicIds or [])
        if siteDescription:
            self._harvest_topics_recursive(siteDescription)

        self.topics = []
        """:type: list of Topic"""
        for topicId in self.allTopicIds:
            try:
                self.topics.append(Topic(topicId))
            except TopicDoesNotExist:
                log.warning('topic %s is broken', topicId)

    def export(self):
        for topic in self.topics:
            self._export_topic(topic)

    def _harvest_topics_recursive(self, content):
        self.allTopicIds.add(content.mainTopicId)
        for content in content.contents:
            if isinstance(content, int):
                self.allTopicIds.add(content)
            else:
                self._harvest_topics_recursive(content)

    def _export_topic(self, topic):
        topicPath = PATH.CNT_RAW / id2name(topic.id)
        log.info('%s -> %s', topic.id, topicPath)
        for post in topic.posts:
            current = "%s" % (post.subject)
            log.debug("export: %s", current)
            contentPath = topicPath / (post.filename + EXT.IN)
            dump_contents(contentPath, post.content)
            metadataPath = topicPath / (post.filename + EXT.META)
            dump_contents(metadataPath, post.md.asFileContents)
