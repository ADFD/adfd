import json
import logging
from collections import OrderedDict

from cached_property import cached_property
from plumbum import LocalPath

from adfd.conf import PATH
from adfd.content import PageMetadata, CategoryMetadata
from adfd.cst import EXT, NAME
from adfd.utils import ContentGrabber, id2filename, obj_attr

log = logging.getLogger(__name__)


class Structure(object):
    """fetch structure from meta data in finalized files"""
    def __init__(self, rootPath, structureDstPath):
        self.rootPath = LocalPath(rootPath)
        self.structureDstPath = structureDstPath

    def dump_structure(self):
        pageMap = self.create_page_map(self.rootPath)
        self.jsonify_structure(pageMap)

    @classmethod
    def create_page_map(cls, rootPath):
        pages = OrderedDict()
        for path in rootPath.walk(lambda n: n.endswith(EXT.META)):
            md = PageMetadata(path=path)
            curDict = None
            for part in md.relPath.split('/'):
                if part not in pages:
                    pages[part] = OrderedDict()
                curDict = pages[part]
            # noinspection PyUnboundLocalVariable
            curDict[part] = md.relFilePath
        return pages

    def jsonify_structure(self, pageMap):
        log.debug(str(pageMap))
        with open(self.structureDstPath, 'w') as fp:
            json.dump(pageMap, fp)


class Category(object):
    ROOT = PATH.CNT_FINAL

    def __init__(self, name):
        self.name = name

    @cached_property
    def mainTopic(self):
        return Page(self.md.mainTopicId)

    @cached_property
    def md(self):
        return CategoryMetadata(self.path / (NAME.CATEGORY + EXT.META))

    @cached_property
    def path(self):
        for path in self.ROOT.walk():
            if path.isdir() and self.name in path:
                return path


class Page(object):
    ROOT = PATH.CNT_FINAL

    def __init__(self, topicId):
        self.topicId = topicId

    @cached_property
    def name(self):
        return id2filename(self.topicId)

    @cached_property
    def contentPath(self):
        return LocalPath(self._partialPathName + EXT.OUT)

    @cached_property
    def mdPath(self):
        return LocalPath(self._partialPathName + EXT.META)

    @cached_property
    def _partialPathName(self):
        for path in self.ROOT.walk():
            if self.name in path:
                return LocalPath(path.rpartition('.')[0])

    @cached_property
    def content(self):
        ContentGrabber(self.contentPath)

    @cached_property
    def md(self):
        return PageMetadata(self.mdPath)


if __name__ == '__main__':
    p = Page(10694)
    print(obj_attr(p))
