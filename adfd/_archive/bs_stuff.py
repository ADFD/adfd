from collections import OrderedDict
import re
from bs4 import BeautifulSoup, Tag

from adfd.adfd_parser import AdfdParser


# def wrap_stuff():
#     print "\n".join([unicode(c) for c in list(body.children)])
#     for c in body.contents:
#         ctype = type(c)
#         print ctype, ctype == NavigableString
#         if ctype == NavigableString:
#             c.wrap(soup.new_tag('p'))
#         print "###%s###" % (c)
#         print
from adfd.utils import DataGrabber


def bs(text):
    # print text
    soup = BeautifulSoup(text, 'lxml')
    body = soup.find('body')
    # print body.prettify()
    # print '#' * 80
    children = list(body.children)
    currentKey = children[0]
    sectionMap = OrderedDict({currentKey: None})
    currentSectionTags = []
    for child in children[1:]:
        if type(child) == Tag and (re.match("h\d", child.name)):
            # print child
            if currentSectionTags:
                sectionMap[currentKey] = currentSectionTags
            currentKey = child
            sectionMap[currentKey] = None
            currentSectionTags = []
        else:
            currentSectionTags.append(child)
    sectionMap[currentKey] = currentSectionTags

    for sectionStarter, items in sectionMap.items():
        print sectionStarter, items
        sectionTag = soup.new_tag('section')
        sectionStarter.wrap(sectionTag)
        for elem in items:
            sectionTag.append(elem)

    # pprint.pprint(sections)
    print soup.prettify()
    exit()

    firstTopElement = list(body.children)[0]

    allTopElements = [firstTopElement] + firstTopElement.find_next_siblings()
    for e in allTopElements:
        print e

    print body.prettify()


if __name__ == '__main__':
    # text = "http://adfd.org simple paragraph should be wrapped in p tags."
    text = DataGrabber('1-structure.bb').grab()
    text = AdfdParser().format(text)
    bs(text)
