# -*- coding: utf-8 -*-
import logging

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker

from adfd import cst
from adfd.conf import PATH
from adfd.cst import EXT
from adfd.db.phpbb_classes import Topic, TopicDoesNotExist
from adfd.db.phpbb_schema import PhpbbTopic, PhpbbForum, PhpbbPost, PhpbbUser
from adfd.utils import id2name, dump_contents


log = logging.getLogger(__name__)


class RawTopicsExporter:
    """Read all given topics from DB into raw file"""

    def __init__(self, topicIds=None, siteDescription=None):
        self.allTopicIds = set(topicIds or [])
        if siteDescription:
            self._harvest_topics_recursive(siteDescription)

        self.topics = []
        """:type: list of Topic"""
        for topicId in self.allTopicIds:
            try:
                self.topics.append(Topic(topicId))
            except TopicDoesNotExist:
                log.warning('topic %s is broken', topicId)

    def export(self):
        for topic in self.topics:
            self._export_topic(topic)

    def _harvest_topics_recursive(self, content):
        self.allTopicIds.add(content.mainTopicId)
        for content in content.contents:
            if isinstance(content, int):
                self.allTopicIds.add(content)
            else:
                self._harvest_topics_recursive(content)

    def _export_topic(self, topic):
        topicPath = PATH.CNT_RAW / id2name(topic.id)
        log.info('%s -> %s', topic.id, topicPath)
        for post in topic.posts:
            current = "%s" % (post.subject)
            log.debug("export: %s", current)
            contentPath = topicPath / (post.filename + EXT.IN)
            dump_contents(contentPath, post.content)
            metadataPath = topicPath / (post.filename + EXT.META)
            dump_contents(metadataPath, post.md.asFileContents)


def generate_schema(writeToFile="schema.py"):
    # if you are bored: use https://github.com/google/yapf to format file
    engine = create_engine(cst.DB_URL)
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
    engine = create_engine(cst.DB_URL, echo=False)
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
