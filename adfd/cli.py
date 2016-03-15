import http.server
import logging
import socketserver

from plumbum import cli, local

from adfd.cst import PATH, APP, TARGET
from adfd.content import ContentWrangler
from adfd.db.sync import DbSynchronizer
from adfd.structure import Navigator
from adfd.sitebuilder.fridge import freeze
from adfd.sitebuilder.lib import deploy
from adfd.sitebuilder.views import run_devserver


log = logging.getLogger(__name__)


class Sibu(cli.Application):
    """All functions for the ADFD website"""
    def main(self):
        if not self.nested_command:
            self.nested_command = (SibuDev, ['sibu dev'])


@Sibu.subcommand('sync-remote')
class SibuSyncRemote(cli.Application):
    """Fetch remote dump und load dump to local db"""
    def main(self):
        DbSynchronizer().sync()


@Sibu.subcommand('sync-local')
class SibuSyncLocal(cli.Application):
    """Update local content from local db contents"""
    def main(self):
        ContentWrangler.wrangle_content()


@Sibu.subcommand('sync')
class SibuSync(cli.Application):
    """sync all. remote DB -> local DB -> generate content"""
    def main(self):
        DbSynchronizer().sync()
        ContentWrangler.wrangle_content()


@Sibu.subcommand('dev')
class SibuDev(cli.Application):
    """Run local development server"""
    def main(self):
        run_devserver()


@Sibu.subcommand('freeze')
class SibuBuild(cli.Application):
    """Freeze website to static files"""
    target = cli.SwitchAttr(
        ['t', 'target'], default='test', help="one of %s" % (TARGET.ALL))

    def main(self):
        target = TARGET.get(self.target)
        freeze(target.prefix)


@Sibu.subcommand('deploy')
class SibuDeploy(cli.Application):
    """Deploy frozen web page to remote location"""
    target = cli.SwitchAttr(
        ['t', 'target'], default='test', help="one of %s" % (TARGET.ALL))

    def main(self):
        target = TARGET.get(self.target)
        freeze(target.prefix)
        deploy(PATH.OUTPUT, target)


@Sibu.subcommand('outline')
class SibuOutline(cli.Application):
    """Generate web page outline in bbcode to post in forum"""
    def main(self):
        outline = Navigator().outline
        print(outline, end='\n\n')


@Sibu.subcommand('serve-frozen')
class SibuServeFrozen(cli.Application):
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
        Sibu.run()
    except KeyboardInterrupt:
        log.info('stopped by user')
