# -*- coding: utf-8 -*-
import logging

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker

from adfd.db.schema import PhpbbTopic, PhpbbForum, PhpbbPost, PhpbbUser
from adfd.cnf import DB

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
        query = self.query(PhpbbTopic).filter(PhpbbTopic.topic_id == topicId)
        return query.first().forum_id

    def fetch_post(self, postId):
        """:rtype: adfd.db.schema.PhpbbPost"""
        q = self.query(PhpbbPost).filter(PhpbbPost.post_id == postId)
        return q.first()

    def get_username(self, userId):
        """:rtype: str"""
        n = self.query(PhpbbUser).filter(PhpbbUser.user_id == userId).first()
        return n.username or "Anonymous"


if __name__ == '__main__':
    generate_schema(writeToFile='')
