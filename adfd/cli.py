import http.server
import logging
import os
import socketserver

from plumbum import cli, local, LocalPath

from adfd.cnf import PATH, SITE, APP
from adfd.db.lib import get_db_config_info
from adfd.db.sync import DbSynchronizer
from adfd.site.controller import app, navigator, run_devserver
from flask.ext.frozen import Freezer

log = logging.getLogger(__name__)


class Adfd(cli.Application):
    """All functions for the ADFD website"""
    def main(self):
        if not self.nested_command:
            self.nested_command = (AdfdDev, ['adfd dev'])


@Adfd.subcommand('sync')
class AdfdSyncRemote(cli.Application):
    """Fetch remote dump und load dump to local db"""
    def main(self):
        DbSynchronizer().sync()


@Adfd.subcommand('update-local')
class AdfdSyncRemote(cli.Application):
    def main(self):
        DbSynchronizer().update_local_db()


@Adfd.subcommand('dev')
class AdfdDev(cli.Application):
    """Run local development server"""
    def main(self):
        run_devserver()


@Adfd.subcommand('freeze')
class AdfdFreeze(cli.Application):
    """Freeze website to static files"""
    TM = {
        'dev': (PATH.PROJECT / '.frozen', None),
        'test': (LocalPath('/home/www/privat/neu'),  'privat/neu'),
        'live': (None, None),
    }
    target = cli.SwitchAttr(
        ['t', 'target'], default='test', help="one of %s" % TM.keys())

    def main(self):
        if self.target == 'live':
            raise Exception("not ready for live!")

        self.freeze(self.target, *self.TM[self.target])

    @staticmethod
    def freeze(target, dstPath, pathPrefix):
        def path_route():
            for _url, node in navigator.pathNodeMap.items():
                if not node.hasContent:
                    log.info("nothing to render for %s -> %r", _url, node)
                    continue

                log.info("yield %s", _url)
                yield {'path': _url}

        log.info("freeze to: %s", dstPath)
        os.environ[APP.ENV_TARGET] = target
        app.config.update(FREEZER_DESTINATION=str(dstPath),
                          FREEZER_RELATIVE_URLS=True,
                          FREEZER_REMOVE_EXTRA_FILES=True)
        freezer = Freezer(app)
        freezer.register_generator(path_route)
        with local.cwd(PATH.PROJECT):
            log.info("freezing %s", freezer)
            seenUrls = freezer.freeze()
            log.info("frozen urls are:\n%s", '\n'.join(seenUrls))
        if pathPrefix:
            log.warning("prefix %s - changing links", pathPrefix)
            for url in seenUrls:
                if url.endswith('/'):
                    filePath = dstPath / url[1:] / 'index.html'
                    with open(filePath) as f:
                        content = f.read()
                        content = content.replace(
                            'href="/', 'href="/%s/' % pathPrefix)
                    with open(filePath, 'w') as f:
                        f.write(content)


@Adfd.subcommand('frozen')
class AdfdServeFrozen(cli.Application):
    """Serve frozen web page locally"""
    def main(self):
        dstPath = AdfdFreeze.TM['dev'][0]
        log.info("'%s' -> http://localhost:%s", dstPath, SITE.APP_PORT)
        self.serve(dstPath)

    @staticmethod
    def serve(siteRoot):
        with local.cwd(siteRoot):
            Handler = http.server.SimpleHTTPRequestHandler
            httpd = socketserver.TCPServer(("", SITE.APP_PORT), Handler)
            try:
                httpd.serve_forever()
            finally:
                httpd.server_close()


@Adfd.subcommand('info')
class AdfdInfo(cli.Application):
    def main(self):
        print(get_db_config_info)


def main():
    try:
        Adfd.run()
    except KeyboardInterrupt:
        log.info('stopped by user')
