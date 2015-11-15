import sys
import webbrowser

from nikola.__main__ import main as nikola_main
from plumbum import cli

from adfd.db.export import (
    Post, PostDoesNotExist, Topic, Forum, ForumIsEmpty, ForumDoesNotExist)


class Adfd(cli.Application):
    pass


def show(htmlText):
    path = "/tmp/adfd-html-out.html"
    with open(path, 'w') as f:
        f.write(htmlText)
    webbrowser.open("file://%s" % (path))


@Adfd.subcommand("forum")
class ShowForum(cli.Application):
    outType = cli.SwitchAttr(["out-type"], default='bbcode')

    def main(self, forumId):
        try:
            forum = Forum(forumId)
        except ForumDoesNotExist:
            print("forum with id %s does not exist" % (forumId))
            return 1

        except ForumIsEmpty:
            print("forum with id %s is empty" % (forumId))
            return 1

        if self.outType == 'bbcode':
            print("Forum with ID %s" % (forum.forumId))
            print("name: %s" % (forum.name))
        elif self.outType == 'summary':
            print("topic ids:", forum.topicIds)


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
        elif self.outType == 'summary':
            print("post ids:", topic.postIds)


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
        elif self.outType == 'summary':
            print(post)


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
