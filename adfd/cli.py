import sys

from nikola.__main__ import main as nikola_main
from plumbum import cli

from adfd.db.export import Post, PostDoesNotExist, Topic


class Adfd(cli.Application):
    pass


@Adfd.subcommand("topic")
class ShowTopic(cli.Application):
    outType = cli.SwitchAttr(["out-type"], default='bbcode')

    def main(self, topicId):
        try:
            topic = Topic(topicId)
        except PostDoesNotExist:
            print("topic with id %s does not exist" % (topicId))
            return 1

        if self.outType == 'bbcode':
            print("Topic with ID %s" % (topic.topicId))
            print("subject: %s" % (topic.subject))
            print("slug: %s" % (topic.subject))
            print("\n".join([p.content for p in topic.posts]))
        elif self.outType == 'html':
            raise Exception('arg')


@Adfd.subcommand("post")
class ShowPost(cli.Application):
    outType = cli.SwitchAttr(["out-type"], default='bbcode')

    def main(self, postId):
        try:
            post = Post(postId)
        except PostDoesNotExist:
            print("post with id %s does not exist" % (postId))
            return 1

        if self.outType == 'bbcode':
            print("Post with ID %s by %s" % (post.postId, post.username))
            print("subject: %s" % (post.subject))
            print("slug: %s" % (post.slug))
            print(post.content)
        elif self.outType == 'html':
            raise Exception('arg')


@Adfd.subcommand("build")
class BuildSite(cli.Application):
    def main(self):
        nikola_main(['build'])


@Adfd.subcommand("deploy")
class DeploySite(cli.Application):
    def main(self):
        nikola_main(['deploy'])


def main():
    Adfd.run()


if __name__ == '__main__':
    sys.exit(main())
