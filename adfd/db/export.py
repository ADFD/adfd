# coding=utf-8
import html
import logging
import re
import subprocess
from datetime import datetime

from cached_property import cached_property

from adfd import cst
from adfd.db.schema import PhpbbPost, PhpbbForum, PhpbbTopic, PhpbbUser
from adfd.db.utils import DB_SESSION
from adfd.utils import slugify


log = logging.getLogger(__name__)


class Forum(object):
    def __init__(self, forumId):
        self.id = forumId
        self.db = DbWrapper()
        self.dbObject = self.db.fetch_forum(self.id)
        if not self.dbObject:
            raise ForumDoesNotExist(str(self.id))

        self.topicIds = self.db.fetch_topic_ids_from_forum(self.id)
        if not self.topicIds:
            raise ForumIsEmpty(str(self.id))

        self.name = self.dbObject.forum_name

    @property
    def topics(self):
        for topicId in self.topicIds:
            try:
                yield Topic(topicId)

            except TopicIsEmpty:
                log.warning("topic %s is broken", topicId)
                continue


class ForumDoesNotExist(Exception):
    """raised if the forum contains no topics"""


class ForumIsEmpty(Exception):
    """raised if the forum contains no topics"""


class Topic(object):
    """This has a bit of flexibility to make it possible to filter posts."""
    def __init__(self, topicId=None, postIds=None, excludedPostIds=None):
        assert topicId or postIds, 'need either topic or post id'
        assert not (topicId and postIds), 'need only one'
        self.id = topicId
        self.db = DbWrapper()
        self.postIds = self.get_ids(self.id, postIds, excludedPostIds or [])
        if self.postIds:
            self.subject = self.get_subject(self.postIds[0])

    @cached_property
    def posts(self):
        """:rtype: list of Post"""
        return [Post(postId) for postId in self.postIds]

    def get_ids(self, topicId, postIds, excludedPostIds):
        if topicId:
            ids = self.db.fetch_post_ids_from_topic(topicId)
            return [i for i in ids if i not in excludedPostIds]

        if not isinstance(postIds, list):
            assert isinstance(postIds, int), postIds
            log.warning('no sanity check for arbitrarily set postIds')
            return [postIds]

        if not postIds:
            raise TopicIsEmpty(str(topicId))

    def get_subject(self, wantedPostId):
        # first **wanted** post does not have to be the actual first post
        # If this is the case the topic information is set from first wanted
        return Post(wantedPostId).subject


class TopicIsEmpty(Exception):
    """raised if the topic contains no posts"""


class Post(object):
    def __init__(self, postId):
        self.id = postId
        self.db = DbWrapper()
        self.dbp = self.db.fetch_post(self.id)
        if not self.dbp:
            raise PostDoesNotExist(str(self.id))

        self.topicId = self.dbp.topic_id
        self.rawText = self.dbp.post_text

    def __repr__(self):
        return ("<%s %s (%s)>" %
                (self.__class__.__name__, self.id, self.uniqueSlug))

    @cached_property
    def metadata(self):
        return "%s\n\n" % '\n'.join([
            '.. author: %s' % (self.username),
            '.. lastUpdate: %s' % (self.lastUpdate),
            '.. postDate: %s' % (self.format_date(int(self.dbp.post_time))),
            '.. postId: %s' % (self.id),
            '.. slug: %s' % (self.uniqueSlug),
            '.. title: %s' % (self.subject),
            '.. topicId: %s' % (self.topicId),
            '.. authorId: %s' % (self.dbp.poster_id)])

    @cached_property
    def content(self):
        """This should be exactly the editable source of the post"""
        return self.sanitize(self.preprocessedText)

    @cached_property
    def filename(self):
        filename = '%06d' % (self.id)
        if self.slug:
            filename += '-%s' % (self.slug)
        return filename

    @cached_property
    def uniqueSlug(self):
        isReSlug = self.slug.startswith('re-')
        if not self.slug or isReSlug:
            slug = str(self.id)
            subslug = slugify(self.subject)
            if not subslug or isReSlug:
                return slug

            return "%s-%s" % (slug, subslug)

        return self.slug

    @cached_property
    def slug(self):
        return slugify(self.subject)

    @cached_property
    def subject(self):
        return self.preprocess(self.dbp.post_subject)

    @cached_property
    def username(self):
        username = (self.dbp.post_username or
                    self.db.get_username(self.dbp.poster_id))
        return self.preprocess(username)

    @cached_property
    def lastUpdate(self):
        lastUpdate = (self.dbp.post_edit_time or self.dbp.post_time)
        return self.format_date(lastUpdate)

    @cached_property
    def preprocessedText(self):
        return self.preprocess(self.rawText, self.dbp.bbcode_uid)

    @staticmethod
    def preprocess(text, bbcodeUid=None):
        if bbcodeUid:
            text = text.replace(':%s' % (bbcodeUid), '')
        text = html.unescape(text)
        return text

    @staticmethod
    def format_date(timestamp):
        return datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y')

    @classmethod
    def sanitize(cls, text):
        text = cls.fix_db_storage_patterns(text)
        return cls.fix_whitespace(text)

    @classmethod
    def fix_db_storage_patterns(cls, text):
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
    def fix_whitespace(cls, text):
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        lines = []
        for line in text.split('\n'):
            lines.append('' if not line.strip() else line)
        text = "\n".join(lines)
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        return text


