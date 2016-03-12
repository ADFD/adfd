import logging

from adfd.conf import PATH
from adfd.cst import EXT
from adfd.db.phpbb_classes import TopicDoesNotExist, Topic
from adfd.utils import dump_contents, id2name


log = logging.getLogger(__name__)


class TopicsExporter:
    """root of all content for the website"""

    def __init__(self, topicIds=None, siteDescription=None):
        self.allTopicIds = set(topicIds or [])
        if siteDescription:
            self.harvest_topics_recursive(siteDescription)

        self.topics = []
        """:type: list of Topic"""
        for topicId in self.allTopicIds:
            try:
                self.topics.append(Topic(topicId))
            except TopicDoesNotExist:
                log.warning('topic %s is broken', topicId)

    def harvest_topics_recursive(self, content):
        self.allTopicIds.add(content.mainTopicId)
        for content in content.contents:
            if isinstance(content, int):
                self.allTopicIds.add(content)
            else:
                self.harvest_topics_recursive(content)

    def export_all(self):
        for topic in self.topics:
            self._export_topic(topic)

    def _export_topic(self, topic):
        out = ["%s: %s" % (topic.id, topic.subject)]
        topicPath = PATH.CNT_RAW / id2name(topic.id)
        log.info('%s -> %s', topic.id, topicPath)
        for post in topic.posts:
            current = "%s" % (post.subject)
            log.debug("export: %s", current)
            out.append("    " + current)
            contentPath = topicPath / (post.filename + EXT.IN)
            dump_contents(contentPath, post.content)
            metadataPath = topicPath / (post.filename + EXT.META)
            dump_contents(metadataPath, post.md.asFileContents)
        return out
