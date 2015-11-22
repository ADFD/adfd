# -*- coding: utf-8 -*-
"""
This is just a hunch, but atm I feel that I make my life easier if I create the
whole structure of the site from an input of categories and a set of Articles
programmatically and then create the navigation and whatever the website
generator needs here.

rough idea:

Website structure is represented by a hierarchical tree. Each tree node holds
a list of articles.

Each Article has
    * ID that is used to localize the file with the content
    * and the ordering comes from place in the list.
    * metadata from accompanying file (e.g. tags, slug, ...)

"""

import logging
import pprint

from adfd.content import Article


logging.basicConfig(level=logging.DEBUG)


def get_prepared_article_representations(identifiers, path=u''):
    representations = []
    for identifier in identifiers:
        article = Article(identifier, path)
        representation = article.structuralRepresentation
        representations.append(representation)
    return tuple(representations), path


# fixme this is still with nikola constraints
# todo create fitting stucture and inject it via GLOBAL_CONTEXT in own theme
# For regular links: ('https://getnikola.com/', 'Nikola Homepage')
# submenus: ((('http://a.com/', 'A'), ('http://b.com/', 'O')), 'Fruits')
# TODO Make sure to end all urls with /
NAVIGATION_LINKS = {
    'de': (
        get_prepared_article_representations(['tmp-index']),
        get_prepared_article_representations([9913, 9910, 853], 'Absetzen'),
        get_prepared_article_representations([940, 9420], 'Hintergründe'),
        get_prepared_article_representations([689, 893], 'Info'),
        get_prepared_article_representations(['kitchen-sink', 9730], 'Demo'),
        get_prepared_article_representations([10068], 'BBcode'),
    )
}


if __name__ == '__main__':
    pprint.pprint(NAVIGATION_LINKS)
