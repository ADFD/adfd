from collections import OrderedDict

from bs4 import BeautifulSoup, Tag


class AdfdPostProcessor(object):
    def __init__(self, text):
        self.text = text
        self.soup = BeautifulSoup(text, 'lxml')

    @property
    def processedText(self):
        self.wrap_sections()
        return self.soup.prettify()

    def wrap_sections(self):
        body = self.soup.find('body')
        children = list(body.children)
        currentKey = children[0]
        sectionMap = OrderedDict({currentKey: None})
        currentSectionTags = []
        for child in children[1:]:
            if type(child) == Tag and (re.match("h\d", child.name)):
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
            sectionTag = self.soup.new_tag('section')
            sectionStarter.wrap(sectionTag)
            for elem in items:
                sectionTag.append(elem)

if __name__ == '__main__':
    text = (
        "<h1>bla</h1>sdfgdfg http://asddf.org asdf \nasdsd\n"
        "<h2>bla</h2>qwewerqer sdfgg httpf \nasdsd\n"
    )
    app = AdfdPostProcessor(text)
    app.wrap_sections()
    # print app.processedText
    soup = app.soup
    for headerTag in soup.find_all(re.compile("h\d")):
        print headerTag
        print headerTag.parent
