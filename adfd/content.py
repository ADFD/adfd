# -*- coding: utf-8 -*-
import logging

from cached_property import cached_property

from adfd.bbcode import AdfdParser
from adfd.cst import PATH, PARSE, EXT, NAME
from adfd.exc import *
from adfd.metadata import CategoryMetadata, PageMetadata
from adfd.utils import (
    dump_contents, ContentGrabber, get_paths, slugify_path, id2name, slugify)


log = logging.getLogger(__name__)


class ContentWrangler:
    """Thin wrapper with housekeeping to do the whole dance"""
    @classmethod
    def wrangle_content(cls):
        cls.export_topics_from_db()
        cls.prepare_topics()
        cls.finalize_articles()

    @staticmethod
    def export_topics_from_db():
        from adfd.db.export import harvest_topic_ids, export_topics
        from adfd.site_description import SITE_DESCRIPTION

        PATH.CNT_RAW.delete()
        export_topics(harvest_topic_ids(SITE_DESCRIPTION))

    @staticmethod
    def prepare_topics():
        PATH.CNT_PREPARED.delete()
        prepare_topics(PATH.CNT_RAW, PATH.CNT_PREPARED)

    @staticmethod
    def finalize_articles():
        from adfd.site_description import SITE_DESCRIPTION

        PATH.CNT_FINAL.delete()
        GlobalFinalizer.finalize(SITE_DESCRIPTION)


class RawPost:
    def __init__(self, path):
        self.content = ContentGrabber(path).grab()
        self.md = PageMetadata(path.with_suffix(EXT.META))
        self.postId = int(self.md.postId)


class TopicPreparator:
    """Take exported files of a topic and prepare them for HTML conversion"""

    def __init__(self, path, dstPath):
        self.path = path
        sourcePaths = get_paths(self.path, EXT.IN)
        if not sourcePaths:
            raise TopicNotFound(self.path)

        self.rawPosts = [RawPost(path) for path in sourcePaths]
        self.mergedMd = self.merge_metadata()
        if self.mergedMd.includePosts and self.mergedMd.excludePosts:
            raise MutuallyExclusiveMetadata('either include or exclude posts')

        filename = id2name(self.mergedMd.topicId)
        self.cntDstPath = dstPath / (filename + EXT.IN)
        self.mdDstPath = dstPath / (filename + EXT.META)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.path)

    @property
    def content(self):
        """merge contents from topic files into one file"""
        contents = []
        for rawPost in self.rawPosts:
            if self.post_is_excluded(rawPost.postId):
                continue

            content = ''
            if self.mergedMd.useTitles:
                content += PARSE.TITLE_PATTERN % (self.mergedMd.title)
            contents.append(rawPost.content)
        return "\n\n".join(contents)

    def post_is_excluded(self, postId):
        def str_to_ints(posts):
            return [int(p) for p in posts.split(',')]

        assert isinstance(postId, int)
        if self.mergedMd.includePosts:
            if postId not in str_to_ints(self.mergedMd.includePosts):
                log.info("post %s is not explicitly included", postId)
                return True

        if self.mergedMd.excludePosts:
            if postId in str_to_ints(self.mergedMd.excludePosts):
                log.info("post %s is explicitly excluded", postId)
                return True

    def prepare(self):
        dump_contents(self.cntDstPath, self.content)
        self.mergedMd.dump(self.mdDstPath)

    def merge_metadata(self):
        """
        * merge in [meta] from content (and write back)
        * merge metadata from all posts new -> old (oldest/first post wins)

        :returns: PageMetadata
        """
        md = PageMetadata()
        for rawPost in reversed(self.rawPosts):
            assert isinstance(rawPost, RawPost)
            rawPost.md.populate_from_text(rawPost.content)
            rawPost.md.dump()
            md.populate_from_kwargs(rawPost.md.asDict)
        return md


class TopicFinalizer:
    """Convert topic to final format (usually HTML)"""
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
            hyphenate=True, typogrify=False).to_html
        return parse_func(self.inContent)


class GlobalFinalizer:
    """After all this mangling and wrangling dump the final results"""
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
        for idx, elem in enumerate(desc.contents, start=1):
            if isinstance(elem, int):
                log.info('topic %s in %s is "%s"', idx, relPath, elem)
                TopicFinalizer(elem, relPath, idx).finalize()
            else:
                cls._finalize_recursive(elem, relPath, weight + idx)

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
