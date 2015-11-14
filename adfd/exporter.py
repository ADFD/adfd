# -*- coding: utf-8 -*-
import logging

from adfd.db.export import Topic, Forum, TopicsExporter

FORUM_IDS = [
    5,   # Erfahrungsberichte
    6,   # Hintergrundinformationen über Psychopharmaka
    19,  # Hilfen zum Absetzen von Psychopharmaka
]

TOPICS = [
    Topic(postIds=[109252]),
    # Topic(2207),
    # Topic(9345, excludedPostIds=[94933, 95114, 95786]),
]


def export_all(forumIds, topics):
    allTopics = []
    for forumId in forumIds:
        forum = Forum(forumId)
        allTopics.extend(forum.topics)
    allTopics.extend(topics)
    te = TopicsExporter(allTopics)
    te.export_topics()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    export_all(FORUM_IDS, TOPICS)
