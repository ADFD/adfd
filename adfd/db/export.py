import logging

from adfd.cst import PATH, EXT
from adfd.db.phpbb_classes import Topic
from adfd.exc import TopicDoesNotExist
from adfd.utils import id2name, dump_contents

log = logging.getLogger(__name__)


def harvest_topic_ids(siteDescription):
    allTopicIds = set()

    def _harvest_topics_recursive(content):
        allTopicIds.add(content.mainTopicId)
        for content in content.contents:
            if isinstance(content, int):
                allTopicIds.add(content)
            else:
                _harvest_topics_recursive(content)

    _harvest_topics_recursive(siteDescription)
    return allTopicIds


def export_topics(topicIds):
    topics = []
    for topicId in topicIds:
        try:
            topics.append(Topic(topicId))
        except TopicDoesNotExist:
            log.warning('topic %s is broken', topicId)

    for topic in topics:
        export_topic(topic)


def export_topic(topic):
    topicPath = PATH.CNT_RAW / id2name(topic.id)
    log.info('%s -> %s', topic.id, topicPath)
    for post in topic.posts:
        current = "%s" % (post.subject)
        log.debug("export: %s", current)
        contentPath = topicPath / (post.filename + EXT.IN)
        dump_contents(contentPath, post.content)
        metadataPath = topicPath / (post.filename + EXT.META)
        dump_contents(metadataPath, post.md.asFileContents)
