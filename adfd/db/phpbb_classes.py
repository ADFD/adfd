import html
import logging
import re

from cached_property import cached_property

from adfd.content import Metadata
from adfd.db.utils import DbWrapper
from adfd.utils import slugify, format_date

log = logging.getLogger(__name__)


__all__ = [
    'Forum',
    'ForumDoesNotExist',
    'ForumIsEmpty',
    'Topic',
    'TopicDoesNotExist',
    'Post',
    'PostDoesNotExist',
]


class Forum(object):
    def __init__(self, forumId):
        self.id = forumId
        self.db = DbWrapper()
        self.dbObject = self.db.fetch_forum(self.id)
        if not self.dbObject:
            raise ForumDoesNotExist(str(self.id))

        self.topicIds = self.db.fetch_topic_ids_from_forum(self.id)
        if not self.topicIds:
            raise ForumIsEmpty(str(self.id))

        self.name = self.dbObject.forum_name

    @property
    def topics(self):
        for topicId in self.topicIds:
            try:
                yield Topic(topicId)

            except TopicDoesNotExist:
                log.warning("topic %s is broken", topicId)
                continue


class ForumDoesNotExist(Exception):
    """raised if the forum contains no topics"""


class ForumIsEmpty(Exception):
    """raised if the forum contains no topics"""


class Topic(object):
    """This has a bit of flexibility to make it possible to filter posts."""

    def __init__(self, topicId):
        self.postIds = self.fetch_post_ids(topicId)
        self.firstPost = self.posts[0]
        self.id = self.firstPost.topicId
        self.subject = self.firstPost.subject
        self.lastUpdate = self._get_latest_update(self.posts),

    @cached_property
    def posts(self):
        """:rtype: list of Post"""
        return [Post(postId) for postId in self.postIds]

    @classmethod
    def _get_latest_update(cls, posts):
        # fixme still broken?
        newestDate = sorted([p.lastUpdate for p in posts], reverse=True)[0]
        return format_date(newestDate)

    def fetch_post_ids(self, topicId):
        ids = DbWrapper().fetch_post_ids_from_topic(topicId)
        if not ids:
            raise TopicDoesNotExist(str(topicId))

        return ids


class TopicDoesNotExist(Exception):
    """raised if the topic contains no posts"""


class Post(object):
    def __init__(self, postId):
        self.id = postId
        self.db = DbWrapper()
        self.dbp = self.db.fetch_post(self.id)
        if not self.dbp:
            raise PostDoesNotExist(str(self.id))

        self.topicId = self.dbp.topic_id
        self.rawText = self.dbp.post_text
        self.md = Metadata(kwargs=dict(
            slug=self.slug,
            title=self.subject,
            author=self.username,
            authorId=str(self.dbp.poster_id),
            lastUpdate=str(self.lastUpdate),
            postDate=str(format_date(self.dbp.post_time)),
            topicId=str(self.topicId),
            postId=str(self.id)))

    def __repr__(self):
        return ("<%s %s (%s)>" %
                (self.__class__.__name__, self.id, self.slug))

    @cached_property
    def content(self):
        content = self._preprocess(self.rawText, self.dbp.bbcode_uid)
        content = self._fix_db_storage_patterns(content)
        return self._fix_whitespace(content)

    @cached_property
    def slug(self):
        return slugify(self.subject)

    @cached_property
    def subject(self):
        return self._preprocess(self.dbp.post_subject)

    @cached_property
    def username(self):
        username = (self.dbp.post_username or
                    self.db.get_username(self.dbp.poster_id))
        return self._preprocess(username)

    @cached_property
    def lastUpdate(self):
        return self.dbp.post_edit_time or self.dbp.post_time

    @cached_property
    def filename(self):
        filename = '%06d' % (self.id)
        if self.slug:
            filename += '-%s' % (self.slug)
        return filename

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


class PostDoesNotExist(Exception):
    """raised if a post with the given ID does not exist"""
