import sys
import webbrowser

from plumbum import cli, LocalPath

from adfd.bbcode import AdfdParser


class Adfd(cli.Application):
    pass


# fixme remove db related stuff and work exclusively on generated content

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
            print("Forum with ID %s" % (forum.id))
            print("name: %s" % (forum.name))
        elif self.outType == 'summary':
            print("topic ids:", forum.topicIds)


@Adfd.subcommand("topic")
class ShowTopic(cli.Application):
    outType = cli.SwitchAttr(["out-type"], default='bbcode')

    def main(self, topicId):
        try:
            topic = Topic(topicId)
        except Topic:
            print("topic with id %s does not exist" % (topicId))
            return 1

        if self.outType == 'bbcode':
            print("Topic with ID %s" % (topic.id))
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
            print("Post with ID %s by %s" % (post.id, post.username))
            print("subject: %s" % (post.subject))
            print("slug: %s" % (post.slug))
            print(post.content)
        elif self.outType == 'html':
            html = AdfdParser().to_html(data=post.content)
            self._open_html_in_webbrowser(html)
        elif self.outType == 'summary':
            print(post)

    def _open_html_in_webbrowser(self, html):
        path = LocalPath("/tmp/adfd-html-out.html")
        html = ('<html><head><meta charset="utf-8"></head>'
                '<body>%s</body></html>' % (html))
        path.write(html, 'utf8')
        webbrowser.open("file://%s" % (path))


def main():
    Adfd.run()


if __name__ == '__main__':
    sys.exit(main())
