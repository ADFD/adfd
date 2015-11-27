# coding=utf-8
import logging
import subprocess

from adfd import cst
from adfd import conf
from adfd.db.phpbb_classes import Forum, TopicDoesNotExist, Topic
from adfd.utils import dump_contents


log = logging.getLogger(__name__)


def export():
    allTopics = []
    for kwargs in conf.EXPORT.TOPIC_IDS:
        try:
            allTopics.append(Topic(**kwargs))
        except TopicDoesNotExist:
            log.warning('kwargs %s are broken', str(kwargs))
    for forumId in conf.EXPORT.FORUM_IDS:
        allTopics.extend(Forum(forumId).topics)
    TopicsExporter(allTopics).process()


class TopicsExporter(object):
    TOPICS_PATH = cst.PATH.TOPICS
    """root of all content for the website"""

    SUMMARY_PATH = TOPICS_PATH / 'summary.txt'
    """keep a list of topics and their imported posts as text"""

    def __init__(self, topics, useGit=False):
        self.topics = topics
        """:type: list of Topic"""
        self.allPaths = [self.SUMMARY_PATH]
        """contains a list of all imperted paths at end of import

        used to keep track of what whould be removed between imports
        """
        self.useGit = useGit

    def process(self):
        self._export_topics()
        if self.useGit:
            self._git_prune_orphans()
            self._git_add_files()

    def _export_topics(self):
        out = []
        for topic in self.topics:
            out.extend(self._export_topic(topic))
        log.info('%s files, %s topics', len(self.allPaths), len(self.topics))
        dump_contents(self.SUMMARY_PATH, "\n".join(out))

    def _export_topic(self, topic):
        out = ["%s: %s" % (topic.id, topic.subject)]
        topicPath = self.TOPICS_PATH / ("%05d" % (topic.id)) / cst.DIR.RAW
        log.info('%s -> %s', topic.id, topicPath)
        for post in topic.posts:
            current = "%s" % (post.subject)
            log.debug("export: %s", current)
            out.append("    " + current)
            contentPath = topicPath / (post.filename + cst.EXT.BBCODE)
            dump_contents(contentPath, post.content)
            metadataPath = topicPath / (post.filename + cst.EXT.META)
            dump_contents(metadataPath, post.md.asFileContents)
            self.allPaths.extend([contentPath, metadataPath])
        return out

    def _git_add_files(self):
        cmd = ['git', 'add', '--all', '.']
        try:
            subprocess.check_output(cmd, cwd=str(self.TOPICS_PATH))
        except subprocess.CalledProcessError:
            pass

    def _git_prune_orphans(self):
        for p in self.TOPICS_PATH.walk():
            if not p.isdir() and not any(ap == p for ap in self.allPaths):
                log.warning("removing %s", p)
                cmd = ['git', 'rm', '-f', str(p)]
                try:
                    subprocess.check_output(cmd, cwd=str(self.TOPICS_PATH))
                except subprocess.CalledProcessError:
                    p.delete()
