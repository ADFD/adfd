import logging
import webbrowser

from plumbum import cli, LocalPath

from adfd import cst, conf
from adfd.content import TopicFinalizer, ContentWrangler
from adfd.exc import TopicNotFound
from adfd.utils import get_obj_info

log = logging.getLogger(__name__)


class AdfdCnt(cli.Application):
    @cli.switch("l", int)
    def set_log_level(self, level):
        """Sets the log-level of the logger"""
        logging.root.setLevel(level)


@AdfdCnt.subcommand("export")
class AdfdDbExport(cli.Application):
    """export topics from db"""
    def main(self):
        ContentWrangler.export_topics_from_db()


@AdfdCnt.subcommand("prepare")
class AdfdCntPrepare(cli.Application):
    """prepare imported articles for final transformation"""
    def main(self):
        ContentWrangler.prepare_topics()


@AdfdCnt.subcommand("finalize")
class AdfdCntFinalize(cli.Application):
    """finalize prepared articles and create structure"""
    def main(self):
        ContentWrangler.finalize_articles()


@AdfdCnt.subcommand("do-all")
class AdfdCntFinalize(cli.Application):
    """export, prepare, finalize"""
    def main(self):
        ContentWrangler.wrangle()


@AdfdCnt.subcommand("conf")
class AdfdCntConf(cli.Application):
    def main(self):
        print(get_obj_info([cst, conf]))


@AdfdCnt.subcommand("article")
class AdfdCntArticle(cli.Application):
    browse = cli.Flag(
        ['b', 'browse'], help="if given: open output in webbrowser")

    def main(self, identifier):
        try:
            article = TopicFinalizer(int(identifier))
        except TopicNotFound as e:
            log.error(e)
            return 1

        print("Article <%s>\n%s" % (identifier, article.md.asFileContents))
        print("#" * 120)
        print(article.inContent)
        print("#" * 120)
        print(article.outContent)
        print("#" * 120)
        if self.browse:
            self._open_html_in_webbrowser(article.outContent)

    def _open_html_in_webbrowser(self, html):
        path = LocalPath("/tmp/adfd-html-out.html")
        html = ('<html><head><meta charset="utf-8"></head>'
                '<body>%s</body></html>' % (html))
        path.write(html, 'utf8')
        webbrowser.open("file://%s" % (path))


def main():
    fmt = '%(module)s.%(funcName)s:%(lineno)d %(levelname)s: %(message)s'
    logging.basicConfig(level=logging.INFO, format=fmt)
    AdfdCnt.run()
