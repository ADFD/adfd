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
    * relative path the article should be placed on the site
    * ordering comes from place in the list.
    * metadata from accompanying file (e.g. tags, slug, ...)
"""
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


STRUCTURE = [
    ([10694]),
    ([9913, 9910, 853], 'Absetzen'),
    ([940, 9420], 'Hintergründe'),
    ([689, 893], 'Info'),
    ([10068], 'BBcode'),
]
