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


def get_main_content_topic_ids():
    return DbWrapper().get_topic_ids(SITE.MAIN_CONTENT_FORUM_ID)


class DbWrapper:
    """very simple wrapper that can fetch the little that is needed"""
    def __init__(self):
        self.session = get_db_session()
        self.q = self.session.query

    def get_forum_name(self, forumId):
        """:rtype: list of int"""
        return self.get_forum(forumId).forum_name

    def get_forum_id(self, topicId):
        """:rtype: int"""
        return self.get_topic(topicId).forum_id

    def get_topic_ids(self, forumId):
        """:rtype: list of int"""
        query = self.q(PhpbbTopic).filter(PhpbbTopic.forum_id == forumId)
        return [r.topic_id for r in query.all()]

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


class DbPost:
    WRAPPER = None
    TOPIC_IDS_POST_IDS_MAP = {}

    @classmethod
    def get_post_ids_for_topic(cls, topicId):
        try:
            ids = cls.TOPIC_IDS_POST_IDS_MAP[topicId]
        except KeyError:
            if not cls.WRAPPER:
                cls.WRAPPER = DbWrapper()
            forumId = cls.WRAPPER.get_forum_id(topicId)
            if forumId != SITE.MAIN_CONTENT_FORUM_ID:
                log.warning("Topic not imported yet: %s", topicId)
                if forumId not in SITE.ALLOWED_FORUM_IDS:
                    name = cls.WRAPPER.get_forum_name(forumId)
                    raise TopicNotAccessible(
                        "%s in %s (%s)", topicId, name, forumId)

            ids = cls.WRAPPER.get_posts(topicId)
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
            ('<!-- e -->.*?href="(.*?)".*?<!-- e -->', '[url=\g<1>]\g<1>[/url]'),
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
        dbp = DbWrapper().get_post(self.id)
        if not dbp:
            raise PostDoesNotExist(str(self.id))

        return dbp


def get_db_config_info():
    msg = ""
    allowedForums = [
        "%s (%s)" % (DbWrapper().get_forum_name(fId), fId)
        for fId in SITE.ALLOWED_FORUM_IDS]
    msg += "allowed Forums:\n    %s" % ("\n    ".join(allowedForums))
    return msg


if __name__ == '__main__':
    generate_schema(writeToFile='')
