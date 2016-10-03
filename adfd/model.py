import html
import logging
import os
import re

from cached_property import cached_property

from adfd.cnf import SITE, PATH, APP
from adfd.db.lib import DbWrapper
from adfd.exc import *
from adfd.metadata import PageMetadata
from adfd.parse import AdfdParser
from adfd.utils import slugify, ContentGrabber, date_from_timestamp

log = logging.getLogger(__name__)


class Node:
    SPEC = "N"

    def __init__(self, identifier, title=None):
        self.identifier = identifier
        self._title = title
        self.parents = []
        """:type: list of Node"""
        self.children = []
        """:type: list of Node"""
        self.isActive = False

    def __repr__(self):
        return "<%s(%s: %s)>" % (self.SPEC, self.identifier, self.title[:6])

    def __html__(self):
        """In a template: ``{{ page }}`` == ``{{ page.html|safe }}``."""
        return self.html

    @cached_property
    def title(self):
        return self._title or self.topic.title

    @cached_property
    def html(self):
        return self.topic.html

    @cached_property
    def bbcode(self):
        return self.topic.bbcode

    @cached_property
    def relPath(self):
        return "/".join([c.slug for c in self.parents + [self]]) or "/"

    # Todo return file path if it is a static page
    @cached_property
    def link(self):
        return "http://adfd.org/austausch/viewtopic.php?t=%s" % self.topic.id

    @cached_property
    def slug(self):
        """:rtype: str"""
        isRoot = isinstance(self, CategoryNode) and self._title == ''
        return '' if isRoot else slugify(self.title)

    @cached_property
    def hasContent(self):
        return self.identifier is not None

    @cached_property
    def topic(self):
        # FIXME seems to be never called -> remove
        if not self.identifier:
            # todo determine what should happen, if e.g category has no page
            return CategoryTopic(self._title)

        if isinstance(self.identifier, int):
            return DbTopic(self.identifier)

        return StaticTopic(self.identifier)


class CategoryNode(Node):
    SPEC = "C"

    def __init__(self, data):
        super().__init__(*self._parse(data))

    def __str__(self):
        return self.navPattern % "".join([str(c) for c in self.children])

    @cached_property
    def navPattern(self):
        pattern = '<div class="%s">'
        if self._isSubMenu:
            classes = ['item']
        else:
            classes = ['ui', 'simple', 'dropdown', 'item']
        if self.isActive:
            classes.append('active')
        opener = pattern % (" ".join(classes))
        if self.hasContent:
            opener += '<a href="%s">%s</a>' % (self.relPath, self.title)
        else:
            opener += self.title
        opener += ' <i class="dropdown icon"></i>'
        opener += '<div class="menu">'
        return "%s%%s</div></div>" % opener

    @classmethod
    def _parse(cls, data):
        sep = "|"
        sd = data.split(sep)
        if len(sd) > 2:
            raise ValueError("Too many '%s' in %s" % (sep, data))

        title = sd[0].strip()
        title = title if title != "Home" else ""
        mainTopicId = int(sd[1].strip()) if len(sd) == 2 else None
        return mainTopicId, title

    @cached_property
    def _isSubMenu(self):
        return (isinstance(self, CategoryNode) and
                any(isinstance(c, CategoryNode) for c in self.parents[1:]))


class ArticleNode(Node):
    SPEC = "A"

    def __str__(self):
        pattern = '<a class="%s" href="%s">%s</a>'
        classes = ['item']
        if self.isActive:
            classes.append('active')
        return pattern % (" ".join(classes), self.relPath, self.title)


class CategoryTopic:
    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<CategoryTopic(%s (%s))>" % (self.title, self.identifier)

    @cached_property
    def html(self):
        return "#### HTML TODO ###"


class StaticTopic:
    def __init__(self, identifier):
        self.identifier = identifier

    def __repr__(self):
        return "<StaticTopic(%s (%s))>" % (self.title, self.identifier)

    @cached_property
    def slug(self):
        return slugify(self.title)

    @cached_property
    def title(self):
        return self.md.title

    @cached_property
    def html(self):
        return AdfdParser().to_html(self.bbcode)

    @cached_property
    def bbcode(self):
        return self.content

    # @cached_property
    @cached_property
    def content(self):
        grabber = ContentGrabber(PATH.STATIC / 'content' / self.identifier)
        return grabber.grab()

    @cached_property
    def lastUpdate(self):
        raise NotImplementedError

    @cached_property
    def md(self):
        return PageMetadata(text=self.content)


class DbTopic:
    TITLE_PATTERN = '[h2]%s[/h2]\n'

    def __init__(self, topicId):
        self.id = topicId
        self.postIds = self._get_post_ids()

    def __repr__(self):
        return "<DbTopic(%s (%s))>" % (self.title, self.id)

    @cached_property
    def title(self):
        return self.posts[0].subject

    # @cached_property
    @cached_property
    def html(self):
        return AdfdParser().to_html(self.bbcode)

    # @cached_property
    @cached_property
    def bbcode(self):
        return self.content

    @cached_property
    def content(self):
        contents = []
        for post in self.posts:
            if post.isExcluded:
                continue

            content = ''
            if self.md.useTitles:
                title = post.md.title or post.subject
                content += self.TITLE_PATTERN % title
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
        wrapper = DbWrapper()
        forumId = wrapper.topic_id_2_forum_id(self.id)
        if forumId not in SITE.ALLOWED_FORUM_IDS:
            if self.id not in SITE.ALLOWED_TOPIC_IDS:
                name = wrapper.forum_id_2_forum_name(forumId)
                raise TopicNotAccessible(
                    "%s in %s (%s)", self.id, name, forumId)

        ids = wrapper.topic_id_2_db_posts(self.id)
        if not ids:
            raise TopicDoesNotExist(str(self.id))

        return ids


class Post:
    def __init__(self, postId):
        self.id = postId

    def __repr__(self):
        return "<%s %s (%s)>" % (self.__class__.__name__, self.id, self.slug)

    @cached_property
    def subject(self):
        return self._preprocess(self.dbp.post_subject)

    @cached_property
    def content(self):
        content = self._preprocess(self.dbp.post_text, self.dbp.bbcode_uid)
        content = self._fix_db_storage_patterns(content)
        content = self._fix_whitespace(content)
        return content

    @cached_property
    def slug(self):
        return slugify(self.subject)

    @cached_property
    def postTime(self):
        return self.dbp.post_edit_time or self.dbp.post_time

    @cached_property
    def md(self):
        return PageMetadata(text=self.content)

    @cached_property
    def username(self):
        username = (self.dbp.post_username or
                    DbWrapper().get_username(self.dbp.poster_id))
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
    def dbp(self):
        dbp = DbWrapper().fetch_post(self.id)
        if not dbp:
            raise PostDoesNotExist(str(self.id))

        return dbp
