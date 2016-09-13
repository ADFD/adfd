import http.server
import logging
import socketserver

from plumbum import cli, local

from adfd.cnt.massage import GlobalFinalizer, TopicPreparator
from adfd.cst import PATH, APP, TARGET
from adfd.db.export import export_topics, harvest_topic_ids
from adfd.db.sync import DbSynchronizer
from adfd.site.fridge import freeze
from adfd.site.structure import Navigator
from adfd.site.views import run_devserver
from adfd.site_description import SITE_DESCRIPTION


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
        export_topics(harvest_topic_ids(SITE_DESCRIPTION))

    @staticmethod
    def prepare_topics():
        PATH.CNT_PREPARED.delete()
        for path in [p for p in PATH.CNT_RAW.list() if p.isdir()]:
            log.info('prepare %s', path)
            TopicPreparator(path, PATH.CNT_PREPARED).prepare()

    @staticmethod
    def finalize_articles():
        PATH.CNT_FINAL.delete()
        GlobalFinalizer.finalize(SITE_DESCRIPTION)


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
        freeze(target.prefix)


@Adfd.subcommand('deploy')
class AdfdDeploy(cli.Application):
    """Deploy frozen web page to remote location"""
    target = cli.SwitchAttr(
        ['t', 'target'], default='test', help="one of %s" % (TARGET.ALL))

    def main(self):
        target = TARGET.get(self.target)
        freeze(target.prefix)
        self.deploy(PATH.OUTPUT, target)

    @staticmethod
    def deploy(outputPath, target):
        """Synchronize static website contents with a remote target

        :type outputPath: LocalPath or str
        :type target: _Target
        """
        args = ('-av', str(outputPath) + '/', target.path)
        log.info('run rsync%s', args)
        rsyncOutput = local['rsync'](*args)
        log.info("rsync result:\n%s", rsyncOutput)


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
