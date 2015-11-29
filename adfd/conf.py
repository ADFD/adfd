import plumbum

from adfd.cst import CONTENT_ROOT, DIR


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
    ([10694], '.'),
    ([9913, 9910, 853], 'Absetzen'),
    ([9241], 'Hintergründe/'),
    ([10046, 933], 'Hintergründe/System'),
    ([940, 9420], 'Hintergründe/Geschichte'),
    ([689, 893], 'Info'),
    ([10068], 'BBcode'),
]
"""structure of the site from a list of topicIds mapped to a relPath

The topic ids used here must have been exported to RAW
"""


class PATH(object):
    PROJECT = plumbum.LocalPath(__file__).up().up(2) / 'adfd'
    TEST_DATA = PROJECT / 'adfd' / 'tests' / 'data'
    CONTENT = CONTENT_ROOT
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


class METADATA(object):
    """settings for the accompanying meta data used by the web generator"""
    OVERRIDABLES = [
        'author',
        'title',
        'slug',
        'linktext',
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


class BBCODE(object):
    TITLE_PATTERN = '[h2]%s[/h2]\n'
