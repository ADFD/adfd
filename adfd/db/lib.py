import html
import logging
from typing import List

from bs4 import BeautifulSoup
from cached_property import cached_property
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from adfd.cnf import DB, SITE
from adfd.db.schema import PhpbbForum, PhpbbPost, PhpbbTopic, PhpbbUser
from adfd.exc import PostDoesNotExist, TopicDoesNotExist, TopicNotAccessible
from adfd.metadata import PageMetadata

log = logging.getLogger(__name__)
logging.getLogger("sqlalchemy").setLevel(logging.WARNING)


class _DbWrapper:
    """very simple wrapper that can fetch the little that is needed"""

    @cached_property
    def session(self) -> Session:
        session = sessionmaker()
        engine = create_engine(DB.URL, echo=False)
        session.configure(bind=engine)
        return session()

    def get_topic_ids(self, forumId) -> List[int]:
        query = self.session.query(PhpbbTopic).filter(PhpbbTopic.forum_id == forumId)
        return [t.topic_id for t in query]

    def get_topic(self, topicId) -> PhpbbTopic:
        return (
            self.session.query(PhpbbTopic)
            .filter(PhpbbTopic.topic_id == topicId)
            .first()
        )

    def get_post_ids(self, topicId) -> List[int]:
        query = (
            self.session.query(PhpbbPost)
            .join(PhpbbTopic, PhpbbTopic.topic_id == PhpbbPost.topic_id)
            .filter(PhpbbTopic.topic_id == topicId)
        )
        return [row.post_id for row in query.all()]

    def get_forum(self, id_) -> PhpbbForum:
        return self.session.query(PhpbbForum).filter(PhpbbForum.forum_id == id_).first()

    def get_post(self, postId) -> PhpbbPost:
        return self.session.query(PhpbbPost).filter(PhpbbPost.post_id == postId).first()

    def get_username(self, userId) -> str:
        n = self.session.query(PhpbbUser).filter(PhpbbUser.user_id == userId).first()
        return n.username or "Anonymous"


DB_WRAPPER = _DbWrapper()


class DbPost:
    _topic_ids_post_ids_map = {}

    def __init__(self, post_id):
        self.id = post_id

    @classmethod
    def get_post_ids_for_topic(cls, topicId) -> List[int]:
        try:
            ids = cls._topic_ids_post_ids_map[topicId]
        except KeyError:
            assert isinstance(topicId, int), (topicId, type(topicId))
            topic = DB_WRAPPER.get_topic(topicId)
            if not topic:
                log.error(f"{topicId} not found, use placeholder ...")
                topicId = SITE.PLACEHOLDER_TOPIC_ID
                topic = DB_WRAPPER.get_topic(topicId)
            if topic.forum_id != SITE.MAIN_CONTENT_FORUM_ID:
                if topic.forum_id not in SITE.ALLOWED_FORUM_IDS:
                    raise TopicNotAccessible(f"{topicId} in {topic.forum_id}")

            ids = DB_WRAPPER.get_post_ids(topicId)
            if not ids:
                raise TopicDoesNotExist(str(topicId))

            cls._topic_ids_post_ids_map[topicId] = ids
        return ids

    def __repr__(self):
        return f"<DbPost({self.id}, {self.subject})>"

    @cached_property
    def subject(self) -> str:
        return html.unescape(self.dbp.post_subject)

    @cached_property
    def content(self) -> str:
        """Some reassembly needed due to how phpbb stores the content"""
        content = self.dbp.post_text
        content = content.replace("<br/>", "\n")
        soup = BeautifulSoup(content, "html5lib")
        content = "".join(soup.findAll(text=True))
        return self._fix_whitespace(content)

    @cached_property
    def postTime(self) -> int:
        return self.dbp.post_edit_time or self.dbp.post_time

    @cached_property
    def author(self) -> str:
        author = self.dbp.post_username or DB_WRAPPER.get_username(self.dbp.poster_id)
        return html.unescape(author)

    @cached_property
    def isExcluded(self) -> bool:
        return self.md.isExcluded

    @cached_property
    def isVisible(self) -> bool:
        return self.dbp.post_visibility == 1

    @cached_property
    def md(self) -> PageMetadata:
        return PageMetadata(text=self.content)

    @cached_property
    def dbp(self) -> PhpbbPost:
        dbp = DB_WRAPPER.get_post(self.id)
        if not dbp:
            raise PostDoesNotExist(str(self.id))

        return dbp

    @classmethod
    def _fix_whitespace(cls, text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = []
        for line in text.split("\n"):
            lines.append("" if not line.strip() else line)
        text = "\n".join(lines)
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        return text

    def _attrs_for_cache(self, isFirstPost=True):
        d = self.md._make_dict(isFirstPost)
        for name, attr in sorted(self.__class__.__dict__.items()):
            if name.startswith("_"):
                continue

            if name in ["dbp", "content", "get_post_ids_for_topic", "md"]:
                continue

            if name.isupper():
                continue

            attr = getattr(self, name)

            d[name] = attr
        return d
