import logging

from adfd.conf import PATH
from adfd.cst import EXT
from adfd.db.phpbb_classes import TopicDoesNotExist, Topic
from adfd.utils import dump_contents, id2name


log = logging.getLogger(__name__)


class RawTopicsExporter:
    """Read all given topics from DB into raw file"""

    def __init__(self, topicIds=None, siteDescription=None):
        self.allTopicIds = set(topicIds or [])
        if siteDescription:
            self._harvest_topics_recursive(siteDescription)

        self.topics = []
        """:type: list of Topic"""
        for topicId in self.allTopicIds:
            try:
                self.topics.append(Topic(topicId))
            except TopicDoesNotExist:
                log.warning('topic %s is broken', topicId)

    def export(self):
        for topic in self.topics:
            self._export_topic(topic)

    def _harvest_topics_recursive(self, content):
        self.allTopicIds.add(content.mainTopicId)
        for content in content.contents:
            if isinstance(content, int):
                self.allTopicIds.add(content)
            else:
                self._harvest_topics_recursive(content)

    def _export_topic(self, topic):
        topicPath = PATH.CNT_RAW / id2name(topic.id)
        log.info('%s -> %s', topic.id, topicPath)
        for post in topic.posts:
            current = "%s" % (post.subject)
            log.debug("export: %s", current)
            contentPath = topicPath / (post.filename + EXT.IN)
            dump_contents(contentPath, post.content)
            metadataPath = topicPath / (post.filename + EXT.META)
            dump_contents(metadataPath, post.md.asFileContents)
