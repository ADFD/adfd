# coding=utf-8
from datetime import datetime
import html
import logging
import os
import re
import subprocess

import sqlsoup

# noinspection PyUnresolvedReferences
import translitcodec  # This registers new codecs for slugification

from adfd.db import cst
from adfd.db.schema import PhpbbPost, PhpbbForum, PhpbbTopic
from adfd.db.utils import get_session


log = logging.getLogger(__name__)


class Forum(object):
    def __init__(self, forumId):
        self.forumId = forumId
        self._topicIds = SoupKitchen.fetch_topic_ids_from_forum(forumId)

    @property
    def topics(self):
        # return [Topic(topicId) for topicId in self._topicIds]
        for topicId in self._topicIds:
            try:
                yield Topic(topicId)

            except EmptyTopicException:
                log.warning("topic %s is corrupt", topicId)
                continue


class Topic(object):
    def __init__(self, topicId=None, postIds=None, excludedPostIds=None):
        assert topicId or postIds, 'need either topic or post id'
        assert not (topicId and postIds), 'need only one'
        if topicId:
            ids = SoupKitchen.fetch_post_ids_from_topic(topicId)
            self.postIds = [i for i in ids if i not in (excludedPostIds or [])]
        else:
            if not isinstance(postIds, list):
                assert isinstance(postIds, int), (postIds, type(postIds))
                postIds = [postIds]
            self.postIds = postIds
        if not self.postIds:
            raise EmptyTopicException("Topic %s has no posts" % (topicId))
        firstPostId = self.postIds[0]
        firstPost = DbPost(firstPostId)
        self.topicId = firstPost.topicId
        self.subject = firstPost.subject
        self.fileName = "%s.bb" % (firstPost.slug)
        if topicId:  # little sanity check ...
            assert topicId == self.topicId, (topicId, self.topicId)

    @property
    def posts(self):
        """:rtype: list of DbPost"""
        return [DbPost(postId) for postId in self.postIds]


class EmptyTopicException(Exception):
    pass


class DbPost(object):
    def __init__(self, postId):
        self.postId = postId
        self.p = SoupKitchen.fetch_post(postId)
        self.topicId = self.p.topic_id

    @property
    def metadata(self):
        return "%s\n\n" % '\n'.join([
            u'.. author: %s' % (self.username),
            u'.. lastUpdate: %s' % (self.lastUpdate),
            u'.. postDate: %s' % (self.format_date(int(self.p.post_time))),
            u'.. postId: %s' % (self.postId),
            u'.. slug: %s' % (self.uniqueSlug),
            u'.. title: %s' % (self.subject),
            u'.. topicId: %s' % (self.topicId),
            u'.. authorId: %s' % (self.p.poster_id)])

    @property
    def content(self):
        """This should be exactly the editable source of the post"""
        return self.sanitize(self.preprocessedText)

    @property
    def uniqueSlug(self):
        if not self.slug:
            return "re-%s" % (self.postId)

        if self.slug.startswith('re-'):
            return "%s-%s" % (self.postId, self.slug)

        return self.slug

    @property
    def slug(self):
        result = []
        for word in cst.SLUG.PUNCT.split(self.subject.lower()):
            word = word.encode('translit/long')
            if word and word.strip() != 'None':
                result.append(word)
        return u'-'.join(result)

    @property
    def subject(self):
        return self.preprocess(self.p.post_subject.decode(cst.ENC.IN))

    @property
    def username(self):
        username = (self.p.post_username or
                    SoupKitchen.get_username(self.p.poster_id))
        username = username.decode(cst.ENC.IN)
        return self.preprocess(username)

    @property
    def lastUpdate(self):
        lastUpdate = (self.p.post_edit_time or self.p.post_time)
        return self.format_date(lastUpdate)

    @property
    def preprocessedText(self):
        return self.preprocess(self.rawText, self.p.bbcode_uid)

    @property
    def rawText(self):
        return self.p.post_text.decode(cst.ENC.IN)

    @staticmethod
    def preprocess(text, bbcodeUid=None):
        if bbcodeUid:
            text = text.replace(':%s' % (bbcodeUid), '')
        text = html.unescape(text)
        return text

    @staticmethod
    def format_date(timestamp):
        return datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y')

    @classmethod
    def sanitize(cls, text):
        text = cls.fix_db_storage_patterns(text)
        return cls.fix_whitespace(text)

    @classmethod
    def fix_db_storage_patterns(cls, text):
        """restore original bbcode from phpBB db storage scheme"""
        pairs = [
            ("<!-- s(\S+) -->(?:.*?)<!-- s(?:\S+) -->", '\g<1>'),
            ('<!-- m -->.*?href="(.*?)".*?<!-- m -->', '[url]\g<1>[/url]'),
            ('<!-- l -->.*?href="(.*?)".*?<!-- l -->', '[url]\g<1>[/url]'),
            ("\[list\](.*?)\[\/list:u\]", '[list]\g<1>[/list]'),
            ("\[list=1\](.*?)\[\/list:o\]", '[list=1]\g<1>[/list]'),
            ("\[\*\](.*?)\[\/\*:m\]", '[*] \g<1>')]
        for pattern, replacement in pairs:
            log.debug("'%s' -> '%s'\n%s", pattern, replacement, text)
            text = re.compile(pattern, flags=re.DOTALL).sub(replacement, text)
            log.debug("applied\n%s\n%s", text, '#' * 120)
        return text

    @classmethod
    def fix_whitespace(cls, text):
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        lines = []
        for line in text.split('\n'):
            lines.append('' if not line.strip() else line)
        text = "\n".join(lines)
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        return text


