import http.server
import logging
import os
import socketserver

from flask.ext.frozen import Freezer
from plumbum import cli, local

from adfd.cnf import PATH, SITE, DB
from adfd.db.lib import get_db_config_info
from adfd.db.sync import DbSynchronizer
from adfd.site.controller import app, navigator, run_devserver

log = logging.getLogger(__name__)

TEST = ('%s:./www/privat/neu' % DB.REMOTE_HOST, 'privat/neu')
LIVE = ('%s:./www/inhalt' % DB.REMOTE_HOST, 'inhalt')
TARGET_MAP = {'local': (None, None), 'test': TEST, 'live': LIVE}


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
    target = cli.SwitchAttr(
        ['t', 'target'], default='local', help="one of %s" % TARGET_MAP.keys())

    def main(self):
        PATH.FROZEN.delete()
        self.freeze(TARGET_MAP[self.target][1], self.target)

    @staticmethod
    def freeze(pathPrefix, target):
        """:param pathPrefix: for freezing when it's served not from root"""

        def page():
            for _url in navigator.pathNodeMap.keys():
                log.info("yield %s", _url)
                yield {'path': _url}

        log.info("freeze in: %s", PATH.PROJECT)
        os.environ['APP_TARGET'] = target
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
        prefix = TARGET_MAP[self.target][1]
        AdfdFreeze.freeze(prefix, self.target)
        self.deploy(PATH.FROZEN, prefix)

    # FIXME paths and args still screwed up ... still needed
    @staticmethod
    def deploy(outputPath, target):
        """synchronize static website with target"""
        args = ('-av', outputPath + '/', target)
        log.debug('run rsync%s', args)
        rsyncOutput = local['rsync'](*args)
        log.info("rsync result:\n%s", rsyncOutput)


@Adfd.subcommand('frozen')
class AdfdServeFrozen(cli.Application):
    """Serve frozen web page locally"""
    def main(self):
        log.info("'%s' -> http://localhost:%s", PATH.FROZEN, SITE.APP_PORT)
        self.serve(PATH.FROZEN)

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
    logging.basicConfig(level=logging.INFO)
    try:
        Adfd.run()
    except KeyboardInterrupt:
        log.info('stopped by user')
