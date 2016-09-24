import html
import logging
import re

from adfd.cst import PARSE
from adfd.db.lib import DbWrapper
from adfd.db.metadata import PageMetadata
from adfd.exc import *
from adfd.parse import AdfdParser
from adfd.utils import slugify, date_from_timestamp
from cached_property import cached_property

log = logging.getLogger(__name__)


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
        self.id = topicId
        self.postIds = self._get_post_ids()
        self.isActive = False

    def __repr__(self):
        return "<Topic(%s (%s))>" % (self.subject, self.id)

    @cached_property
    def slug(self):
        return self.posts[0].slug

    @cached_property
    def subject(self):
        return self.posts[0].subject

    @cached_property
    def html(self):
        return AdfdParser().to_html(self.content)

    @cached_property
    def content(self):
        """merge contents from topic files into one file"""
        contents = []
        for post in self.posts:
            if post.isExcluded:
                continue

            content = ''
            if self.md.useTitles:
                content += PARSE.TITLE_PATTERN % self.md.title
            contents.append(post.content)
        return "\n\n".join(contents)

    @cached_property
    def lastUpdate(self):
        newestDate = sorted([p.postTime for p in self.posts], reverse=True)[0]
        return date_from_timestamp(newestDate)

    @cached_property
    def md(self):
        return self.posts[0].md

    @cached_property
    def posts(self):
        """:rtype: list of Post"""
        posts = []
        for postId in self.postIds:
            post = Post(postId)
            if not post.isExcluded:
                posts.append(post)
        return posts

    def _get_post_ids(self):
        ids = DbWrapper().fetch_post_ids_from_topic(self.id)
        if not ids:
            raise TopicDoesNotExist(str(self.id))

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
        md = PageMetadata(kwargs=dict(
            title=self.subject,
            author=self.username,
            authorId=self.dbp.poster_id,
            lastUpdate=self.lastUpdate,
            postDate=date_from_timestamp(self.dbp.post_time),
            topicId=self.topicId,
            postId=self.id))
        md.populate_from_text(self.content)
        return md

    @cached_property
    def filename(self):
        filename = '%06d' % self.id
        if self.slug:
            filename += '-%s' % self.slug
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

    @cached_property
    def isExcluded(self):
        return self.md.isExcluded

    @staticmethod
    def _preprocess(text, bbcodeUid=None):
        if bbcodeUid:
            text = text.replace(':%s' % bbcodeUid, '')
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