import plumbum

from adfd.bbcode import AdfdParser
from adfd.cst import _CONTENT_ROOT, DIR


class EXPORT(object):
    """what is configured here is eported as raw posts"""
    FORUM_IDS = [
        6,    # Hintergrundinformationen über Psychopharmaka
        19,   # Hilfen zum Absetzen von Psychopharmaka
        54,   # Webseite: Inhalt
    ]
    """export whole forums"""

    TOPIC_IDS = [
        10068,
    ]
    """export single topics"""


STRUCTURE = [
    (('', 10694), []),
    (('Absetzen', 10694), [9913, 9910, 853]),
    (('Hintergründe', 10694), (
        (('Geschichte', 10694), [9241, 10046, 933]),
        (('Steckbriefe', 10694), [9738, 9735, 9733, 9732, 9731])
    )),
    (('Info', 10694), [689, 893]),
    (('BBcode', 10694), [10068]),
]
"""structure of the site from a list of topicIds mapped to a relPath

The topic ids used here must have been exported to RAW
"""


class PATH(object):
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
    # FIXME obsolete
    STRUCTURE = CNT_FINAL / 'structure.json'
    """json containing the page structure for menu generation"""


class METADATA(object):
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
    class CATEGORY(object):
        ATTRIBUTES = [
            'name',
            'mainTopicId',
            'weight'
        ]

    class PAGE(object):
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


class PARSE(object):
    FUNC = AdfdParser().to_html
    TITLE_PATTERN = '[h2]%s[/h2]\n'
