import html
import io
import logging
import re
from collections import OrderedDict

from cached_property import cached_property
from werkzeug.utils import cached_property
import yaml

from adfd.cnf import SITE, PATH
from adfd.db.lib import DbWrapper
from adfd.metadata import PageMetadata
from adfd.exc import *
from adfd.parse import AdfdParser, extract_from_bbcode
from adfd.utils import slugify, ContentGrabber, date_from_timestamp

log = logging.getLogger(__name__)


class StaticTopic:
    def __init__(self, identifier):
        self.identifier = identifier

    @cached_property
    def slug(self):
        return slugify(self.subject)

    @cached_property
    def subject(self):
        return self.md.title

    @cached_property
    def html(self):
        return AdfdParser().to_html(self.bbcode)

    @cached_property
    def bbcode(self):
        return self.content

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


class Topic:
    TITLE_PATTERN = '[h2]%s[/h2]\n'

    def __init__(self, topicId):
        self.id = topicId
        self.postIds = self._get_post_ids()

    def __repr__(self):
        return "<Topic(%s (%s))>" % (self.subject, self.id)

    @cached_property
    def subject(self):
        return self.posts[0].subject

    @cached_property
    def html(self):
        return AdfdParser().to_html(self.bbcode)

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
                content += self.TITLE_PATTERN % self.md.title
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
        md = PageMetadata(
            kwargs=dict(
                author=self.username,
                authorId=self.dbp.poster_id,
                lastUpdate=self.lastUpdate,
                postDate=date_from_timestamp(self.dbp.post_time),
                postId=self.id,
                title=self.subject,
                topicId=self.topicId),
            text=self.content)
        return md

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


# Fixme Markup should have nothing to do in here
# find a way to move the representational part completely into the view
# (how about a recursive jinja2 macro that generates navigation from nodes?)
class Node:
    SPEC = "N"

    def __init__(self, identifier, name=None):
        self.identifier = identifier
        self.isHome = name == ''
        self._name = name
        self.parents = []
        """:type: list of Node"""
        self.children = []
        """:type: list of Node"""
        self.isActive = False

    def __repr__(self):
        return "<%s(%s: %s)>" % (self.SPEC, self.identifier, self.name[:6])

    def __html__(self):
        """In a template: ``{{ page }}`` == ``{{ page.html|safe }}``."""
        return self.html

    # def __getitem__(self, name):
    #     """Shortcut for accessing metadata.
    #
    #     ``page['title']`` == ``{{ page.title }}`` == ``page.meta['title']``.
    #     """
    #     return self.topic.md[name]

    @property
    def relPath(self):
        return "/".join([c.slug for c in self.crumbs])

    @property
    def crumbs(self):
        return self.parents + [self]

    @cached_property
    def html(self):
        return self.topic.html

    # Todo return file path if it is a static page
    @cached_property
    def link(self):
        return "http://adfd.org/austausch/viewtopic.php?t=%s" % self.topic.id

    @cached_property
    def name(self):
        return self._name or self.topic.subject

    @cached_property
    def slug(self):
        """:rtype: str"""
        return slugify(self.name) if not self.isHome else ''

    @property
    def hasContent(self):
        return self.identifier is not None

    @property
    def isSubMenu(self):
        return (isinstance(self, CategoryNode) and
                any(isinstance(c, CategoryNode) for c in self.parents))

    @cached_property
    def topic(self):
        """:rtype: adfd.db.model.Topic"""
        # FIXME seems to be never called -> remove
        if not self.identifier:
            # todo determine what should happen, if e.g category has no page
            raise NotImplementedError

        if isinstance(self.identifier, int):
            return Topic(self.identifier)

        return StaticTopic(self.identifier)

    @property
    def navHtml(self):
        return self.navHtmlOpener + self.navHtmlCloser

    @property
    def navHtmlOpener(self):
        raise NotImplementedError

    @cached_property
    def navHtmlCloser(self):
        raise NotImplementedError


class CategoryNode(Node):
    SPEC = "C"

    def __init__(self, data):
        super().__init__(*self._parse(data))

    def __str__(self):
        return (self.navHtmlOpener +
                "".join([str(c) for c in self.children]) +
                self.navHtmlCloser)

    @property
    def navHtmlOpener(self):
        pattern = '<div class="%s">'
        if self.isSubMenu:
            classes = ['item']
        else:
            classes = ['ui', 'simple', 'dropdown', 'item']
        if self.isActive:
            classes.append('active')
        opener = pattern % (" ".join(classes))
        if self.hasContent:
            opener += '<a href="%s">%s</a>' % (self.relPath, self.name)
        else:
            opener += self.name
        opener += ' <i class="dropdown icon"></i>'
        opener += '<div class="menu">'
        return opener

    @property
    def navHtmlCloser(self):
        return '</div></div>'

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


class ArticleNode(Node):
    SPEC = "A"

    def __str__(self):
        return self.navHtml

    @property
    def navHtmlOpener(self):
        pattern = '<a class="%s" href="%s">%s'
        classes = ['item']
        if self.isActive:
            classes.append('active')
        return pattern % (" ".join(classes), self.relPath, self.name)

    @cached_property
    def navHtmlCloser(self):
        return '</a>'


class StructureLoader:
    @classmethod
    def load(cls):
        if SITE.USE_FILE:
            return cls.ordered_yaml_load(stream=open(SITE.STRUCTURE_PATH))

        post = Topic(SITE.STRUCTURE_TOPIC_ID)
        stream = io.StringIO(extract_from_bbcode(SITE.META_TAG, post.content))
        return cls.ordered_yaml_load(stream=stream)

    @classmethod
    def ordered_yaml_load(cls, stream):
        class OrderedLoader(yaml.SafeLoader):
            pass

        def construct_mapping(loader, node):
            loader.flatten_mapping(node)
            return OrderedDict(loader.construct_pairs(node))

        # noinspection PyUnresolvedReferences
        OrderedLoader.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            construct_mapping)
        return yaml.load(stream, OrderedLoader)
