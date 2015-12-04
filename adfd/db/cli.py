import logging
import sys

from plumbum import cli

from adfd import conf, cst
from adfd.db.export import export
from adfd.db.phpbb_classes import *
from adfd.utils import get_obj_info


class AdfdDb(cli.Application):
    pass


@AdfdDb.subcommand("forum")
class AdfdDbForum(cli.Application):
    def main(self, forumId):
        try:
            forum = Forum(forumId)
        except ForumDoesNotExist:
            print("forum with id %s does not exist" % (forumId))
            return 1

        except ForumIsEmpty:
            print("forum with id %s is empty" % (forumId))
            return 1

        print("Forum %s: %s" % (forum.id, forum.name))
        print("topics:", forum.topicIds)


@AdfdDb.subcommand("topic")
class AdfdDbTopic(cli.Application):
    @cli.switch("-t", cli.Set("raw", "editable", case_sensitive=False))
    def contentType(self, contentType):
        self.contentType = contentType

    def main(self, topicId):
        try:
            topic = Topic(topicId)
        except TopicDoesNotExist:
            print("topic with id %s does not exist" % (topicId))
            return 1

        print("%s (%s)" % (topic.id, topic.subject))
        print("ids:", topic.postIds)
        if self.contentType == 'raw':
            print("\n\n --##--\n\n".join([p.rawText for p in topic.posts]))
        if self.contentType == 'editable':
            print("\n\n --##--\n\n".join([p.content for p in topic.posts]))


@AdfdDb.subcommand("post")
class AdfdDbPost(cli.Application):
    @cli.switch("-t", cli.Set("raw", "editable", case_sensitive=False))
    def contentType(self, contentType):
        self.contentType = contentType

    def main(self, postId):
        try:
            post = Post(postId)
        except PostDoesNotExist:
            print("post with id %s does not exist" % (postId))
            return 1

        print("%s by %s (%s)" % (post.subject, post.id, post.username))
        if self.contentType == 'raw':
            print(post.rawText)
        elif self.outType == 'html':
            print(post.content)


@AdfdDb.subcommand("status")
class AdfdDbStatus(cli.Application):
    def main(self):
        print(get_obj_info([cst, conf]))


def main():
    logging.basicConfig(level=logging.INFO)
    AdfdDb.run()


if __name__ == '__main__':
    sys.exit(main())
