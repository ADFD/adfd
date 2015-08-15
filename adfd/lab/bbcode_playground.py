from __future__ import print_function
from __future__ import print_function
import bbcode
from plumbum import LocalPath


def custom_render():
    parser = bbcode.Parser()

    # A custom render function.
    def render_color(tag_name, value, options, parent, context):
        return '<span style="color:%s;">%s</span>' % (tag_name, value)

    # Installing advanced formatters.
    for color in ('red', 'blue', 'green', 'yellow', 'black', 'white'):
        parser.add_formatter(color, render_color)
    print(parser.format(text, somevar='somevalue'))


def simple_formatters():
    parser = bbcode.Parser()
    parser.add_simple_formatter('br', '<br>', standalone=True)
    # parser.add_simple_formatter('sup', '<sup>%(value)s</sup>')


def parsing():
    # Using the default parser.
    parser = bbcode.Parser()
    html = parser.format(text)
    outFilePath.write(html.encode('utf-8'))
    print(html)


if __name__ == '__main__':
    HERE = LocalPath(__file__).up()
    testFilePath = HERE / 'bbcode-playground.bb'
    outFilePath = HERE / 'bbcode-playground.html'

    text = testFilePath.read().decode('utf-8')
    custom_render()
