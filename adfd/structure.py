import logging

from cached_property import cached_property

from adfd.conf import PATH
from adfd.content import PageMetadata, CategoryMetadata
from adfd.cst import EXT, NAME
from adfd.utils import ContentGrabber, id2name, obj_attr, slugify

log = logging.getLogger(__name__)


class WRAP(object):
    MAIN = '<ul class="dropdown menu" data-dropdown-menu>\n%s\n</ul>\n'
    SUB = '<li><a>%s</a><ul class="menu"><ul class="menu">\n%s\n</ul></li>\n'
    ELEM = '<li><a href="%s">%s</a></li>\n'


class Category(object):
    ROOT = PATH.CNT_FINAL

    def __init__(self, name):
        self.name = name
        self.cleanName = slugify(self.name)

    @cached_property
    def mainPage(self):
        return Page(self.md.mainTopicId)

    @cached_property
    def md(self):
        return CategoryMetadata(self.path / (NAME.CATEGORY + EXT.META))

    @cached_property
    def path(self):
        for path in self.ROOT.walk():
            if path.isdir() and self.cleanName in path:
                return path


class Page(object):
    ROOT = PATH.CNT_FINAL

    def __init__(self, topicId):
        if isinstance(topicId, str):
            topicId = int(topicId)
        self.topicId = topicId
        self.name = id2name(self.topicId)
        self.cntPath = self.catPath / (self.name + EXT.OUT)
        self.pageMdPath = self.catPath / (self.name + EXT.META)
        self.catMdPath = self.catPath / (NAME.CATEGORY + EXT.META)

    @cached_property
    def catPath(self):
        """path to the folder all articles of this category live in"""
        for path in self.ROOT.walk():
            if self.name in path:
                return path.dirname

    @cached_property
    def content(self):
        return ContentGrabber(self.cntPath).grab()

    @cached_property
    def pageMd(self):
        """metadata of this page"""
        return PageMetadata(self.pageMdPath)

    @property
    def catMd(self):
        """metadata of this category"""
        return CategoryMetadata(self.catMdPath)


if __name__ == '__main__':
    p = Category('Hintergründe')
    print(obj_attr(p))
    # p = Page(10694)
    # print(obj_attr(p))
