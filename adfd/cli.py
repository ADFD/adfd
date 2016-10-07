import http.server
import logging
import os
import shutil
import socketserver
import tempfile

from flask.ext.frozen import Freezer
from plumbum import ProcessExecutionError, SshMachine, cli, local

from adfd.cnf import PATH, SITE, DB, TARGET
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
    push = cli.SwitchAttr(
        ['p', 'push'], argtype=bool, default=True, help="push changes")

    def main(self):
        self.freeze(self.push)

    @classmethod
    def freeze(cls, push):
        buildPath = tempfile.mkdtemp()
        app.config.update(
            FREEZER_DESTINATION=PATH.RENDERED,
            FREEZER_RELATIVE_URLS=True,
            FREEZER_REMOVE_EXTRA_FILES=True,
            FREEZER_DESTINATION_IGNORE=['.git*','*.idea'])
        freezer = Freezer(app)
        freezer.register_generator(fridge.path_route)
        with local.cwd(PATH.PROJECT):
            log.info("freezing %s", freezer)
            seenUrls = freezer.freeze()
            log.info("frozen urls are:\n%s", '\n'.join(seenUrls))
        cls.copytree(buildPath, PATH.RENDERED)
        cls.deliver_static_root_files()
        cls.remove_clutter()
        if push:
            cls.push_to_github()

    @classmethod
    def deliver_static_root_files(cls):
        for path in [p for p in PATH.ROOT_FILES.walk() if p.is_file()]:
            path.copy(PATH.RENDERED)

    @classmethod
    def remove_clutter(cls):
        for path in [
            # PATH.RENDERED / 'static/experiments',
            PATH.RENDERED / 'static/_root',
            PATH.RENDERED / 'reset',
        ]:
            path.delete()

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

    @classmethod
    def push_to_github(cls):
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


@Adfd.subcommand('deploy')
class AdfdDeploy(cli.Application):
    """Deploy code by pulling it from github"""
    def main(self):
        remote = SshMachine(TARGET.DOMAIN)
        with remote.cwd(TARGET.STAGING):
            print(remote['git']('pull'))
        with remote.cwd(TARGET.TOOL):
            print(remote['git']('pull'))
            print(remote[TARGET.PYTHON_BIN]('pip', 'install', '-U', '-e', '.'))
            print(remote['adfd']('fix-staging-paths'))


@Adfd.subcommand('fix-staging-paths')
class AdfdFixStagingPaths(cli.Application):
    """fix paths for deployed site"""

    def main(self):
        self.fix_staging_paths()

    @classmethod
    def fix_staging_paths(cls):
        log.warning("prefix %s - changing links", TARGET.PREFIX_STR)
        print(cls.get_all_page_paths())
        return

        for path in cls.get_all_page_paths():
            with open(path) as f:
                cnt = f.read()
            cnt = cnt.replace('href="/', 'href="/%s/' % TARGET.PREFIX_STR)
            with open(path, 'w') as f:
                f.write(cnt)

    @classmethod
    def get_all_page_paths(cls):
        return [p for p in TARGET.STAGING.walk() if p.endswith("index.html")]


@Adfd.subcommand('info')
class AdfdInfo(cli.Application):
    def main(self):
        print(get_db_config_info)


def main():
    try:
        Adfd.run()
    except KeyboardInterrupt:
        log.info('stopped by user')
