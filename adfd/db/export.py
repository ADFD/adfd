# coding=utf-8
import logging

from adfd.cst import EXT
from adfd.conf import PATH
from adfd.db.phpbb_classes import Forum, TopicDoesNotExist, Topic
from adfd.utils import dump_contents, id2name

log = logging.getLogger(__name__)


def export(forumIds=None, topicIds=None):
    allTopicIds = []
    for forumId in forumIds or []:
        forumTopicIds = Forum(forumId).topicIds
        allTopicIds.extend(forumTopicIds)
        log.info("export topics from forum %s: %s", forumId, forumTopicIds)
    if topicIds:
        allTopicIds.extend(topicIds)
    TopicsExporter(allTopicIds).export_all()


class TopicsExporter(object):
    """root of all content for the website"""

    SUMMARY_PATH = PATH.CNT_RAW / 'summary.txt'
    """keep a list of topics and their imported posts as text"""

    def __init__(self, topicIds):
        self.topics = []
        """:type: list of Topic"""
        for topicId in topicIds:
            try:
                self.topics.append(Topic(topicId))
            except TopicDoesNotExist:
                log.warning('topic %s is broken', topicId)
        self.allPaths = [self.SUMMARY_PATH]
        """list of all written paths at end of import (purely for logging)"""

    def export_all(self):
        out = []
        for topic in self.topics:
            out.extend(self._export_topic(topic))
        log.info('%s files, %s topics', len(self.allPaths), len(self.topics))
        dump_contents(self.SUMMARY_PATH, "\n".join(out))

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
            self.allPaths.extend([contentPath, metadataPath])
        return out
