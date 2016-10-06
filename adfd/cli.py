import http.server
import logging
import os
import socketserver
import tempfile

import shutil
from flask.ext.frozen import Freezer
from plumbum import ProcessExecutionError
from plumbum import cli, local, LocalPath

from adfd.cnf import PATH, SITE, APP
from adfd.db.lib import get_db_config_info
from adfd.db.sync import DbSynchronizer
from adfd.site import fridge
from adfd.site.controller import app, run_devserver
from adfd.utils import configure_logging

log = logging.getLogger(__name__)


class Adfd(cli.Application):
    """All functions for the ADFD website"""
    logLevel = cli.SwitchAttr(
        ['l', 'log-level'], default='WARNING', help="set log level")

    def main(self):
        configure_logging(self.logLevel)
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
        'dev': (PATH.RENDERED, None),
        'test': (LocalPath('/home/www/privat/neu'),  'privat/neu'),
        'live': (None, None),
    }
    target = cli.SwitchAttr(
        ['t', 'target'], default='dev', help="one of %s" % TM.keys())

    def main(self):
        if self.target == 'live':
            raise Exception("not ready for live!")

        self.freeze(self.target)

    @classmethod
    def freeze(cls, target):
        dstPath, pathPrefix = cls.TM[target]
        os.environ[APP.ENV_TARGET] = target
        buildPath = tempfile.mkdtemp()
        app.config.update(FREEZER_DESTINATION=buildPath,
                          FREEZER_RELATIVE_URLS=True,
                          FREEZER_REMOVE_EXTRA_FILES=True)
        freezer = Freezer(app)
        freezer.register_generator(fridge.path_route)
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
        cls.copytree(buildPath, PATH.RENDERED)
        with local.cwd(PATH.RENDERED):
            local['git']('add', '.')
            try:
                local['git']('commit', '-m', 'new build')
            except ProcessExecutionError as e:
                if "nothing to commit" in e.stdout:
                    log.warning("no changes -> nothing to commit")
                    return

                log.warning("commit failed: %s", e)
                return

            local['git']('push')

    @classmethod
    def copytree(cls, src, dst, symlinks=False, ignore=None):
        if not os.path.exists(dst):
            os.makedirs(dst)
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                cls.copytree(s, d, symlinks, ignore)
            else:
                if (not os.path.exists(d) or
                        os.stat(s).st_mtime - os.stat(d).st_mtime > 1):
                    shutil.copy2(s, d)


@Adfd.subcommand('frozen')
class AdfdServeFrozen(cli.Application):
    """Serve frozen web page locally"""
    def main(self):
        frozenPath = PATH.RENDERED
        log.info("'%s' -> http://localhost:%s", frozenPath, SITE.APP_PORT)
        self.serve(frozenPath)

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
