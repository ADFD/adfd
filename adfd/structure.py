import logging
from functools import total_ordering

from cached_property import cached_property

from adfd.conf import PATH
from adfd.content import PageMetadata, CategoryMetadata
from adfd.cst import EXT, NAME
from adfd.utils import ContentGrabber, obj_attr

log = logging.getLogger(__name__)


class WRAP(object):
    MAIN = '<ul class="dropdown menu" data-dropdown-menu>\n%s\n</ul>\n'
    SUB = '<li><a>%s</a><ul class="menu"><ul class="menu">\n%s\n</ul></li>\n'
    ELEM = '<li><a href="%s">%s</a></li>\n'


@total_ordering
class Container(object):
    ROOT = PATH.CNT_FINAL

    def __init__(self, path):
        self.basePath = self.ROOT / path

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
        categories = []
        for path in self.basePath.list():
            if Container(path).isCategory:
                categories.append(Category(path=path))
        return sorted(categories)

    def find_pages(self):
        pages = []
        for path in self.basePath.list():
            log.info(path)
            log.info(Container(path).isPage)
            if Container(path).isPage:
                pages.append(Page(path=path))
        return sorted(pages)


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
        self.cntPath = (self.basePath / NAME.INDEX).with_suffix(EXT.OUT)
        self.pageMdPath = (self.basePath / NAME.PAGE).with_suffix(EXT.META)

    @cached_property
    def content(self):
        return ContentGrabber(self.cntPath).grab()

    @cached_property
    def md(self):
        return PageMetadata(self.pageMdPath)


class PageNotFound(Exception):
    pass


def traverse_site(element=Category(), depth=1):
    def indent():
        print(' ' * 4 * depth, end='')

    for category in element.find_categories():
        indent()
        print('cat:', category.md.name, 'mainPage:',
              category.mainPage.md.title)
        traverse_site(category, depth + 1)
    for page in element.find_pages():
        indent()
        print('page:', page.md.title)


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    traverse_site()

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
    # print(get_structure(STRUCTURE))
    # p = Page(path=LocalPath('bbcode'))
    # p = Page(path=LocalPath('bbcode/spezielle-bbcode-formatierungen'))
    # print(obj_attr(p))
    # print(obj_attr(p, excludeAttrs=['content']))
    # print(obj_attr(p2, excludeAttrs=['content']))
