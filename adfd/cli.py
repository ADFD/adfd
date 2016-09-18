import http.server
import logging
import socketserver

from flask.ext.frozen import Freezer
from plumbum import cli, local

from adfd.cnt.massage import GlobalFinalizer, TopicPreparator
from adfd.cst import PATH, APP, TARGET
from adfd.db.export import export_topics, harvest_topic_ids
from adfd.db.sync import DbSynchronizer
from adfd.site.navigation import Navigator
from adfd.site.structure import get_structure
from adfd.site.views import app, navigator, run_devserver


log = logging.getLogger(__name__)


class ContentWrangler:
    """Thin wrapper with housekeeping to do the whole dance"""
    @classmethod
    def wrangle_content(cls):
        cls.export_topics_from_db()
        cls.prepare_topics()
        cls.finalize_articles()

    @staticmethod
    def export_topics_from_db():
        PATH.CNT_RAW.delete()
        export_topics(harvest_topic_ids(get_structure()))

    @staticmethod
    def prepare_topics():
        PATH.CNT_PREPARED.delete()
        for path in [p for p in PATH.CNT_RAW.list() if p.isdir()]:
            log.info('prepare %s', path)
            TopicPreparator(path, PATH.CNT_PREPARED).prepare()

    @staticmethod
    def finalize_articles():
        PATH.CNT_FINAL.delete()
        GlobalFinalizer.finalize(get_structure())


class Adfd(cli.Application):
    """All functions for the ADFD website"""
    def main(self):
        if not self.nested_command:
            self.nested_command = (AdfdDev, ['adfd dev'])


@Adfd.subcommand('sync-remote')
class AdfdSyncRemote(cli.Application):
    """Fetch remote dump und load dump to local db"""
    def main(self):
        DbSynchronizer().sync()


@Adfd.subcommand('sync-local')
class AdfdSyncLocal(cli.Application):
    """Update local content from local db contents"""
    def main(self):
        ContentWrangler.wrangle_content()


@Adfd.subcommand('sync')
class AdfdSync(cli.Application):
    """sync all. remote DB -> local DB -> generate content"""
    def main(self):
        DbSynchronizer().sync()
        ContentWrangler.wrangle_content()


@Adfd.subcommand('dev')
class AdfdDev(cli.Application):
    """Run local development server"""
    def main(self):
        run_devserver()


@Adfd.subcommand('freeze')
class AdfdBuild(cli.Application):
    """Freeze website to static files"""
    target = cli.SwitchAttr(
        ['t', 'target'], default='test', help="one of %s" % (TARGET.ALL))

    def main(self):
        target = TARGET.get(self.target)
        self.freeze(target.prefix)

    @staticmethod
    def freeze(pathPrefix=None):
        """:param pathPrefix: for freezing when it's served not from root"""

        def page():
            for url in navigator.allUrls:
                yield {'path': url}

        log.info("freeze in: %s", PATH.PROJECT)
        freezer = Freezer(app)
        freezer.register_generator(page)

        with local.cwd(PATH.PROJECT):
            log.info("freezing %s", freezer)
            seenUrls = freezer.freeze()
            log.info("frozen urls are:\n%s", '\n'.join(seenUrls))
        if pathPrefix:
            for url in seenUrls:
                if url.endswith('/'):
                    filePath = PATH.OUTPUT / url[1:] / 'index.html'
                    with open(filePath) as f:
                        content = f.read()
                        content = content.replace(
                            'href="/', 'href="/%s/' % (pathPrefix))
                    with open(filePath, 'w') as f:
                        f.write(content)


@Adfd.subcommand('deploy')
class AdfdDeploy(cli.Application):
    """Deploy frozen web page to remote location"""
    target = cli.SwitchAttr(
        ['t', 'target'], default='test', help="one of %s" % (TARGET.ALL))

    def main(self):
        self.deploy(PATH.OUTPUT, TARGET.get(self.target))


@Adfd.subcommand('outline')
class AdfdOutline(cli.Application):
    """Generate web page outline in bbcode to post in forum"""
    def main(self):
        outline = Navigator().outline
        print(outline, end='\n\n')


@Adfd.subcommand('serve-frozen')
class AdfdServeFrozen(cli.Application):
    """Serve frozen web page locally"""
    def main(self):
        log.info("serve '%s' at http://localhost:%s", PATH.OUTPUT, APP.PORT)
        self.serve(PATH.OUTPUT)

    @staticmethod
    def serve(siteRoot):
        with local.cwd(siteRoot):
            Handler = http.server.SimpleHTTPRequestHandler
            httpd = socketserver.TCPServer(("", APP.PORT), Handler)
            try:
                httpd.serve_forever()
            finally:
                httpd.server_close()


def main():
    logging.basicConfig(level=logging.INFO)
    try:
        Adfd.run()
    except KeyboardInterrupt:
        log.info('stopped by user')
