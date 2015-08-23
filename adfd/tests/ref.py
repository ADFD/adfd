from bs4 import BeautifulSoup, NavigableString
from adfd.adfd_parser import AdfdParser
from test_adfd_parser import get_pairs
from test_adfd_primer import get_text


def with_pairs():
    for fName, src, exp in get_pairs():
        # if 'ordered-list' not in fName:
        #     continue

        parser = AdfdParser()
        print fName
        result = parser.format(src)
        print result
        print '#' * 80


def soup():
    data = get_text('kitchen-sink')
    parser = AdfdParser()
    rawHtmlStr = parser.format(data)
    # print rawHtmlStr
    # print '*' * 80
    # print '*' * 80
    # print '*' * 80
    bs = BeautifulSoup(rawHtmlStr, 'lxml')
    child = bs.body.children.next()
    while child:
        # if isinstance(child, NavigableString):
        print "#%s#%s##" % (type(child), child)
        child = child.next_sibling

    # if isinstance(d, NavigableString):
    #     print d, type(d)
    #     print '#' * 80
    # print rawHtmlStr
    # print '#' * 80
    # print parser.pretty_print_html(rawHtmlStr)


if __name__ == '__main__':
    soup()
