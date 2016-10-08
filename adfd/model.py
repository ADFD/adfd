import logging

from cached_property import cached_property
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name

from adfd.cnf import PATH, SITE, NAME
from adfd.db.lib import DbPost
from adfd.metadata import PageMetadata
from adfd.parse import AdfdParser
from adfd.utils import slugify, ContentGrabber, date_from_timestamp
from pygments.styles import get_style_by_name

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
        return "<%s(%s: %s)>" % (
            self.SPEC, self.identifier, self.title[:6])

    @cached_property
    def title(self):
        if not self.parents:
            return "Start"

        return self._title or self.article.subject

    @cached_property
    def relPath(self):
        return "/".join([c.slug for c in self.parents + [self]]) or "/"

    @cached_property
    def sourceLink(self):
        if isinstance(self.article, StaticContentContainer):
            return "/%s/%s" % (NAME.STATIC, self.identifier)

        elif isinstance(self.article, DbContentContainer):
            return SITE.VIEWTOPIC_PATTERN % self.identifier

        raise NotImplementedError(str(type(self.article)))

    @cached_property
    def slug(self):
        """:rtype: str"""
        isRoot = isinstance(self, CategoryNode) and self._title == ''
        return '' if isRoot else slugify(self.title)

    @cached_property
    def hasContent(self):
        return self.identifier is not None

    @cached_property
    def article(self):
        if not self.identifier:
            return CategoryContentContainer(self._title)

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
    def slug(self):
        return slugify(self._title)

    @cached_property
    def navPattern(self):
        pattern = '<div class="%s">'
        if self._isSubMenu:
            classes = ['item']
        else:
            classes = ['ui', 'simple', 'dropdown', 'item']
        if self.isActive:
            classes.append('active')
        tag = pattern % (" ".join(classes))
        if self.hasContent:
            tag += '<a href="%s">%s</a>' % (self.relPath, self.title)
        else:
            tag += self.title
        tag += '<i class="dropdown icon"></i>'
        tag += '<div class="menu">'
        return "%s%%s</div></div>" % tag

    @cached_property
    def _isSubMenu(self):
        return (isinstance(self, CategoryNode) and
                any(isinstance(c, CategoryNode) for c in self.parents[1:]))

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
    HOME_NODE = "Home"

    def __init__(self, data):
        super().__init__(*self._parse(data))

    def __str__(self):
        pattern = '<a class="%s" href="%s">%s</a>'
        classes = ['item']
        if self.isActive:
            classes.append('active')
        return pattern % (" ".join(classes), self.relPath, self.title)

    @classmethod
    def _parse(cls, data):
        """returns: (identifier, title)"""
        if isinstance(data, int):
            return data, None

        identifier = None
        assert isinstance(data, str)
        sep = "|"
        sd = data.split(sep)
        if len(sd) > 2:
            raise ValueError("Too many '%s' in %s" % (sep, data))

        title = sd[0].strip()
        title = title if title != cls.HOME_NODE else ""
        if len(sd) == 2:
            txt = sd[1].strip()
            try:
                identifier = int(txt)
            except ValueError:
                identifier = txt
        return identifier, title


class ContentContainer:
    def __init__(self, identifier):
        self.identifier = identifier
        self.requestPath = None
        self.bbcodeIsActive = False

    def __repr__(self):
        return "<%s(%s)" % (self.__class__.__name__, self.identifier)

    @cached_property
    def allAuthors(self):
        """list of authors (at least one)"""
        raise NotImplementedError

    @cached_property
    def hasOneAuthor(self):
        return len(self.allAuthors) == 1

    @cached_property
    def creationDate(self):
        raise NotImplementedError

    @cached_property
    def lastUpdate(self):
        raise NotImplementedError

    def __html__(self):
        """mark article as safe html object and show the right content"""
        if self.bbcodeIsActive:
            return self.bbcodeAsHtml

        return self.html

    @cached_property
    def html(self):
        raise NotImplementedError

    @cached_property
    def bbcode(self):
        raise NotImplementedError

    @property
    def contentToggleLink(self):
        assert self.requestPath
        if self.bbcodeIsActive:
            path = self.requestPath.partition(NAME.BBCODE)[-1]
        else:
            path = "/" + NAME.BBCODE
            if self.requestPath != "/":
                path = "%s%s" % (path, self.requestPath)
        return path

    @property
    def contentToggleLinkText(self):
        return "BBCode" if self.bbcodeIsActive else "HTML"

    @cached_property
    def bbcodeAsHtml(self):
        style = get_style_by_name('igor')
        formatter = HtmlFormatter(style=style)
        lexer = get_lexer_by_name("bbcode", stripall=True)
        css = formatter.get_style_defs()
        txt = highlight(self.bbcode, lexer, HtmlFormatter())
        return "<style>%s</style>\n%s" % (css, txt)


class CategoryContentContainer(ContentContainer):
    pass

class StaticContentContainer(ContentContainer):
    @cached_property
    def allAuthors(self):
        return self.md.allAuthors

    @cached_property
    def creationDate(self):
        return self._grabber.get_ctime()

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
    TITLE_PATTERN = '[h1]%s[/h1]\n'

    @cached_property
    def subject(self):
        return self._firstPost.subject

    @cached_property
    def allAuthors(self):
        return self.md.allAuthors or [self._firstPost.username]

    @cached_property
    def creationDate(self):
        return date_from_timestamp(self._firstPost.postTime)

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
            assert isinstance(post, DbPost)
            if self.md.useTitles and post != self._firstPost:
                contents.append(self.TITLE_PATTERN % post.subject)
            contents.append(post.content)
        return "\n\n".join(contents)

    @cached_property
    def md(self):
        return self._firstPost.md

    @cached_property
    def _firstPost(self):
        return self.posts[0]

    @cached_property
    def posts(self):
        """:rtype: list of DbPost"""
        firstPostId = self.postIds[0]
        firstPost = DbPost(firstPostId)
        posts = [firstPost]
        if firstPost.md.firstPostOnly:
            return [firstPost]

        for postId in self.postIds[1:]:
            post = DbPost(postId)
            if not post.isExcluded and post.isVisible:
                posts.append(post)

        return posts

    @cached_property
    def postIds(self):
        return DbPost.get_post_ids_for_topic(self.identifier)
