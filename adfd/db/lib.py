# -*- coding: utf-8 -*-
import logging

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker

from adfd.db.phpbb_schema import PhpbbTopic, PhpbbForum, PhpbbPost, PhpbbUser

log = logging.getLogger(__name__)

try:
    from adfd.secrets import DB
    URL = DB.URL
except ImportError:
    URL = 'mysql://user:pw@localhost/dbname'
    log.error("secrets not found - using generic db url: %s", URL)


def generate_schema(writeToFile="schema.py"):
    # if you are bored: use https://github.com/google/yapf to format file
    engine = create_engine(URL)
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
    """":rtype: sqlalchemy.orm.session.Session"""
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    Session = sessionmaker()
    engine = create_engine(URL, echo=False)
    Session.configure(bind=engine)
    return Session()


class DbWrapper:
    """very simple wrapper that can fetch the little that's needed atm"""
    DB_SESSION = get_db_session()

    def __init__(self):
        self.query = self.DB_SESSION.query

    def fetch_topic_ids_from_forum(self, forumId):
        """:rtype: list of int"""
        query = self.query(PhpbbTopic).join(
            PhpbbForum, PhpbbForum.forum_id == PhpbbTopic.forum_id)\
            .filter(PhpbbTopic.forum_id == forumId)
        return [row.topic_id for row in query.all()]

    def fetch_post_ids_from_topic(self, topicId):
        """:rtype: list of int"""
        query = self.query(PhpbbPost).join(
            PhpbbTopic, PhpbbTopic.topic_id == PhpbbPost.topic_id)\
            .filter(PhpbbTopic.topic_id == topicId)
        return [row.post_id for row in query.all()]

    def fetch_forum(self, forumId):
        """:rtype: adfd.db.phpbb_schema.PhpbbForum"""
        q = self.query(PhpbbForum).filter(PhpbbForum.forum_id == forumId)
        return q.first()

    def fetch_post(self, postId):
        """:rtype: adfd.db.phpbb_schema.PhpbbPost"""
        q = self.query(PhpbbPost).filter(PhpbbPost.post_id == postId)
        return q.first()

    def get_username(self, userId):
        """:rtype: str"""
        n = self.query(PhpbbUser).filter(PhpbbUser.user_id == userId).first()
        return n.username or "Anonymous"


if __name__ == '__main__':
    generate_schema(writeToFile='')
