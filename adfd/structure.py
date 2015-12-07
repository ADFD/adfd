import logging

from cached_property import cached_property
from plumbum import LocalPath

from adfd.conf import PATH
from adfd.content import PageMetadata, CategoryMetadata
from adfd.cst import EXT, NAME
from adfd.utils import ContentGrabber, id2name, obj_attr

log = logging.getLogger(__name__)


class WRAP(object):
    MAIN = '<ul class="dropdown menu" data-dropdown-menu>\n%s\n</ul>\n'
    SUB = '<li><a>%s</a><ul class="menu"><ul class="menu">\n%s\n</ul></li>\n'
    ELEM = '<li><a href="%s">%s</a></li>\n'


class ContentElement(object):
    ROOT = PATH.CNT_FINAL

    def __init__(self, path=''):
        if path.startswith(self.ROOT):
            self.catPath = path
        else:
            self.catPath = self.ROOT / path
        if not self.catPath.isdir():
            self.catPath = self.catPath.dirname

    def __repr__(self):
        return "%s" % (obj_attr(self))

    def find_pages(self):
        pages = []
        for path in self.catPath.list():
            if path.isfile() and path.endswith(EXT.OUT):
                pages.append(Page(path=path))
        return pages

    def find_categories(self):
        categories = []
        for path in self.catPath.list():
            if path.isdir():
                categories.append(Category(path))
        return categories


class Category(ContentElement):
    def __init__(self, path=''):
        super().__init__(path)

    @cached_property
    def indexPage(self):
        return Page(path=(self.catPath / 'index').with_suffix(EXT.OUT))

    @cached_property
    def md(self):
        path = (self.catPath / NAME.CATEGORY).with_suffix(EXT.META)
        return CategoryMetadata(path)

    @cached_property
    def contents(self):
        return NotImplemented


class Page(ContentElement):
    def __init__(self, topicId=None, path=LocalPath('')):
        assert topicId or path
        if topicId:
            if isinstance(topicId, str):
                topicId = int(topicId)
            self.topicId = topicId
            name = id2name(self.topicId)
            log.debug('look for topicId %s', name)
            for path in (self.ROOT / path).walk():
                if name in path:
                    path = path.dirname
                    break

            else:
                raise PageNotFound()

            self.basePath = path / name
        else:
            self.basePath = self.ROOT / path
        super().__init__(self.basePath)
        self.cntPath = self.basePath.with_suffix(EXT.OUT)
        self.pageMdPath = self.basePath.with_suffix(EXT.META)

    @cached_property
    def content(self):
        return ContentGrabber(self.cntPath).grab()

    @cached_property
    def md(self):
        """metadata of this page"""
        return PageMetadata(self.pageMdPath)


class PageNotFound(Exception):
    pass


def traverse_content_elements(element=Category(), depth=1):
    def indent():
        print(' ' * 4 * depth, end='')

    for category in element.find_categories():
        indent()
        print('cat:', category.md.name, 'indexPage:',
              category.indexPage.md.title)
        traverse_content_elements(category, depth + 1)
    for page in element.find_pages():
        indent()
        print('page:', page.md.title)
    print('#' * 100)


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    # traverse_content_elements()
    # c = ContentElement()
    # print(c.find_categories())
    # print(c.find_pages())
    # print(obj_attr(p))
    # print(get_structure(STRUCTURE))
    p1 = Page(10068)
    # p2 = Page(path=LocalPath('bbcode/10068.html'))
    # print(obj_attr(p1))
    # print(obj_attr(p2))
    # print(obj_attr(p1, excludeAttrs=['content']))
    # print(obj_attr(p2, excludeAttrs=['content']))
