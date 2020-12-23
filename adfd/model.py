import json
import logging
import re
import traceback
from functools import total_ordering
from typing import List, Union

import plumbum
from cached_property import cached_property
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name

from adfd.cnf import NAME, PATH, SITE, EXT
from adfd.db.lib import DbPost
from adfd.metadata import PageMetadata
from adfd.parse import AdfdParser
from adfd.process import ContentGrabber, date_from_timestamp, slugify

log = logging.getLogger(__name__)


@total_ordering
class Node:
    SPEC = "N"
    BROKEN_TEXT = "<h1>Konnte nicht geparsed werden</h1>"
    BROKEN_METADATA_TEXT = "[mod=Redakteur]Metadaten fehlerhaft[/mod]\n"
    UNKNOWN_METADATA_PATT = "[mod=Redakteur]unbekannte Metadaten: %s[/mod]\n"
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
        self.bbcode_is_active = False

    def __repr__(self):
        return "<{}({}: {})>".format(self.SPEC, self.identifier, self.title[:6])

    def __gt__(self, other):
        return self.title > other.title

    @property
    def isSane(self):
        try:
            return (
                self.identifier != SITE.PLACEHOLDER_TOPIC_ID
                and isinstance(self._bbcode, str)
                and isinstance(self.title, str)
                and isinstance(self.relPath, str)
            )
        except Exception as e:
            log.warning(f"{self.identifier} is not sane ({e})")
            return False

    @property
    def isHome(self):
        return not self.parents

    @property
    def slug(self):
        """:rtype: str"""
        isRoot = self.isCategory and self._title == ""
        return "" if isRoot else slugify(self.title)

    @property
    def relPath(self):
        return "/".join([c.slug for c in self.parents + [self]]) or "/"

    @property
    def title(self):
        return self._title or self._container.title or "Start"

    def __html__(self):
        """mark as safe html object and show the right content"""
        if not self.hasArticle:
            return None

        if self.bbcode_is_active:
            return self._bbcodeAsHtml

        return self.html

    @property
    def html(self):
        from adfd.site.wsgi import NAV

        return NAV.replace_links(self._rawHtml)

    @property
    def _rawHtml(self):
        try:
            return self._parser.to_html(self._bbcode)
        except Exception:
            return "{}<div><pre>{}</pre></div>".format(
                self.BROKEN_TEXT, traceback.format_exc(),
            )

    @property
    def creationDate(self):
        return self._container.creationDate

    @property
    def lastUpdate(self):
        return self._container.lastUpdate

    @property
    def allAuthors(self):
        md = self._container.md
        aa = [a.strip() for a in md.allAuthors.split(",") if a.strip()]
        return aa or [self._container.author]

    @property
    def hasOneAuthor(self):
        return len(self.allAuthors) == 1

    @property
    def sourceLink(self):
        if isinstance(self._container, StaticArticleContainer):
            parts = self.REPO_URL, NAME.STATIC, NAME.CONTENT, self.identifier
            return "/".join(parts)
        if isinstance(self._container, DbArticleContainer):
            return SITE.TOPIC_REL_PATH_PATTERN % self.identifier

    @property
    def contentToggleLink(self):
        assert self.requestPath
        if self.bbcode_is_active:
            path = self.requestPath.partition(NAME.BBCODE)[-1]
        else:
            path = "/" + NAME.BBCODE
            if self.requestPath != "/":
                path = f"{path}{self.requestPath}"
        return path

    @property
    def contentToggleLinkText(self):
        return "HTML zeigen" if self.bbcode_is_active else "BBCode zeigen"

    @property
    def isCategory(self):
        return isinstance(self, CategoryNode)

    @property
    def hasArticle(self):
        return isinstance(self._container, ArticleContainer)

    @property
    def isForeign(self):
        if isinstance(self._container, NoContentContainer):
            return False

        return self._container.isForeign

    @property
    def hasTodos(self):
        if isinstance(self._container, NoContentContainer):
            return False

        return "[mod=" in self._bbcode

    @property
    def hasSmilies(self):
        if isinstance(self._container, NoContentContainer):
            return False

        return bool(self.smilies)

    @property
    def hasBrokenMetadata(self):
        if isinstance(self._container, NoContentContainer):
            return False

        return self._container.md._isBroken

    @property
    def unknownMetadata(self):
        if isinstance(self._container, NoContentContainer):
            return []

        return self._container.md.invalid_keys

    @property
    def smilies(self):
        match = re.search(r"(:[^\s/\[\].@]*?:)", self._bbcode)
        return match.groups() if match else ()

    @property
    def isDirty(self):
        if isinstance(self._container, NoContentContainer):
            return False

        return len(self.unknownTags) > 0

    @property
    def bbcodeIsBroken(self):
        return not self.isCategory and self.BROKEN_TEXT in self._rawHtml

    @property
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

    @property
    def _bbcode(self):
        if isinstance(self._container, NoContentContainer):
            return ""
        content = self._container._content
        if self._container.md._isBroken:
            content = self.BROKEN_METADATA_TEXT + content
        if self.unknownMetadata:
            content = (
                self.UNKNOWN_METADATA_PATT % ", ".join(self.unknownMetadata) + content
            )
        return content

    @property
    def _bbcodeAsHtml(self):
        style = get_style_by_name("igor")
        formatter = HtmlFormatter(style=style)
        lexer = get_lexer_by_name("bbcode", stripall=True)
        css = formatter.get_style_defs()
        txt = highlight(self._bbcode, lexer, HtmlFormatter())
        return f"<style>{css}</style>\n{txt}"

    @property
    def _container(self):
        if not self.identifier:
            return NoContentContainer(self._title, self.children)

        if isinstance(self.identifier, int):
            permanent_cache = PATH.DB_CACHE_PERMANENT / f"{self.identifier}"
            if permanent_cache.exists():
                return PermanentlyCachedDbArticleContainer(permanent_cache)

            db_cache = PATH.DB_CACHE_PERMANENT / f"{self.identifier}"
            if db_cache.exists():
                return CachedDbArticleContainer(db_cache)

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

    @property
    def _navPattern(self):
        pattern = '<div class="%s">'
        if self._isSubMenu:
            classes = ["item"]
        else:
            classes = ["ui", "simple", "dropdown", "item"]
        if self.isActive:
            classes.append("active")
        tag = pattern % (" ".join(classes))
        if self._isSubMenu:
            tag += '<i class="orange dropdown icon"></i>'
        padding = "&nbsp;" * 3 if self._isSubMenu else ""
        tag += f'<a href="{self.relPath}">{self.title}</a>{padding}'
        if not self._isSubMenu:
            tag += '<i class="orange dropdown icon"></i>'
        tag += '<div class="menu">'
        return "%s%%s</div></div>" % tag

    @property
    def _isSubMenu(self):
        return isinstance(self, CategoryNode) and any(
            isinstance(c, CategoryNode) for c in self.parents[1:]
        )

    @classmethod
    def _parse(cls, data):
        sep = "|"
        sd = data.split(sep)
        if len(sd) > 2:
            raise ValueError(f"Too many '{sep}' in {data}")

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
        classes = ["item"]
        if self.isActive:
            classes.append("active")
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
            raise ValueError(f"Too many '{sep}' in {data}")

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
    def __init__(self, identifier: Union[int, str]):
        self.identifier = identifier

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.identifier})"


