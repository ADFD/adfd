# coding=utf-8
import logging
import subprocess

from adfd import cst
from adfd import conf
from adfd.db.phpbb_classes import Forum, TopicDoesNotExist, Topic

log = logging.getLogger(__name__)


def export():
    allTopics = []
    for kwargs in conf.EXPORT.TOPIC_KWARGS:
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
        self._write(self.SUMMARY_PATH, "\n".join(out))

    def _export_topic(self, topic):
        out = ["%s: %s" % (topic.id, topic.subject)]
        topicPath = self.TOPICS_PATH / ("%05d" % (topic.id)) / cst.DIR.RAW
        log.info('%s -> %s', topic.id, topicPath)
        metadataPath = topicPath / cst.FILENAME.META
        self._write(metadataPath, topic.md.asFileContents)
        self.allPaths.append(metadataPath)
        for post in topic.posts:
            current = "%s" % (post.subject)
            log.debug("export: %s", current)
            out.append("    " + current)
            contentPath = topicPath / (post.filename + cst.EXT.BBCODE)
            self._write(contentPath, post.content)
            self.allPaths.append(contentPath)
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

    def _write(self, path, content):
        log.debug('%s', path)
        path.dirname.mkdir()
        path.write(content.encode('utf8'))
