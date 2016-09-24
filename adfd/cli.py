import http.server
import logging
import os
import socketserver

from adfd.cnf import PATH, APP
from adfd.db.sync import DbSynchronizer
from adfd.secrets import DB
from adfd.site.views import app, navigator, run_devserver
from flask.ext.frozen import Freezer
from plumbum import cli, local

log = logging.getLogger(__name__)

TEST = ('%s:./www/privat/neu' % DB.REMOTE_HOST, 'privat/neu')
LIVE = ('%s:./www/inhalt' % DB.REMOTE_HOST, 'inhalt')
TARGET_MAP = {'local': (None, None), 'test': TEST, 'live': LIVE}


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


@Adfd.subcommand('dev')
class AdfdDev(cli.Application):
    """Run local development server"""
    def main(self):
        run_devserver()


@Adfd.subcommand('freeze')
class AdfdBuild(cli.Application):
    """Freeze website to static files"""
    target = cli.SwitchAttr(
        ['t', 'target'], default='local', help="one of %s" % TARGET_MAP.keys())

    def main(self):
        self.freeze(TARGET_MAP[self.target][1], self.target == 'live')

    @staticmethod
    def freeze(pathPrefix, isLive):
        """:param pathPrefix: for freezing when it's served not from root"""

        def page():
            for url in navigator.allUrls:
                yield {'path': url}

        log.info("freeze in: %s", PATH.PROJECT)
        os.environ['IS_LIVE'] = isLive
        freezer = Freezer(app)
        freezer.register_generator(page)
        with local.cwd(PATH.PROJECT):
            log.info("freezing %s", freezer)
            seenUrls = freezer.freeze()
            log.info("frozen urls are:\n%s", '\n'.join(seenUrls))
        if pathPrefix:
            log.warning("prefix %s - changing links", pathPrefix)
            for url in seenUrls:
                if url.endswith('/'):
                    filePath = PATH.FROZEN / url[1:] / 'index.html'
                    with open(filePath) as f:
                        content = f.read()
                        content = content.replace(
                            'href="/', 'href="/%s/' % pathPrefix)
                    with open(filePath, 'w') as f:
                        f.write(content)


@Adfd.subcommand('deploy')
class AdfdDeploy(cli.Application):
    """Deploy frozen web page to remote location"""
    target = cli.SwitchAttr(
        ['t', 'target'], default='test', help="one of %s" % TARGET_MAP.keys())

    def main(self):
        if self.target == 'local':
            raise Exception("no local deploy possible")
        self.deploy(PATH.FROZEN, TARGET_MAP[self.target][1])


@Adfd.subcommand('frozen')
class AdfdServeFrozen(cli.Application):
    """Serve frozen web page locally"""
    def main(self):
        log.info("serve '%s' at http://localhost:%s", PATH.FROZEN, APP.PORT)
        self.serve(PATH.FROZEN)

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
