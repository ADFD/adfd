# -*- coding: utf-8 -*-
import html
import logging

from bs4 import BeautifulSoup
from cached_property import cached_property
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker

from adfd.exc import PostDoesNotExist, TopicNotAccessible, TopicDoesNotExist
from adfd.metadata import PageMetadata
from adfd.db.schema import PhpbbTopic, PhpbbForum, PhpbbPost, PhpbbUser
from adfd.cnf import DB, SITE

log = logging.getLogger(__name__)

_DB_SESSION = None
"""":type: sqlalchemy.orm.session.Session"""


def get_db_session():
    global _DB_SESSION
    if _DB_SESSION:
        return _DB_SESSION

    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    session = sessionmaker()
    engine = create_engine(DB.URL, echo=False)
    session.configure(bind=engine)
    _DB_SESSION = session()
    return _DB_SESSION


class _DbWrapper:
    """very simple wrapper that can fetch the little that is needed"""
    @cached_property
    def session(self):
        return get_db_session()

    @property
    def q(self):
        return self.session.query

    def get_topics(self, forumId):
        """:rtype: list of int"""
        query = self.q(PhpbbTopic).filter(PhpbbTopic.forum_id == forumId)
        return [t for t in query]

    def get_topic(self, topicId):
        return self.q(PhpbbTopic).\
            filter(PhpbbTopic.topic_id == topicId).first()

    def get_posts(self, topicId):
        """:rtype: list of int"""
        query = self.q(PhpbbPost).join(
            PhpbbTopic, PhpbbTopic.topic_id == PhpbbPost.topic_id)\
            .filter(PhpbbTopic.topic_id == topicId)
        return [row.post_id for row in query.all()]

    def get_forum(self, id_):
        return self.q(PhpbbForum).filter(PhpbbForum.forum_id == id_).first()

    def get_post(self, postId):
        """:rtype: adfd.db.schema.PhpbbPost"""
        return self.q(PhpbbPost).filter(PhpbbPost.post_id == postId).first()

    def get_username(self, userId):
        """:rtype: str"""
        n = self.q(PhpbbUser).filter(PhpbbUser.user_id == userId).first()
        return n.username or "Anonymous"


DB_WRAPPER = _DbWrapper()


class DbPost:
    TOPIC_IDS_POST_IDS_MAP = {}

    @classmethod
    def get_post_ids_for_topic(cls, topicId):
        try:
            ids = cls.TOPIC_IDS_POST_IDS_MAP[topicId]
        except KeyError:
            assert isinstance(topicId, int), (topicId, type(topicId))
            t = DB_WRAPPER.get_topic(topicId)
            if not t:
                log.error("%s not found, use placeholder ...", topicId)
                topicId = SITE.PLACEHOLDER_TOPIC_ID
                t = DB_WRAPPER.get_topic(topicId)
            if t.forum_id != SITE.MAIN_CONTENT_FORUM_ID:
                if t.forum_id not in SITE.ALLOWED_FORUM_IDS:
                    raise TopicNotAccessible("%s in %s ", topicId, t.forum_id)

            ids = DB_WRAPPER.get_posts(topicId)
            if not ids:
                raise TopicDoesNotExist(str(topicId))

            cls.TOPIC_IDS_POST_IDS_MAP[topicId] = ids
        return ids

    def __init__(self, postId):
        self.id = postId

    def __repr__(self):
        return "<DbPost(%s, %s)>" % (self.id, self.subject)

    @cached_property
    def subject(self):
        return html.unescape(self.dbp.post_subject)

    @cached_property
    def content(self):
        """Some reassembly needed due to how phpbb stores the content"""
        content = self.dbp.post_text
        content = content.replace('<br/>', '\n')
        soup = BeautifulSoup(content, 'html5lib')
        content = ''.join(soup.findAll(text=True))
        return self._fix_whitespace(content)

    @cached_property
    def postTime(self):
        return self.dbp.post_edit_time or self.dbp.post_time

    @cached_property
    def author(self):
        author = (self.dbp.post_username or
                  DB_WRAPPER.get_username(self.dbp.poster_id))
        return html.unescape(author)

    @cached_property
    def isExcluded(self):
        return self.md.isExcluded

    @cached_property
    def isVisible(self):
        return self.dbp.post_visibility == 1

    @cached_property
    def md(self):
        return PageMetadata(text=self.content)

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
        dbp = DB_WRAPPER.get_post(self.id)
        if not dbp:
            raise PostDoesNotExist(str(self.id))

        return dbp


if __name__ == '__main__':
    def generate_schema(writeToFile="schema.py"):
        # if you are bored: use https://github.com/google/yapf to format file
        engine = create_engine(DB.URL)
        meta = MetaData()
        meta.reflect(bind=engine)
        imports = ("from sqlalchemy import Table\n"
                   "from db_reflection.schema import Base\n\n\n")
        defs = [imports]
        for table in meta.tables.values():
            defs.append("class %s(Base):\n    __table__ = "
                        "Table(%r, Base.metadata, autoload=True)\n\n\n" %
                        (table.name, table.name))
        declText = "".join(defs)
        if writeToFile:
            with open(writeToFile, "w") as f:
                f.write(declText)
        else:
            print(declText)


    generate_schema(writeToFile='')
