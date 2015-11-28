class EXPORT(object):
    """what is configured here is eported as raw posts"""
    FORUM_IDS = [
        6,    # Hintergrundinformationen über Psychopharmaka
        19,   # Hilfen zum Absetzen von Psychopharmaka
        54,   # Webseite: Inhalt
    ]
    """export whole forums"""

    TOPIC_IDS = []
    """export single topics"""


class METADATA(object):
    OVERRIDABLES = [
        'author',
        'title',
        'slug',
        'linktext',
    ]
    """those can be overridden by metadata in post content"""
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
    ]
    """All allowed attributes in use, prevents shooting self in foot"""

DATE_FORMAT = '%d.%m.%Y'
