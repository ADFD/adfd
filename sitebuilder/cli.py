import http.server
import logging
import socketserver

from plumbum import cli, LocalPath, local

from adfd.content import ContentWrangler
from adfd.db.sync import DbSynchronizer
from adfd.structure import Navigator
from sitebuilder.conf import APP, PATH, NAME, TARGET
from sitebuilder.fridge import freeze
from sitebuilder.lib import deploy
from sitebuilder.views import run_devserver

log = logging.getLogger(__name__)


class Sibu(cli.Application):
    """All functions for the ADFD website"""
    path = cli.SwitchAttr(['p', 'path'], default=PATH.PROJECT)

    def main(self):
        self.projectPath = LocalPath(self.path)
        if not self.nested_command:
            self.nested_command = (SibuDev, ['sibu dev'])


@Sibu.subcommand('remote-sync')
class SibuSync(cli.Application):
    """Fetch remote dump und load dump to local db"""
    def main(self):
        DbSynchronizer().sync()


@Sibu.subcommand('local-sync')
class SibuUpdate(cli.Application):
    """Update local content from local db contents"""
    def main(self):
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
        freeze(self.parent.projectPath, target.prefix)


@Sibu.subcommand('deploy')
class SibuDeploy(cli.Application):
    """Deploy frozen web page to remote location"""
    target = cli.SwitchAttr(
        ['t', 'target'], default='test', help="one of %s" % (TARGET.ALL))

    def main(self):
        outputPath = self.parent.projectPath / NAME.OUTPUT
        target = TARGET.get(self.target)
        freeze(self.parent.projectPath, target.prefix)
        deploy(outputPath, target)


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
        outputPath = self.parent.projectPath / NAME.OUTPUT
        log.info("serve '%s' at http://localhost:%s", outputPath, APP.PORT)
        self.serve(outputPath)

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
