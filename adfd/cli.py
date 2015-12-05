import logging
import webbrowser

from plumbum import cli, LocalPath

from adfd import cst, conf
from adfd.bbcode import AdfdParser
from adfd.conf import PATH
from adfd.content import TopicFinalizer, TopicNotFound, prepare, finalize
from adfd.db.export import export
from adfd.structure import Structure
from adfd.utils import get_obj_info


class AdfdCnt(cli.Application):
    @cli.switch("l", int)
    def set_log_level(self, level):
        """Sets the log-level of the logger"""
        logging.root.setLevel(level)


@AdfdCnt.subcommand("export")
class AdfdDbExport(cli.Application):
    """export topics from db"""
    def main(self):
        export(conf.EXPORT.FORUM_IDS, conf.EXPORT.TOPIC_IDS)


@AdfdCnt.subcommand("prepare")
class AdfdCntPrepare(cli.Application):
    """prepare imported articles for final transformation"""
    def main(self):
        PATH.CNT_PREPARED.delete()
        prepare(conf.PATH.CNT_RAW, PATH.CNT_PREPARED)


@AdfdCnt.subcommand("finalize")
class AdfdCntFinalize(cli.Application):
    """finalize prepared articles and create structure"""
    def main(self):
        PATH.CNT_FINAL.delete()
        finalize(conf.STRUCTURE)
        s = Structure(PATH.CNT_FINAL, PATH.STRUCTURE)
        s.dump_structure()


@AdfdCnt.subcommand("conf")
class AdfdCntConf(cli.Application):
    def main(self):
        print(get_obj_info([cst, conf]))


@AdfdCnt.subcommand("article")
class AdfdCntArticle(cli.Application):
    outType = cli.SwitchAttr(["out-type"], default='raw')
    refresh = cli.Flag(["refresh"], default=True)

    def main(self, identifier):
        try:
            article = TopicFinalizer(int(identifier))
        except TopicNotFound as e:
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
    logging.basicConfig(level=logging.WARNING)
    AdfdCnt.run()
