# -*- coding: utf-8 -*-
import logging

from adfd.db import export

FORUM_IDS = [
    6,    # Hintergrundinformationen über Psychopharmaka
    19,   # Hilfen zum Absetzen von Psychopharmaka
    51,   # Erfahrungsberichte
    54,   # Webseite/Inhalt
]

TOPICS = [
    export.Topic(10068),
    # export.Topic(9481), not there but passed back by topic
    # export.Topic(postIds=[109252]),
    # export.Topic(9345, excludedPostIds=[94933, 95114, 95786]),
]


def export_all(topics, forumIds):
    allTopics = topics
    for forumId in forumIds:
        allTopics.extend(export.Forum(forumId).topics)
    export.TopicsExporter(allTopics).export_topics()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    export_all(TOPICS, FORUM_IDS)