# fixme this is an awful mix between soup and schema access *juck*
class SoupKitchen(object):
    db = sqlsoup.SQLSoup(cst.DB_URL)

    @classmethod
    def fetch_topic_ids_from_forum(cls, forumId):
        session = get_session()
        query = session.query(PhpbbTopic).join(
            PhpbbForum, PhpbbTopic.forum_id == PhpbbTopic.forum_id).\
            filter(PhpbbTopic.forum_id == forumId)
        return [row.topic_id for row in query.all()]

    @classmethod
    def fetch_post_ids_from_topic(cls, topicId):
        where = cls.db.phpbb_posts.topic_id == str(topicId)
        posts = cls.db.phpbb_posts.filter(where).\
            order_by(PhpbbPost.post_time).all()
        return [p.post_id for p in posts]

    @classmethod
    def fetch_post(cls, postId):
        where = cls.db.phpbb_posts.post_id == str(postId)
        return cls.db.phpbb_posts.filter(where).first()

    @classmethod
    def get_username(cls, userId):
        where = cls.db.phpbb_users.user_id == str(userId)
        try:
            return cls.db.phpbb_users.filter(where).first().username

        except AttributeError:
            log.warning("no username for %s found", userId)
            return "Anonymous"


class TopicsExporter(object):
    SUMMARY_PATH = cst.SITE.EXPORT_PATH / 'summary.txt'
    """keep a list of topics and their imported posts as text"""

    def __init__(self, topics):
        self.topics = topics
        """:type: list of Topic"""
        self.allPaths = [self.SUMMARY_PATH]
        """contains a list of all imperted paths at end of import

        used to keep track of what whould be removed between imports
        """

    def export_topics(self):
        self.update_directory()
        self.prune_orphans()
        self.add_files()

    def update_directory(self):
        out = []
        for topic in self.topics:
            out.append("%s: %s" % (topic.topicId, topic.subject))
            topicPath = cst.SITE.EXPORT_PATH / ("%05d" % (topic.topicId))
            for post in topic.posts:
                current = "%s: %s" % (post.postId, post.slug)
                log.info("export: %s", current)
                out.append("    " + current)
                patt = "%s-%s.%%s" % (post.postId, post.slug)
                postMetadataPath = topicPath / (patt % ('meta'))
                postContentPath = topicPath / (patt % ('bb'))
                self.allPaths.extend([postMetadataPath, postContentPath])
                self.write(postMetadataPath, post.metadata)
                self.write(postContentPath, post.content)
        self.write(self.SUMMARY_PATH, "\n".join(out))

    def add_files(self):
        cmd = ['git', 'add', '--all', '.']
        try:
            subprocess.check_output(cmd, cwd=str(cst.SITE.EXPORT_PATH))
        except subprocess.CalledProcessError:
            pass

    def prune_orphans(self):
        for p in cst.SITE.EXPORT_PATH.walk():
            if not p.isdir() and not any(ap == p for ap in self.allPaths):
                log.warning("removing %s", p)
                cmd = ['git', 'rm', '-f', str(p)]
                try:
                    subprocess.check_output(cmd, cwd=str(cst.SITE.EXPORT_PATH))
                except subprocess.CalledProcessError:
                    p.delete()

    def write(self, path, content):
        try:
            os.makedirs(str(path.dirname))
        except OSError as e:
            log.debug(e)
        # log.info('write %s', path)
        path.write(content.encode(cst.ENC.OUT))
