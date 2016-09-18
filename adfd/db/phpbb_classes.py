import html
import logging
import re

from cached_property import cached_property

from adfd.cnt.metadata import PageMetadata
from adfd.db.lib import DbWrapper
from adfd.exc import *
from adfd.utils import slugify, date_from_timestamp

log = logging.getLogger(__name__)


__all__ = [
    'Forum',
    'Topic',
    'Post',
]


class Forum:
    def __init__(self, forumId):
        self.id = forumId

    @cached_property
    def topics(self):
        for topicId in self.topicIds:
            try:
                yield Topic(topicId)

            except TopicDoesNotExist:
                log.warning("topic %s is broken", topicId)
                continue

    @cached_property
    def name(self):
        return self.dbo.forum_name

    @cached_property
    def db(self):
        return DbWrapper()

    @cached_property
    def topicIds(self):
        ids = self.db.fetch_topic_ids_from_forum(self.id)
        if not ids:
            raise ForumIsEmpty(str(self.id))

        return ids

    @cached_property
    def dbo(self):
        dbo = self.db.fetch_forum(self.id)
        if not dbo:
            raise ForumDoesNotExist(str(self.id))

        return dbo


class Topic:
    def __init__(self, topicId):
        self._originalId = topicId

    @cached_property
    def subject(self):
        return self.firstPost.subject

    @cached_property
    def lastUpdate(self):
        return self._get_last_update(self.posts)

    @cached_property
    def posts(self):
        """:rtype: list of Post"""
        return [Post(postId) for postId in self.postIds]

    @cached_property
    def id(self):
        self.postIds = self.fetch_post_ids(self._originalId)
        self.firstPost = self.posts[0]
        return self.firstPost.topicId

    @classmethod
    def _get_last_update(cls, posts):
        newestDate = sorted([p.postTime for p in posts], reverse=True)[0]
        return date_from_timestamp(newestDate)

    def fetch_post_ids(self, topicId):
        ids = DbWrapper().fetch_post_ids_from_topic(topicId)
        if not ids:
            raise TopicDoesNotExist(str(topicId))

        return ids


class Post:
    def __init__(self, postId):
        self.id = postId

    def __repr__(self):
        return "<%s %s (%s)>" % (self.__class__.__name__, self.id, self.slug)

    @cached_property
    def topicId(self):
        return self.dbp.topic_id

    @cached_property
    def rawText(self):
        return self.dbp.post_text

    @cached_property
    def postTime(self):
        return self.dbp.post_edit_time or self.dbp.post_time

    @cached_property
    def md(self):
        return PageMetadata(kwargs=dict(
            title=self.subject,
            author=self.username,
            authorId=self.dbp.poster_id,
            lastUpdate=self.lastUpdate,
            postDate=date_from_timestamp(self.dbp.post_time),
            topicId=self.topicId,
            postId=self.id))

    @cached_property
    def filename(self):
        filename = '%06d' % (self.id)
        if self.slug:
            filename += '-%s' % (self.slug)
        return filename

    @cached_property
    def subject(self):
        return self._preprocess(self.dbp.post_subject)

    @cached_property
    def content(self):
        content = self._preprocess(self.rawText, self.dbp.bbcode_uid)
        content = self._fix_db_storage_patterns(content)
        content = self._fix_whitespace(content)
        return content

    @cached_property
    def slug(self):
        return slugify(self.subject)

    @cached_property
    def username(self):
        username = (self.dbp.post_username or
                    self.db.get_username(self.dbp.poster_id))
        return self._preprocess(username)

    @cached_property
    def lastUpdate(self):
        return date_from_timestamp(self.postTime)

    @staticmethod
    def _preprocess(text, bbcodeUid=None):
        if bbcodeUid:
            text = text.replace(':%s' % (bbcodeUid), '')
        text = html.unescape(text)
        return text

    @classmethod
    def _fix_db_storage_patterns(cls, text):
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
    def _fix_whitespace(cls, text):
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        lines = []
        for line in text.split('\n'):
            lines.append('' if not line.strip() else line)
        text = "\n".join(lines)
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        return text

    @cached_property
    def db(self):
        return DbWrapper()

    @cached_property
    def dbp(self):
        dbp = self.db.fetch_post(self.id)
        if not dbp:
            raise PostDoesNotExist(str(self.id))

        return dbp
