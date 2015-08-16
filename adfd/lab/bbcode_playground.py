from __future__ import print_function

from plumbum import LocalPath
from adfd.adfd_parser import AdfdParser


if __name__ == '__main__':
    HERE = LocalPath(__file__).up()
    pluginFolder = HERE.up(2) / 'plugins' / 'bbcode'
    testFilePath = HERE / 'bbcode-playground.bb'
    outFilePath = HERE / 'bbcode-playground.html'
    text = testFilePath.read().decode('utf-8')
    parser = AdfdParser()
    html = parser.format(text)
    outFilePath.write(html.encode('utf-8'))
    print(html)
