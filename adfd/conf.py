class RAW(object):
    """what is configured here is eported as raw posts"""
    FORUM_IDS = [
        6,    # Hintergrundinformationen über Psychopharmaka
        19,   # Hilfen zum Absetzen von Psychopharmaka
        51,   # Erfahrungsberichte
        53,   # Webseite: Planung und Dokumentation
        54,   # Webseite: Inhalt
    ]

    TOPIC_KWARGS = [
        dict(topicId=10068),
        dict(topicId=9481),  # not there but passed back by topic?
        dict(postIds=[109252]),
        dict(topicId=9345, excludedPostIds=[94933, 95114, 95786]),
    ]
