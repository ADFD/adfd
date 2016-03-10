import logging
import webbrowser

from plumbum import cli, LocalPath

from adfd import cst, conf
from adfd.content import TopicFinalizer, TopicNotFound, prepare, Finalizator
from adfd.db.export import ExportManager
from adfd.site_description import SITE_DESCRIPTION
from adfd.utils import get_obj_info

log = logging.getLogger(__name__)


def _export():
    conf.PATH.CNT_RAW.delete()
    log.debug('use db at %s', cst.DB_URL)
    ExportManager(siteDescription=SITE_DESCRIPTION).export()


def _prepare():
    conf.PATH.CNT_PREPARED.delete()
    prepare(conf.PATH.CNT_RAW, conf.PATH.CNT_PREPARED)


def _finalize():
    conf.PATH.CNT_FINAL.delete()
    Finalizator(SITE_DESCRIPTION).finalize()


class AdfdCnt(cli.Application):
    @cli.switch("l", int)
    def set_log_level(self, level):
        """Sets the log-level of the logger"""
        logging.root.setLevel(level)


@AdfdCnt.subcommand("export")
class AdfdDbExport(cli.Application):
    """export topics from db"""
    def main(self):
        _export()


@AdfdCnt.subcommand("prepare")
class AdfdCntPrepare(cli.Application):
    """prepare imported articles for final transformation"""
    def main(self):
        _prepare()


@AdfdCnt.subcommand("finalize")
class AdfdCntFinalize(cli.Application):
    """finalize prepared articles and create structure"""
    def main(self):
        _finalize()


@AdfdCnt.subcommand("do-all")
class AdfdCntFinalize(cli.Application):
    """export, prepare, finalize"""
    def main(self):
        _export()
        _prepare()
        _finalize()


@AdfdCnt.subcommand("conf")
class AdfdCntConf(cli.Application):
    def main(self):
        print(get_obj_info([cst, conf]))


@AdfdCnt.subcommand("article")
class AdfdCntArticle(cli.Application):
    output = cli.SwitchAttr(['o', 'output'], default='out')
    refresh = cli.Flag(["refresh"], default=True)

    def main(self, identifier):
        try:
            article = TopicFinalizer(int(identifier))
        except TopicNotFound as e:
            print(e)
            return 1

        print(article.md.asFileContents)
        if self.output == 'out':
            out = article.outContent
            self._open_html_in_webbrowser(out)
        elif self.output == 'in':
            print(article.inContent)

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
