import logging
from functools import total_ordering

from cached_property import cached_property

from adfd.conf import PATH
from adfd.content import PageMetadata, CategoryMetadata
from adfd.cst import EXT, NAME
from adfd.utils import ContentGrabber, obj_attr

log = logging.getLogger(__name__)


class CatDesc(object):
    """describe a category and it's contents"""
    def __init__(self, name, mainTopicId, contents):
        self.name = name
        self.mainTopicId = mainTopicId
        self.contents = contents


@total_ordering
class Container(object):
    ROOT = PATH.CNT_FINAL

    def __init__(self, path):
        self.basePath = self.ROOT / path
        self.relPath = str(self.basePath).split(self.ROOT)[-1]

    def __repr__(self):
        return "%s" % (obj_attr(self))

    def __gt__(self, other):
        return self.weight > other.weight

    @cached_property
    def name(self):
        try:
            return self.md.name

        except AttributeError:
            return self.md.title

    @cached_property
    def weight(self):
        return self.md.weight

    @cached_property
    def isValidContainer(self):
        return self.basePath.isdir()

    @cached_property
    def isCategory(self):
        catMetaPath = (self.basePath / NAME.CATEGORY).with_suffix(EXT.META)
        return self.isValidContainer and catMetaPath.exists()

    @cached_property
    def isPage(self):
        return self.isValidContainer and not self.isCategory

    def find_categories(self):
        return self._find_elems('isCategory', Category)

    def find_pages(self):
        return self._find_elems('isPage', Page)

    def _find_elems(self, checkAttr, Klass):
        elems = []
        for path in self.basePath.list():
            if getattr(Container(path), checkAttr):
                elems.append(Klass(path=path))
        return sorted(elems)


class Category(Container):
    def __init__(self, path=''):
        super().__init__(path)

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.md.name)

    @cached_property
    def mainPage(self):
        return Page(self.basePath)

    @cached_property
    def md(self):
        path = (self.basePath / NAME.CATEGORY).with_suffix(EXT.META)
        return CategoryMetadata(path)


class Page(Container):
    def __init__(self, path):
        self.basePath = self.ROOT / path
        super().__init__(self.basePath)
        idxPath = self.basePath / NAME.INDEX
        self.cntPath = idxPath.with_suffix(EXT.OUT)
        self.pageMdPath = idxPath.with_suffix(EXT.META)

    @cached_property
    def content(self):
        return ContentGrabber(self.cntPath).grab()

    @cached_property
    def md(self):
        return PageMetadata(self.pageMdPath)


class PageNotFound(Exception):
    pass


class Navigator:
    MAIN = ('<ul class="dropdown menu" data-dropdown-menu>', '</ul>')
    STIT = ('<a>', '</a>')
    SUB = ('<ul class="menu">', '</ul>')
    ELEM = ('<li><a href="%s">%s', '</a></li>')

    def __init__(self, root=Category()):
        self.root = root
        self.depth = 1

    def traverse(self):
        self._traverse(self.root)

    def _traverse(self, element):
        if self.depth == 1:
            self.prindent(self.MAIN[0])
        else:
            self.prindent('<ul class="menu">')
        self.depth += 1
        for cat in element.find_categories():
            self.prindent('%s%s%s' % (self.STIT[0], cat.name, self.STIT[0]))
            self._traverse(cat)
        for page in element.find_pages():
            elem = self.ELEM[0] % (page.relPath, page.name)
            self.prindent('%s%s' % (elem, self.ELEM[1]))
            self.prindent('<li><a href="#">%s</a></li>' % (page.name))
        self.depth -= 1
        self.prindent(self.MAIN[1])

    def prindent(self, text):
        print(' ' * 4 * self.depth, text)

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    Navigator().traverse()

    # fixme turn this into tests ...
    exit()
    c = Container('hintergruende/geschichte')
    print(c.isCategory)
    print(c.isPage)
    # print(c.find_categories())
    for cat in c.find_categories():
        print(cat.name, cat.md.weight)
    for cat in c.find_pages():
        print(cat.name, cat.md.weight)

        # print(c.isPage)
    # print(c.find_categories())
    # print(c.find_pages())
    # print(obj_attr(p))
    # p = Page(path=LocalPath('bbcode'))
    # p = Page(path=LocalPath('bbcode/spezielle-bbcode-formatierungen'))
    # print(obj_attr(p))
    # print(obj_attr(p, excludeAttrs=['content']))
    # print(obj_attr(p2, excludeAttrs=['content']))
