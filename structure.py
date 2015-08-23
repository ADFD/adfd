import collections
import yaml

from plumbum.path.local import LocalPath
from adfd.article import Article


class Navigator(object):
    def __init__(self, structurePath):
        self.structurePath = structurePath
        self.map = yaml.safe_load(self.structurePath.read())

    def replace_topic_ids(self):
        for key, value in self.map.items():
            if isinstance(value, list):
                self.map[key] = [Article(item) for item in value]

                not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el


def generate_navigation_links():
    path = LocalPath(__file__).up() / 'content' / 'structure.yml'
    navi = Navigator(path)
    navi.replace_topic_ids()


# For regular links: ('https://getnikola.com/', 'Nikola Homepage')
# submenus: ((('http://a.com/', 'A'), ('http://b.com/', 'O')), 'Fruits')
# Make sure to end all urls with /
NAVIGATION_LINKS = {
    'de': generate_navigation_links(),
    # 'de': (
    #     ('/archive.html', 'Archiv'),
    #     ('/categories/', 'Tags'),
    #     ('/rss.xml', 'RSS-Feed'),
    # )
}

if __name__ == '__main__':
    generate_navigation_links()
