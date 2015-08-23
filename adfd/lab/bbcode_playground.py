from __future__ import print_function

from plumbum import LocalPath
from adfd.adfd_parser import AdfdParser, Paragrafenreiter, AdfdPrimer

HERE = LocalPath(__file__).up()
kitchenSinkPath = HERE.up(2) / 'content' / 'static' / 'kitchen-sink.bb'
specialPath = HERE / 'special.bb'
pgPath = HERE / 'bbcode-playground.bb'


def special_lab():
    # text = specialPath.read().decode('utf-8')
    text = pgPath.read().decode('utf-8')
    print(text)
    print('##')
    primer = AdfdPrimer(text)
    primedText = primer.primedText
    print(primedText)


def write_html():
    text = kitchenSinkPath.read().decode('utf-8')
    parser = AdfdParser()
    # tokens = parser.tokenize(text)
    # tokens = parser.fix_whitespace(tokens)
    # for token in tokens:
    #     print(token)
    html = parser.format(text)
    print(html)
    (HERE / 'out.html').write(html.encode('utf-8'))


if __name__ == '__main__':
    special_lab()
    # write_html()