class DbArticleContainer(ArticleContainer):
    TITLE_PATTERN = "[h1]%s[/h1]\n"

    @cached_property
    def title(self):
        return self._firstPost.subject

    @cached_property
    def author(self):
        return self._firstPost.author

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
    def _posts(self) -> List[DbPost]:
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
    def _postIds(self) -> List[int]:
        return DbPost.get_post_ids_for_topic(self.identifier)

    @cached_property
    def isForeign(self) -> bool:
        return self._firstPost.dbp.forum_id != SITE.MAIN_CONTENT_FORUM_ID

    # FIXME isForeign vs isImported only one is needed
    @cached_property
    def isImported(self) -> bool:
        return self._firstPost.dbp.forum_id == SITE.MAIN_CONTENT_FORUM_ID

    def _attrs_for_md_cache(self):
        d = {}
        for name, attr in sorted(self.__class__.__dict__.items()):
            if name.startswith("_"):
                continue

            if name in ["md"]:
                continue

            if name.isupper():
                continue

            attr = getattr(self, name)
            d[name] = attr
        return d


class CachedDbArticleContainer(DbArticleContainer):
    """Cached on filesystem - simulates db objects."""
    def __init__(self, path):
        """path to folder where cached db topic files are stored."""
        assert isinstance(path, plumbum.LocalPath), path
        assert path.exists()
        self.path = path
        super().__init__(path.name)
        self.container_md = json.loads((self.path / f"{self.identifier}{EXT.MD}").read())

    @property
    def title(self) -> str:
        return self.container_md["title"]

    @property
    def author(self) -> str:
        return self.container_md["author"]

    @property
    def creationDate(self) -> str:
        return self.container_md["creationDate"]

    @property
    def lastUpdate(self) -> str:
        return self.container_md["lastUpdate"]

    @property
    def md(self) -> PageMetadata:
        return self._firstPost.md

    @property
    def _bbcode(self) -> str:
        return self._content

    @property
    def _content(self):
        contents = []
        for post in self._posts:
            if self.md.useTitles and post != self._posts[0]:
                contents.append(self.TITLE_PATTERN % post.subject)
            contents.append(post.content)
        return "\n\n".join(contents)

    @property
    def _firstPost(self):
        return self._posts[0]

    @property
    def _posts(self):
        posts = []
        for path in sorted(self.path.glob("*.bbcode")):
            post = CachedDbPost(path)
            if not post.isExcluded and post.isVisible:
                posts.append(post)
        return posts

    @property
    def _postIds(self):
        raise NotImplementedError  # should not be needed here

    @property
    def isForeign(self):
        return self.container_md["isForeign"]

    @property
    def isImported(self):
        return self.container_md["isImported"]


