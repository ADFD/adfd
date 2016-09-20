import logging

from cached_property import cached_property

from adfd.cnt.parse import AdfdParser
from adfd.cnt.metadata import CategoryMetadata, PageMetadata
from adfd.cst import PATH, PARSE, EXT, NAME
from adfd.utils import (
    dump_contents, ContentGrabber, slugify_path, id2name, slugify)


log = logging.getLogger(__name__)


# FIXME obsolete - for reference
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
        return AdfdParser(
            hyphenate=False, typogrify=False).to_html(self.inContent)


# FIXME make this fetch from SiteStructure (or throw away completely)
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
        # TODO this has to be handled differently to also work in live view
        # e.g. fetch index from SiteDesc Class
        # a lot of stuff should actually move from files into SiteDesc
        # SiteDesc could be serialized into one file instead of having many
        # TopicFinalizer(desc.mainTopicId, relPath, isCategory=True).finalize()
        # cls.dump_cat_md(desc.name, relPath,
        #                 mainTopicId=desc.mainTopicId, weight=weight)
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
