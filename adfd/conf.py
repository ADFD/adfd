import plumbum

from adfd.bbcode import AdfdParser
from adfd.cst import _CONTENT_ROOT, DIR


class PATH:
    PROJECT = plumbum.LocalPath(__file__).dirname.up()
    TEST_DATA = PROJECT / 'adfd' / 'tests' / 'data'
    CONTENT = _CONTENT_ROOT
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
            'author',
            'title',
            'slug',
            'linktext',
            'relPath',
            'relFilePath',
            'weight',
        ]
        """can be overridden by metadata in post content"""
        ATTRIBUTES = OVERRIDABLES + [
            'authorId',
            'lastUpdate',
            'postDate',
            'topicId',
            'postId',

            'allAuthors',
            'useTitles',
            'excludePosts',
            'includePosts',

            'relPath',
        ]
        """all allowed attributes in use, prevents shooting self in foot"""

    DATE_FORMAT = '%d.%m.%Y'
    """this format will be used for human readable dates in meta data"""


class PARSE:
    FUNC = AdfdParser().to_html
    PYPHEN_LANG = 'de_de'
    TITLE_PATTERN = '[h2]%s[/h2]\n'
