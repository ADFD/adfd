# coding=utf-8
import logging

from adfd.conf import PATH
from adfd.cst import EXT
from adfd.db.phpbb_classes import Forum, TopicDoesNotExist, Topic
from adfd.utils import dump_contents, id2name


log = logging.getLogger(__name__)


class ExportManager(object):
    def __init__(self, topicIds=None, forumIds=None, siteDescription=None):
        self.allTopicIds = set(topicIds or [])
        if forumIds:
            for forumId in forumIds:
                self.allTopicIds | set(Forum(forumId).topicIds)
        if siteDescription:
            self.harvest_topics_from_site_description(siteDescription)

    def harvest_topics_from_site_description(self, siteDescription):
        """export topics from a site description"""
        self.allTopicIds.add(siteDescription.mainTopicId)
        for content in siteDescription.contents:
            if isinstance(content, int):
                self.allTopicIds.add(content)
            else:
                self.harvest_topics_from_site_description(content)

    def export(self):
        TopicsExporter(self.allTopicIds).export_all()


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
