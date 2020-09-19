import logging
import re
import traceback
from functools import total_ordering

from adfd.cnf import PATH, SITE, NAME
from adfd.db.lib import DbPost
from adfd.metadata import PageMetadata
from adfd.parse import AdfdParser
from adfd.process import date_from_timestamp, slugify, ContentGrabber
from cached_property import cached_property
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name

log = logging.getLogger(__name__)


@total_ordering
class Node:
    SPEC = "N"
    BROKEN_TEXT = "<h1>Konnte nicht geparsed werden</h1>"
    BROKEN_METADATA_TEXT = '[mod=Redakteur]Metadaten fehlerhaft[/mod]\n'
    UNKNOWN_METADATA_PATT = '[mod=Redakteur]unbekannte Metadaten: %s[/mod]\n'
    REPO_URL = "https://github.com/ADFD/adfd/tree/master/adfd/site"

    def __init__(self, identifier, title=None, isOrphan=False):
        self.identifier = identifier
        self._title = title
        self.parents = []
        """:type: list of Node"""
        self.children = []
        """:type: list of Node"""
        self.isActive = False
        self.isOrphan = isOrphan
        self.requestPath = None
        self.bbcodeIsActive = False

    def __repr__(self):
        return "<%s(%s: %s)>" % (self.SPEC, self.identifier, self.title[:6])

    def __gt__(self, other):
        return self.title > other.title

    @property
    def isSane(self):
        try:
            return (self.identifier != SITE.PLACEHOLDER_TOPIC_ID and
                    isinstance(self._bbcode, str) and
                    isinstance(self.title, str) and
                    isinstance(self.relPath, str))
        except Exception as e:
            log.warning(f"{self.identifier} is not sane ({e})")
            return False

    @cached_property
    def isHome(self):
        return not self.parents

    @cached_property
    def slug(self):
        """:rtype: str"""
        isRoot = self.isCategory and self._title == ''
        return '' if isRoot else slugify(self.title)

    @cached_property
    def relPath(self):
        return "/".join([c.slug for c in self.parents + [self]]) or "/"

    @cached_property
    def title(self):
        return self._title or self._container.title or "Start"

    def __html__(self):
        """mark as safe html object and show the right content"""
        if not self.hasArticle:
            return None

        if self.bbcodeIsActive:
            return self._bbcodeAsHtml

        return self.html

    # @cached_property
    @property
    def html(self):
        from adfd.site.wsgi import NAV
        return NAV.replace_links(self._rawHtml)

    @cached_property
    def _rawHtml(self):
        try:
            return self._parser.to_html(self._bbcode)
        except Exception:
            return ("%s<div><pre>%s</pre></div>" %
                    (self.BROKEN_TEXT, traceback.format_exc()))

    @cached_property
    def creationDate(self):
        return self._container.creationDate

    @cached_property
    def lastUpdate(self):
        return self._container.lastUpdate

    @cached_property
    def allAuthors(self):
        md = self._container.md
        aa = [a.strip() for a in md.allAuthors.split(",") if a.strip()]
        return aa or [self._container.author]

    @cached_property
    def hasOneAuthor(self):
        return len(self.allAuthors) == 1

    @cached_property
    def sourceLink(self):
        if isinstance(self._container, StaticArticleContainer):
            parts = self.REPO_URL, NAME.STATIC, NAME.CONTENT, self.identifier
            return "/".join(parts)
        if isinstance(self._container, DbArticleContainer):
            return SITE.TOPIC_REL_PATH_PATTERN % self.identifier

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
        return "HTML zeigen" if self.bbcodeIsActive else "BBCode zeigen"

    @cached_property
    def isCategory(self):
        return isinstance(self, CategoryNode)

    @cached_property
    def hasArticle(self):
        return isinstance(self._container, ArticleContainer)

    @cached_property
    def isForeign(self):
        if isinstance(self._container, NoContentContainer):
            return False

        return self._container.isForeign

    @cached_property
    def hasTodos(self):
        if isinstance(self._container, NoContentContainer):
            return False

        return "[mod=" in self._bbcode

    @cached_property
    def hasSmilies(self):
        if isinstance(self._container, NoContentContainer):
            return False

        return bool(self.smilies)

    @cached_property
    def hasBrokenMetadata(self):
        if isinstance(self._container, NoContentContainer):
            return False

        return self._container.md._isBroken

    @cached_property
    def unknownMetadata(self):
        if isinstance(self._container, NoContentContainer):
            return []

        return self._container.md.invalidAttributes

    @cached_property
    def smilies(self):
        match = re.search(r'(:[^\s/\[\]\.@]*?:)', self._bbcode)
        return match.groups() if match else ()

    @cached_property
    def isDirty(self):
        if isinstance(self._container, NoContentContainer):
            return False

        return len(self.unknownTags) > 0

    @cached_property
    def bbcodeIsBroken(self):
        return not self.isCategory and self.BROKEN_TEXT in self._rawHtml

    @cached_property
    def unknownTags(self):
        # noinspection PyStatementEffect
        self._rawHtml  # ensure parsing has happened
        unknownTags = []
        for tag in [t for t in self._parser.unknownTags if t.strip()]:
            try:
                int(tag)
                continue

            except ValueError:
                pass

            if any(e in tag for e in SITE.IGNORED_TAG_ELEMENTS):
                continue

            unknownTags.append(tag)

        return unknownTags

    @cached_property
    def _bbcode(self):
        if isinstance(self._container, NoContentContainer):
            return ""
        content = self._container._content
        if self._container.md._isBroken:
            content = self.BROKEN_METADATA_TEXT + content
        if self.unknownMetadata:
            # noinspection PyTypeChecker
            content = (self.UNKNOWN_METADATA_PATT %
                       ", ".join(self.unknownMetadata) + content)
        return content

    @cached_property
    def _bbcodeAsHtml(self):
        style = get_style_by_name('igor')
        formatter = HtmlFormatter(style=style)
        lexer = get_lexer_by_name("bbcode", stripall=True)
        css = formatter.get_style_defs()
        txt = highlight(self._bbcode, lexer, HtmlFormatter())
        return "<style>%s</style>\n%s" % (css, txt)

    @cached_property
    def _container(self):
        if not self.identifier:
            return NoContentContainer(self._title, self.children)

        if isinstance(self.identifier, int):
            return DbArticleContainer(self.identifier)

        return StaticArticleContainer(self.identifier)

    @cached_property
    def _parser(self):
        return AdfdParser()


