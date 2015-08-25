import logging
from adfd.article import Article

logging.basicConfig(level=logging.INFO)

DEMO = 'Demo'
INFO = 'Info'

# For regular links: ('https://getnikola.com/', 'Nikola Homepage')
# submenus: ((('http://a.com/', 'A'), ('http://b.com/', 'O')), 'Fruits')
# Make sure to end all urls with /
NAVIGATION_LINKS = {
    'de': (
        (
            (
                Article('kitchen-sink', DEMO).structuralRepresentation,
                Article(966, DEMO).structuralRepresentation,
            ),
            DEMO
        ),
        (
            (
                Article(689, INFO).structuralRepresentation,
                Article(893, INFO).structuralRepresentation,
            ),
            INFO
        ),
        Article(940).structuralRepresentation,
    ),
}

# todo instead of changing metadata in place:
# copy the articles to the right structure inside a folder 'information'
# so that
PAGES = [
    # BAD # ("content/static/*.bb", "", "story.tmpl"),
    # BAD # ("content/imported/*.bb", "", "story.tmpl"),
    # GOOD # ("information/*.bb", "", "story.tmpl"),
]
# also finds the articles in the right places

if __name__ == '__main__':
    print NAVIGATION_LINKS
