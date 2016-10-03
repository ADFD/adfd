import logging

from adfd.cnf import PATH
from adfd.db.lib import DbPost
from adfd.metadata import PageMetadata
from adfd.parse import AdfdParser
from adfd.utils import slugify, ContentGrabber, date_from_timestamp
from cached_property import cached_property

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

    @cached_property
    def title(self):
        return self._title or self.topic.title

    def __html__(self):
        """In a template: ``{{ page }}`` == ``{{ page.html|safe }}``."""
        return self.html

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
        if not self.identifier:
            return CategoryContentContainer(self._title)  # TODO needed?

        if isinstance(self.identifier, int):
            return DbContentContainer(self.identifier)

        return StaticContentContainer(self.identifier)


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


class ContentContainer:
    def __init__(self, identifier):
        self.identifier = identifier

    def __repr__(self):
        return ("<%s(%s) -> (%s>" %
                (self.__class__.__name__, self.identifier, self.title))

    @property
    def title(self):
        raise NotImplementedError

    @cached_property
    def allAuthors(self):
        """list of authors (at least one)"""
        raise NotImplementedError

    @cached_property
    def lastUpdate(self):
        raise NotImplementedError

    @cached_property
    def html(self):
        raise NotImplementedError

    @cached_property
    def bbcode(self):
        raise NotImplementedError


class CategoryContentContainer(ContentContainer):
    @property
    def title(self):
        return self.identifier


class StaticContentContainer(ContentContainer):
    @cached_property
    def title(self):
        return self.md.title

    @cached_property
    def allAuthors(self):
        return self.md.allAuthors

    @cached_property
    def lastUpdate(self):
        return self._grabber.get_mtime()

    @cached_property
    def html(self):
        return AdfdParser().to_html(self.bbcode)

    @cached_property
    def bbcode(self):
        return self.content

    @cached_property
    def content(self):
        return self._grabber.grab()

    @cached_property
    def md(self):
        return PageMetadata(text=self.content)

    @cached_property
    def _grabber(self):
        return ContentGrabber(PATH.STATIC / 'content' / self.identifier)


class DbContentContainer(ContentContainer):
    TITLE_PATTERN = '[h2]%s[/h2]\n'

    @cached_property
    def title(self):
        return self.md.title or self.firstPost.title

    @cached_property
    def allAuthors(self):
        return self.md.allAuthors or [self.firstPost.username]

    @cached_property
    def lastUpdate(self):
        newestDate = sorted([p.postTime for p in self.posts], reverse=True)[0]
        return date_from_timestamp(newestDate)

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
            if self.md.useTitles:
                contents.append(self.TITLE_PATTERN % post.title)
            contents.append(post.content)
        return "\n\n".join(contents)

    @cached_property
    def md(self):
        return self.firstPost.md

    @cached_property
    def firstPost(self):
        return self.posts[0]

    @cached_property
    def posts(self):
        """:rtype: list of DbPost"""
        posts = []
        for postId in self.postIds:
            post = DbPost(postId)
            if not post.isExcluded:
                posts.append(post)
        return posts

    @cached_property
    def postIds(self):
        return DbPost.get_post_ids_for_topic(self.identifier)
