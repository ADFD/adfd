# -*- coding: utf-8 -*-
import logging
import pprint

from adfd.article import Article

logging.basicConfig(level=logging.INFO)


def get_prepared_article_representations(identifiers, path):
    representations = []
    for identifier in identifiers:
        article = Article(identifier, path)
        article.process()
        representation = article.structuralRepresentation
        representations.append(representation)
    return tuple(representations), path

# For regular links: ('https://getnikola.com/', 'Nikola Homepage')
# submenus: ((('http://a.com/', 'A'), ('http://b.com/', 'O')), 'Fruits')
# TODO Make sure to end all urls with /

NAVIGATION_LINKS = {
    'de': (
        get_prepared_article_representations([9913, 9910, 853], u'Absetzen'),
        get_prepared_article_representations([940, 9420], u'Hintergründe'),
        get_prepared_article_representations([689, 893], u'Info'),
        get_prepared_article_representations(['kitchen-sink', 9730], u'Demo'),
    )
}


if __name__ == '__main__':
    pprint.pprint(NAVIGATION_LINKS)
