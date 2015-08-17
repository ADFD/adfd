from __future__ import print_function

from plumbum import LocalPath
from adfd.adfd_parser import AdfdParser


if __name__ == '__main__':
    HERE = LocalPath(__file__).up()
    kitchenSinkPath = HERE.up(2) / 'sources' / 'static' / 'kitchen-sink.bb'
    pgPath = HERE / 'bbcode-playground.bb'
    usedPath = kitchenSinkPath

    text = usedPath.read().decode('utf-8')
    parser = AdfdParser()
    html = parser.format(text)
    print(html)
    (HERE / 'out.html').write(html.encode('utf-8'))
