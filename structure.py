from plumbum.path.local import LocalPath
from adfd.article import Article

structure = [
    [
        [Article('kitchen-sink', 'slug/prefix')],
        'NaviOrdnerName'
    ],
    [
        [Article(68, 'bla'), Article(71, 'blubb')],
        'AndererNaviOrdnerName'
    ],
    [Article(8829), 'blarrr'],
    [Article(8997), 'absetzhilfen'],
]


class Navigator(object):
    def __init__(self, structure):
        self.structure = structure

    def change(self, lol):
        for idx, item in enumerate(lol):
            if isinstance(item, list):
                self.change(item)
            elif item.startswith('-'):
                lol[idx] = ['not', item.split('-')[1]]


def generate_navigation_links():
    navi = Navigator(structure)


# todo think about if we want to use markup in links and if yes: how.

# For regular links: ('https://getnikola.com/', 'Nikola Homepage')
# submenus: ((('http://a.com/', 'A'), ('http://b.com/', 'O')), 'Fruits')
# Make sure to end all urls with /
NAVIGATION_LINKS = {
    'de': generate_navigation_links(),
    'en': (
        (
            (
                ('/documentation.html', '<strong>Documentation</strong>'),
            ),
            'Documentation'
        ),
        ('/blog/index.html', 'Blog'),
    ),
}

if __name__ == '__main__':
    generate_navigation_links()
