import sys
import webbrowser

from plumbum import cli, LocalPath

from adfd.bbcode import AdfdParser
from adfd.content import Article, ArticleNotFound


class AdfdCnt(cli.Application):
    pass


@AdfdCnt.subcommand("article")
class ShowTopic(cli.Application):
    outType = cli.SwitchAttr(["out-type"], default='raw')
    refresh = cli.Flag(["refresh"], default=True)

    def main(self, identifier):
        identifier = int(identifier) if identifier.isdigit() else identifier
        try:
            article = Article(identifier, refresh=self.refresh)
        except ArticleNotFound:
            print("Article '%s' does not exist" % (identifier))
            return 1

        print(article.md.asFileContents)
        if self.outType == 'raw':
            print(article.content)
        elif self.outType == 'html':
            html = AdfdParser().to_html(data=article.content)
            self._open_html_in_webbrowser(html)

    def _open_html_in_webbrowser(self, html):
        path = LocalPath("/tmp/adfd-html-out.html")
        html = ('<html><head><meta charset="utf-8"></head>'
                '<body>%s</body></html>' % (html))
        path.write(html, 'utf8')
        webbrowser.open("file://%s" % (path))


def main():
    AdfdCnt.run()


if __name__ == '__main__':
    sys.exit(main())