class CategoryNode(Node):
    SPEC = "C"

    def __init__(self, data):
        super().__init__(*self._parse(data))

    def __str__(self):
        return self._navPattern % "".join([str(c) for c in self.children])

    @cached_property
    def _navPattern(self):
        pattern = '<div class="%s">'
        if self._isSubMenu:
            classes = ['item']
        else:
            classes = ['ui', 'simple', 'dropdown', 'item']
        if self.isActive:
            classes.append('active')
        tag = pattern % (" ".join(classes))
        if self._isSubMenu:
            tag += '<i class="orange dropdown icon"></i>'
        padding = "&nbsp;" * 3 if self._isSubMenu else ''
        tag += '<a href="%s">%s</a>%s' % (self.relPath, self.title, padding)
        if not self._isSubMenu:
            tag += '<i class="orange dropdown icon"></i>'
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

    def __init__(self, data, isOrphan=False):
        super().__init__(*self._parse(data), isOrphan=isOrphan)

    def __str__(self):
        p = '<a class="%s" href="%s">%s</a>'
        classes = ['item']
        if self.isActive:
            classes.append('active')
        classesStr = " ".join(classes)
        try:
            return p % (classesStr, self.relPath, self.title)
        except Exception as e:
            msg = f"broken: {self.identifier} ({e})"
            html = p % (classesStr, "#", msg)
            log.warning(msg)
            return html

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


class ArticleContainer:
    def __init__(self, identifier):
        self.identifier = identifier

    def __repr__(self):
        return "<%s(%s)" % (self.__class__.__name__, self.identifier)


class NoContentContainer:
    def __init__(self, identifier, children):
        self.identifier = identifier
        self.children = children


class DbArticleContainer(ArticleContainer):
    TITLE_PATTERN = '[h1]%s[/h1]\n'

    @cached_property
    def title(self):
        return self._firstPost.subject

    @cached_property
    def author(self):
        return self._firstPost.username

    @cached_property
    def creationDate(self):
        return date_from_timestamp(self._firstPost.postTime)

    @cached_property
    def lastUpdate(self):
        newestDate = sorted([p.postTime for p in self._posts], reverse=True)[0]
        return date_from_timestamp(newestDate)

    @cached_property
    def md(self):
        return self._firstPost.md

    @cached_property
    def _bbcode(self):
        return self._content

    @cached_property
    def _content(self):
        contents = []
        for post in self._posts:
            assert isinstance(post, DbPost)
            if self.md.useTitles and post != self._firstPost:
                contents.append(self.TITLE_PATTERN % post.subject)
            contents.append(post.content)
        return "\n\n".join(contents)

    @cached_property
    def _firstPost(self):
        return self._posts[0]

    @cached_property
    def _posts(self):
        """:rtype: list of DbPost"""
        firstPostId = self._postIds[0]
        firstPost = DbPost(firstPostId)
        posts = [firstPost] if not firstPost.isExcluded else []
        if firstPost.md.firstPostOnly:
            return [firstPost]

        for postId in self._postIds[1:]:
            post = DbPost(postId)
            if not post.isExcluded and post.isVisible:
                posts.append(post)

        return posts

    @cached_property
    def _postIds(self):
        return DbPost.get_post_ids_for_topic(self.identifier)

    @cached_property
    def isForeign(self):
        return self._firstPost.dbp.forum_id != SITE.MAIN_CONTENT_FORUM_ID

    @cached_property
    def isImported(self):
        return self._firstPost.dbp.forum_id == 54


class StaticArticleContainer(ArticleContainer):
    @cached_property
    def title(self):
        return False

    @cached_property
    def creationDate(self):
        return self._grabber.get_ctime()

    @cached_property
    def lastUpdate(self):
        return self._grabber.get_mtime()

    @cached_property
    def _content(self):
        return self._grabber.grab()

    @cached_property
    def md(self):
        return PageMetadata(text=self._content)

    @cached_property
    def _grabber(self):
        return ContentGrabber(PATH.STATIC / 'content' / self.identifier)

    @cached_property
    def isForeign(self):
        return False

    @cached_property
    def isImported(self):
        return True