# noinspection PyAbstractClass
class PermanentlyCachedDbArticleContainer(CachedDbArticleContainer):
    """Same func but different name to show where it's stored.

    This cache won't be overwritten, when articles are dumped from db into normal cache.
    """


class CachedDbPost(DbPost):
    def __init__(self, path):
        """path to cached db post are stored."""
        assert isinstance(path, plumbum.LocalPath), path
        assert path.exists()
        self.path = path
        super().__init__(path.stem)

    @property
    def subject(self) -> str:
        return self.md.subject

    @property
    def content(self) -> str:
        return self.path.read()

    @property
    def postTime(self) -> int:
        return self.md.postTime

    @property
    def author(self) -> str:
        return self.md.author

    @property
    def isExcluded(self) -> bool:
        return self.md.isExcluded

    @property
    def isVisible(self) -> bool:
        return self.md.isVisible

    @property
    def md(self) -> PageMetadata:
        post_md = json.loads(self.path.with_suffix(EXT.MD).read())
        return PageMetadata(kwargs=post_md)


class StaticArticleContainer(ArticleContainer):
    @property
    def title(self):
        return False

    @property
    def creationDate(self):
        return self._grabber.get_ctime()

    @property
    def lastUpdate(self):
        return self._grabber.get_mtime()

    @property
    def _content(self):
        return self._grabber.grab()

    @property
    def md(self):
        return PageMetadata(text=self._content)

    @property
    def _grabber(self):
        return ContentGrabber(PATH.CONTENT / self.identifier)

    @property
    def isForeign(self):
        return False

    @property
    def isImported(self):
        return True


class NoContentContainer:
    def __init__(self, identifier, children):
        self.identifier = identifier
        self.children = children
