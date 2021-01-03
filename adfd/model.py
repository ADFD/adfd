import json
import logging
from functools import total_ordering, cached_property
from typing import List, Union, Tuple, Optional

import plumbum
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name

from adfd.cnf import NAME, PATH, ADFD, EXT
from adfd.db.lib import DbPost
from adfd.metadata import PageMetadata
from adfd.parse import ADFD_PARSER
from adfd.process import date_from_timestamp, slugify

log = logging.getLogger(__name__)


@total_ordering
class Node:
    SPEC = "N"

    def __init__(self, identifier, title=None, isOrphan=False):
        self.identifier = identifier
        self._title = title
        self.parents: List[Node] = []
        self.children: List[Node] = []
        self.isActive = False
        self.isOrphan = isOrphan
        self.requestPath = None
        self.bbcode_is_active = False

    def __str__(self):
        return f"{self.SPEC}({self.identifier}|{self.relPath}|{self.title})"

    def __repr__(self):
        return f"<{self.SPEC}({self.identifier}: {self.title[:10]})>"

    def __gt__(self, other):
        return self.relPath > other.relPath

    @cached_property
    def slug(self) -> str:
        return "" if self.isRoot else slugify(self.title)

    @cached_property
    def isRoot(self):
        return self.isCategory and self._title == ""

    @cached_property
    def relPath(self):
        if self.isRoot:
            return "/"

        return "/".join([c.slug for c in self.parents + [self]])

    @cached_property
    def title(self):
        return self._title or self.contcon.title or "Start"

    def __html__(self):
        """mark as safe html object and show the right content"""
        if not self.hasArticle:
            return None

        if self.bbcode_is_active:
            return self._bbcodeAsHtml

        return self.html

    @property
    def html(self):
        from adfd.web.wsgi import NAV

        return NAV.replace_links(self._rawHtml)

    @property
    def _rawHtml(self):
        return ADFD_PARSER.to_html(self.raw_bbcode)

    @cached_property
    def creationDate(self):
        return self.contcon.creationDate

    @cached_property
    def lastUpdate(self):
        return self.contcon.lastUpdate

    @cached_property
    def allAuthors(self):
        md = self.contcon.md
        aa = [a.strip() for a in md.allAuthors.split(",") if a.strip()]
        return aa or [self.contcon.author]

    @cached_property
    def hasOneAuthor(self):
        return len(self.allAuthors) == 1

    @cached_property
    def sourceLink(self):
        return self.contcon.sourceLink

    @cached_property
    def isCategory(self):
        return isinstance(self, CategoryNode)

    @cached_property
    def hasArticle(self):
        return isinstance(self.contcon, ArticleContainer)

    @cached_property
    def raw_bbcode(self):
        if isinstance(self.contcon, NoContentContainer):
            return ""
        return self.contcon.raw_bbcode

    @cached_property
    def _bbcodeAsHtml(self):
        style = get_style_by_name("igor")
        formatter = HtmlFormatter(style=style)
        lexer = get_lexer_by_name("bbcode", stripall=True)
        css = formatter.get_style_defs()
        txt = highlight(self.raw_bbcode, lexer, HtmlFormatter())
        return f"<style>{css}</style>\n{txt}"

    @cached_property
    def contcon(self):
        if not self.identifier:
            return NoContentContainer(self._title, self.children)

        filesys_article_path = PATH.ARTICLES / f"{self.identifier}"
        if filesys_article_path.exists():
            return FilesysArticleContainer(filesys_article_path)

        db_cache_path = PATH.DB_CACHE / f"{self.identifier}"
        if db_cache_path.exists():
            return CachedArticleContainer(db_cache_path)

        return DbArticleContainer(self.identifier)


class CategoryNode(Node):
    SPEC = "C"

    def __init__(self, data):
        super().__init__(*self._parse(data))

    @cached_property
    def is_sub_menu(self):
        return isinstance(self, CategoryNode) and any(
            isinstance(c, CategoryNode) for c in self.parents[1:]
        )

    @classmethod
    def _parse(cls, data):
        sep = "|"
        parts = data.split(sep)
        if len(parts) > 2:
            raise ValueError(f"Too many '{sep}' in {data}")

        title = parts[0].strip()
        title = title if title != "Home" else ""
        category_topic_id = int(parts[1].strip()) if len(parts) == 2 else None
        return category_topic_id, title


class ArticleNode(Node):
    SPEC = "A"
    HOME_NODE = "Home"

    def __init__(self, data, isOrphan=False):
        super().__init__(*self._parse(data), isOrphan=isOrphan)

    @classmethod
    def _parse(cls, data) -> Tuple[int, Optional[str]]:
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
    def sourceLink(self):
        return f"{ADFD.FORUM_VIEWTOPIC_URL}?t={self.identifier}"

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
    def raw_bbcode(self):
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
        # TODO extra metadata only for qa purposes

        return d


class CachedArticleContainer(DbArticleContainer):
    """Cached on filesystem - simulates db objects.

    Structure provided by dump_db_articles_to_file_cache
    """

    def __init__(self, path):
        """path to folder where cached db topic files are stored."""
        assert isinstance(path, plumbum.LocalPath), path
        assert path.exists()
        self.path = path
        super().__init__(path.name)
        self.container_md = json.loads(
            (self.path / f"{self.identifier}{EXT.MD}").read()
        )

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
    def raw_bbcode(self):
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
            post = FilesysPost(path)
            if not post.isExcluded and post.isVisible:
                posts.append(post)
        return posts

    @property
    def _postIds(self):
        raise NotImplementedError  # should not be needed here


class FilesysArticleContainer(CachedArticleContainer):
    """Same func but different name to show where it's stored.

    This cache won't be overwritten, when articles are dumped from db into normal cache.
    """

    @cached_property
    def sourceLink(self):
        return f"{ADFD.REPO_URL}/{NAME.ARTICLES}/{self.identifier}/"


class FilesysPost(DbPost):
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
        return PageMetadata(mapping=post_md)


class NoContentContainer:
    def __init__(self, identifier, children):
        self.identifier = identifier
        self.children = children
