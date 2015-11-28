import logging
import webbrowser

from plumbum import cli, LocalPath

from adfd.bbcode import AdfdParser
from adfd.content import Article, TopicNotImported, prepare_all
from adfd.cst import PATH


class AdfdCnt(cli.Application):
    pass


@AdfdCnt.subcommand("prepare")
class AdfdCntPrepare(cli.Application):
    """prepare imported articles for final transformation"""
    def main(self):
        prepare_all(PATH.CNT_RAW)


@AdfdCnt.subcommand("article")
class AdfdCntArticle(cli.Application):
    outType = cli.SwitchAttr(["out-type"], default='raw')
    refresh = cli.Flag(["refresh"], default=True)

    def main(self, identifier):
        try:
            article = Article(int(identifier))
        except TopicNotImported as e:
            print(e)
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
    logging.basicConfig(level=logging.INFO)
    AdfdCnt.run()
