# -*- coding: utf-8 -*-
import html
import logging
import re

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


class DbWrapper:
    """very simple wrapper that can fetch the little that is needed"""
    def __init__(self):
        self.session = get_db_session()
        self.query = self.session.query

    def forum_id_2_forum_name(self, forumId):
        """:rtype: list of int"""
        query = self.query(PhpbbForum).filter(PhpbbForum.forum_id == forumId)
        return query.first().forum_name

    def topic_id_2_db_posts(self, topicId):
        """:rtype: list of int"""
        query = self.query(PhpbbPost).join(
            PhpbbTopic, PhpbbTopic.topic_id == PhpbbPost.topic_id)\
                .filter(PhpbbTopic.topic_id == topicId)
        return [row.post_id for row in query.all()]

    def topic_id_2_forum_id(self, topicId):
        """:rtype: int"""
        return self.topic_from_topic_id(topicId).forum_id

    def topic_from_topic_id(self, topicId):
        return self.query(PhpbbTopic).filter(
            PhpbbTopic.topic_id == topicId).first()

    def fetch_post(self, postId):
        """:rtype: adfd.db.schema.PhpbbPost"""
        q = self.query(PhpbbPost).filter(PhpbbPost.post_id == postId)
        return q.first()

    def get_username(self, userId):
        """:rtype: str"""
        n = self.query(PhpbbUser).filter(PhpbbUser.user_id == userId).first()
        return n.username or "Anonymous"


class DbPost:
    @staticmethod
    def get_post_ids_for_topic(topicId):
        wrapper = DbWrapper()
        forumId = wrapper.topic_id_2_forum_id(topicId)
        if forumId not in SITE.ALLOWED_FORUM_IDS:
            if topicId not in SITE.ALLOWED_TOPIC_IDS:
                name = wrapper.forum_id_2_forum_name(forumId)
                raise TopicNotAccessible(
                    "%s in %s (%s)", topicId, name, forumId)

        ids = wrapper.topic_id_2_db_posts(topicId)
        if not ids:
            raise TopicDoesNotExist(str(topicId))

        return ids

    def __init__(self, postId):
        self.id = postId

    def __repr__(self):
        return "<DbPost(%s, %s)>" % (self.id, self.title)

    @cached_property
    def title(self):
        return self.md.title or html.unescape(self.dbp.post_subject)

    @cached_property
    def content(self):
        content = html.unescape(self.dbp.post_text)
        content = content.replace(':%s' % self.dbp.bbcode_uid, '')
        content = self._fix_db_storage_patterns(content)
        return self._fix_whitespace(content)

    @cached_property
    def postTime(self):
        return self.dbp.post_edit_time or self.dbp.post_time

    @cached_property
    def username(self):
        username = (self.dbp.post_username or
                    DbWrapper().get_username(self.dbp.poster_id))
        return html.unescape(username)

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


def get_db_config_info():
    msg = ""
    allowedForums = [
        "%s (%s)" % (DbWrapper().forum_id_2_forum_name(fId), fId)
        for fId in SITE.ALLOWED_FORUM_IDS]
    msg += "allowed Forums:\n    %s" % ("\n    ".join(allowedForums))
    return msg


if __name__ == '__main__':
    generate_schema(writeToFile='')