class PostDoesNotExist(Exception):
    """raised if a post with the given ID does not exist"""


class DbWrapper(object):
    def __init__(self):
        self.query = DB_SESSION.query

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
        """:rtype: adfd.db.schema.PhpbbForum"""
        q = self.query(PhpbbForum).filter(PhpbbForum.forum_id == forumId)
        return q.first()

    def fetch_post(self, postId):
        """:rtype: adfd.db.schema.PhpbbPost"""
        q = self.query(PhpbbPost).filter(PhpbbPost.post_id == postId)
        return q.first()

    def get_username(self, userId):
        """:rtype: str"""
        n = self.query(PhpbbUser).filter(PhpbbUser.user_id == userId).first()
        return n.username or "Anonymous"


class TopicsExporter(object):
    CONTENT_PATH = cst.PATH.CONTENT
    """root of all content for the website"""
    RAW_EXPORT_PATH = CONTENT_PATH / cst.DIR.RAW
    """exported bbcode like it looks when edited

    It is not raw in the sense that it has the same format like stored in DB
    as this is quite different from what one sees in the editor, but from
    an editors perspective that does not matter, so this is considered raw
    """

    SUMMARY_PATH = CONTENT_PATH / 'summary.txt'
    """keep a list of topics and their imported posts as text"""

    def __init__(self, topics, useGit=False):
        self.topics = topics
        """:type: list of Topic"""
        self.allPaths = [self.SUMMARY_PATH]
        """contains a list of all imperted paths at end of import

        used to keep track of what whould be removed between imports
        """
        self.useGit = useGit

    def export_topics(self):
        self.update_directory()
        if self.useGit:
            self.prune_orphans()
            self.add_files()

    def update_directory(self):
        out = []
        for topic in self.topics:
            try:
                out.extend(self._export_topic(topic))
            except AttributeError:
                log.warning('topic %s broken', topic.id)
        log.info('%s files, %s topics', len(self.allPaths), len(self.topics))
        self.write(self.SUMMARY_PATH, "\n".join(out))

    def _export_topic(self, topic):
        out = ["%s: %s" % (topic.id, topic.subject)]
        topicPath = self.RAW_EXPORT_PATH / ("%05d" % (topic.id))
        log.info('%s -> %s', topic.id, topicPath)
        for post in topic.posts:
            current = "%s" % (post.uniqueSlug)
            log.debug("export: %s", current)
            out.append("    " + current)
            patt = "%s.%%s" % (post.filename)
            postMetadataPath = topicPath / (patt % ('meta'))
            postContentPath = topicPath / (patt % ('bb'))
            self.allPaths.extend([postMetadataPath, postContentPath])
            self.write(postMetadataPath, post.metadata)
            self.write(postContentPath, post.content)
        return out

    def add_files(self):
        cmd = ['git', 'add', '--all', '.']
        try:
            subprocess.check_output(cmd, cwd=str(self.RAW_EXPORT_PATH))
        except subprocess.CalledProcessError:
            pass

    def prune_orphans(self):
        for p in self.RAW_EXPORT_PATH.walk():
            if not p.isdir() and not any(ap == p for ap in self.allPaths):
                log.warning("removing %s", p)
                cmd = ['git', 'rm', '-f', str(p)]
                try:
                    subprocess.check_output(cmd, cwd=str(self.RAW_EXPORT_PATH))
                except subprocess.CalledProcessError:
                    p.delete()

    def write(self, path, content):
        log.debug('%s', path)
        path.dirname.mkdir()
        path.write(content.encode('utf8'))
