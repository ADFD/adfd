from __future__ import print_function

from plumbum import LocalPath
from adfd.adfd_parser import AdfdParser


HERE = LocalPath(__file__).up()
kitchenSinkPath = HERE.up(2) / 'sources' / 'static' / 'kitchen-sink.bb'
specialPath = HERE / 'special.bb'
pgPath = HERE / 'bbcode-playground.bb'


def special_lab():
    text = specialPath.read().decode('utf-8')
    parser = AdfdParser()
    tokens = parser.tokenize(text)
    for token in tokens:
        print(token)
    html = parser.format(text)
    print(html)


def token_lab():
    text = kitchenSinkPath.read().decode('utf-8')
    parser = AdfdParser()
    tokens = parser.tokenize(text)
    text = parser.add_paragraph_tags(tokens)
    print(text)


def write_html():
    text = kitchenSinkPath.read().decode('utf-8')
    parser = AdfdParser()
    tokens = parser.tokenize(text)
    tokens = parser.fix_whitespace(tokens)
    for token in tokens:
        print(token)
    html = parser.format(text)
    print(html)
    (HERE / 'out.html').write(html.encode('utf-8'))


if __name__ == '__main__':
    # special_lab()
    # token_lab()
    write_html()
