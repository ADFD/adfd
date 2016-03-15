import re

import plumbum

from adfd.cst import DIR


class PATH:
    PROJECT = plumbum.LocalPath(__file__).dirname.up()
    TEST_DATA = PROJECT / 'adfd' / 'tests' / 'data'
    CONTENT = PROJECT / 'content'
    CNT_RAW = CONTENT / DIR.RAW
    """exported bbcode like it looks when edited - each posts in a single file.

    It is not raw in the sense that it has the same format like stored in DB
    as this is quite different from what one sees in the editor, but from
    an editors perspective that does not matter, so this is considered raw
    """
    CNT_PREPARED = CONTENT / DIR.PREPARED
    """prepared in a file pair - contents as bbcode in one file + metadata"""
    CNT_FINAL = CONTENT / DIR.FINAL
    """the final structure that makes the website"""


class METADATA:
    """settings for the accompanying meta data used by the web generator

    For overriding this directly from post contents the bbcode tag
    ``meta`` has to be defined on the board.

    The following settings to be done in ``adm/index.php?i=acp_bbcodes``
    define the tag and make it invisible if the post is viewed directly.

    BBCODE use:

        [meta]{TEXT}[/meta]

    BBCODE replacement:

        <span style="display: none;">[meta]{TEXT}[/meta]</span>
    """
    class CATEGORY:
        ATTRIBUTES = [
            'name',
            'mainTopicId',
            'weight'
        ]

    class PAGE:
        OVERRIDABLES = [
            'allAuthors',
            'excludePosts',
            'includePosts',
            'linktext',
            'relFilePath',
            'relPath',
            'slug',
            'title',
            'weight',
        ]
        """can be overridden by metadata in post content"""
        ATTRIBUTES = OVERRIDABLES + [
            'author',
            'authorId',
            'lastUpdate',
            'postDate',
            'topicId',
            'postId',

            'useTitles',

            'relPath',
        ]
        """all allowed attributes in use, prevents shooting self in foot"""

    DATE_FORMAT = '%d.%m.%Y'
    """this format will be used for human readable dates in meta data"""


class PARSE:
    FUNC = None
    PYPHEN_LANG = 'de_de'
    TITLE_PATTERN = '[h2]%s[/h2]\n'


class RE:
    URL = re.compile(
        r'(?im)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)'
        r'(?:[^\s()<>]+|\([^\s()<>]+\))'
        r'+(?:\([^\s()<>]+\)|[^\s`!()\[\]{};:\'".,<>?]))')
    """
    from http://daringfireball.net/2010/07/improved_regex_for_matching_urls
    Only support one level of parentheses - was failing on some URLs.
    See http://www.regular-expressions.info/catastrophic.html
    """
    DOMAIN = re.compile(
        r'(?im)(?:www\d{0,3}[.]|[a-z0-9.\-]+[.]'
        r'(?:com|net|org|edu|biz|gov|mil|info|io|name|me|tv|us|uk|mobi))')
    """
    For the URL tag, try to be smart about when to append a missing http://.
    If the given link looks like a domain, add a http:// in front of it,
    otherwise leave it alone (be a relative path, a filename, etc.).
    """
