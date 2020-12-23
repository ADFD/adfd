import re
from functools import total_ordering

from bs4 import BeautifulSoup

from adfd.model import ArticleNode


@total_ordering
class HeaderTag:
    HIGHEST_LEVEL = 2

    def __init__(self, tag):
        self.tag = tag
        self.level = int(tag.name[1:])
        self.parent = None
        self.children = []

    def find_parent(self):
        curPar = self.parent
        if not curPar:
            return None

        while abs(curPar.level - self.level) > 1:
            curPar = curPar.parent
        return curPar

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.tag.name})>"

    def __str__(self):
        return "### %s ###" % self.tag

    def __gt__(self, other):
        return self.level < other.level

    def is_ancestor_of(self, tag):
        return self.level < tag.level

    def is_sibling_of(self, tag):
        return self.level == tag.level

    def is_child_of(self, tag):
        return self.level == tag.level + 1

    def is_grandchild_of(self, tag):
        return self.level == tag.level + 2

    def is_sane(self, tag):
        return (
            self.is_child_of(tag) or self.is_ancestor_of(tag) or self.is_sibling_of(tag)
        )


class InPageNav:
    def __init__(self, soup):
        self.soup = soup
        self.topHeaders = []
        self.currentHeader = None

    def inPageNav(self):
        return "".join([str(m) for m in self.topHeaders])

    def create_in_page_nav(self):
        for tag in self.soup.body:
            if tag.name and re.match(r"h\d", tag.name):
                print(tag.name)
                self.attach(HeaderTag(tag))

    def attach(self, ht):
        """:type ht: HeaderTag"""
        if not self.topHeaders:
            self.topHeaders.append(ht)
            self.currentHeader = ht
        else:
            if ht.is_child_of(self.currentHeader):
                ht.parent = self.currentHeader
                self.currentHeader.children.append(ht)
            elif ht.is_grandchild_of(self.currentHeader):
                self.currentHeader = self.currentHeader.children[-1]
                self.currentHeader.children.append(ht)
            elif ht.is_sibling_of(self.currentHeader):
                if ht.level == HeaderTag.HIGHEST_LEVEL:
                    self.topHeaders.append(ht)
                    self.currentHeader = ht
                elif self.currentHeader == ht:
                    self.currentHeader.children.append(ht)
            elif ht.is_ancestor_of(self.currentHeader):
                parent = ht.find_parent()
                if parent:
                    self.currentHeader = parent
                    parent.children.append(ht)
                else:
                    self.currentHeader = ht
                    self.topHeaders.append(ht)
            else:
                raise Exception("%s %s", self.currentHeader, ht)


if __name__ == "__main__":
    n = ArticleNode("Bbcode structure | articles/structure.bbcode")
    ipn = InPageNav(BeautifulSoup(n.html, "html5lib"))
    ipn.create_in_page_nav()
    print(ipn)
