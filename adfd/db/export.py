# coding=utf-8
import logging
import subprocess

from adfd import cst
from adfd import conf
from adfd.db import phpbb_classes


log = logging.getLogger(__name__)


def export():
    allTopics = []
    for kwargs in conf.RAW.TOPIC_KWARGS:
        try:
            allTopics.append(phpbb_classes.Topic(**kwargs))
        except phpbb_classes.TopicIsEmpty:
            log.warning('kwargs %s are broken', str(kwargs))
    for forumId in conf.RAW.FORUM_IDS:
        allTopics.extend(phpbb_classes.Forum(forumId).topics)
    TopicsExporter(allTopics).export_topics()


class TopicsExporter(object):
    CONTENT_PATH = cst.PATH.CONTENT
    """root of all content for the website"""
    RAW_EXPORT_PATH = CONTENT_PATH / cst.DIR.RAW
    """exported bbcode like it looks when edited

    It is not raw in the sense that it has the same format like stored in DB
    as this is quite different from what one sees in the editor, but from
    an editors perspective that does not matter, so this is considered raw
    """

    SUMMARY_PATH = CONTENT_PATH / 'summary.txt'
    """keep a list of topics and their imported posts as text"""

    def __init__(self, topics, useGit=False):
        self.topics = topics
        """:type: list of Topic"""
        self.allPaths = [self.SUMMARY_PATH]
        """contains a list of all imperted paths at end of import

        used to keep track of what whould be removed between imports
        """
        self.useGit = useGit

    def export_topics(self):
        self.update_directory()
        if self.useGit:
            self.prune_orphans()
            self.add_files()

    def update_directory(self):
        out = []
        for topic in self.topics:
            out.extend(self._export_topic(topic))
        log.info('%s files, %s topics', len(self.allPaths), len(self.topics))
        self.write(self.SUMMARY_PATH, "\n".join(out))

    def _export_topic(self, topic):
        out = ["%s: %s" % (topic.id, topic.subject)]
        topicPath = self.RAW_EXPORT_PATH / ("%05d" % (topic.id))
        log.info('%s -> %s', topic.id, topicPath)
        for post in topic.posts:
            current = "%s" % (post.uniqueSlug)
            log.debug("export: %s", current)
            out.append("    " + current)
            patt = "%s.%%s" % (post.filename)
            postMetadataPath = topicPath / (patt % ('meta'))
            postContentPath = topicPath / (patt % ('bb'))
            self.allPaths.extend([postMetadataPath, postContentPath])
            self.write(postMetadataPath, post.metadata)
            self.write(postContentPath, post.content)
        return out

    def add_files(self):
        cmd = ['git', 'add', '--all', '.']
        try:
            subprocess.check_output(cmd, cwd=str(self.RAW_EXPORT_PATH))
        except subprocess.CalledProcessError:
            pass

    def prune_orphans(self):
        for p in self.RAW_EXPORT_PATH.walk():
            if not p.isdir() and not any(ap == p for ap in self.allPaths):
                log.warning("removing %s", p)
                cmd = ['git', 'rm', '-f', str(p)]
                try:
                    subprocess.check_output(cmd, cwd=str(self.RAW_EXPORT_PATH))
                except subprocess.CalledProcessError:
                    p.delete()

    def write(self, path, content):
        log.debug('%s', path)
        path.dirname.mkdir()
        path.write(content.encode('utf8'))
