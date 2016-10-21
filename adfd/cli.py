import http.server
import logging
import os
import shutil
import socketserver
import tempfile

from adfd.cnf import PATH, SITE, TARGET, VIRTENV, INFO
from adfd.db.lib import DB_WRAPPER
from adfd.db.sync import DbSynchronizer
from adfd.site import fridge
from adfd.site.controller import app, run_devserver
from adfd.utils import configure_logging, date_from_timestamp
from flask.ext.frozen import Freezer
from plumbum import ProcessExecutionError, SshMachine, cli, local

log = logging.getLogger(__name__)


class Adfd(cli.Application):
    """All functions for the ADFD website"""
    logLevel = cli.SwitchAttr(
        ['l', 'log-level'], default='INFO', help="set log level")

    def main(self):
        configure_logging(self.logLevel)
        if not self.nested_command:
            self.nested_command = (AdfdDev, ['adfd dev'])


@Adfd.subcommand('db-sync')
class AdfdDbSync(cli.Application):
    noRemote = cli.Flag(['--no-remote'], help="only load from dump")

    def main(self):
        if self.noRemote:
            DbSynchronizer().update_local_db()
        else:
            DbSynchronizer().sync()


@Adfd.subcommand('dev')
class AdfdDev(cli.Application):
    """Run local development server"""
    def main(self):
        run_devserver()


@Adfd.subcommand('gulp')
class AdfdGulp(cli.Application):
    """Run local development server"""
    def main(self):
        with local.cwd(PATH.SEMANTIC):
            os.system("gulp build")
            os.system("gulp watch")


@Adfd.subcommand('freeze')
class AdfdFreeze(cli.Application):
    """Freeze website to static files"""
    noPush = cli.Flag(['--no-push'], default=False)
    pullCode = cli.Flag(['--pull-code'], default=False)

    def main(self):
        self.freeze(self.pullCode, not self.noPush)

    @classmethod
    def freeze(cls, pullCode, push):
        if pullCode:
            cls.pull_code_from_github()
        buildPath = tempfile.mkdtemp()
        app.config.update(
            FREEZER_DESTINATION=PATH.RENDERED,
            FREEZER_RELATIVE_URLS=True,
            FREEZER_REMOVE_EXTRA_FILES=True,
            FREEZER_DESTINATION_IGNORE=['.git*', '*.idea'])
        freezer = Freezer(app)
        freezer.register_generator(fridge.path_route)
        with local.cwd(PATH.PROJECT):
            log.info("freezing %s", freezer)
            with open(PATH.LAST_UPDATE, 'w', encoding='utf') as f:
                f.write(date_from_timestamp())
            seenUrls = freezer.freeze()
            log.info("frozen urls are:\n%s", '\n'.join(seenUrls))
        cls.copytree(buildPath, PATH.RENDERED)
        cls.deliver_static_root_files()
        cls.remove_clutter()
        if not INFO.IS_DEV_BOX:
            AdfdFixStagingPaths.fix_staging_paths()
        if push:
            cls.push_to_github()
        print("ADFD site successfully frozen!")

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
    def pull_code_from_github(cls):
        with local.cwd(PATH.PROJECT):
            print(local['git']('pull'))
            print(local['git']('status'))

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
        self.serve()

    @staticmethod
    def serve():
        log.info("%s -> http://localhost:%s", PATH.RENDERED, SITE.FROZEN_PORT)
        with local.cwd(PATH.RENDERED):
            Handler = http.server.SimpleHTTPRequestHandler
            httpd = socketserver.TCPServer(("", SITE.FROZEN_PORT), Handler)
            try:
                httpd.serve_forever()
            finally:
                httpd.server_close()


@Adfd.subcommand('deploy')
class AdfdDeploy(cli.Application):
    """Deploy code by pulling it from github"""
    def main(self):
        remote = SshMachine(TARGET.DOMAIN)
        with remote.cwd(TARGET.CHECKOUT_PATH):
            print(remote['git']('reset', '--hard'))
            print(remote['git']('clean', '-f', '-d'))
            print(remote['git']('pull'))
        with remote.cwd(TARGET.TOOL_PATH):
            print(remote['git']('pull'))
            print(remote[VIRTENV.PIP_BIN]('install', '-U', '-e', '.'))
            print(remote['cp'](VIRTENV.ACTIVATE_THIS_SRC, VIRTENV.FOLDER))
            print(remote['adfd']('fix-staging-paths'))


@Adfd.subcommand('fix-staging-paths')
class AdfdFixStagingPaths(cli.Application):
    """fix paths for deployed site"""

    def main(self):
        self.fix_staging_paths()

    @classmethod
    def fix_staging_paths(cls):
        log.warning("prefix %s - changing links", TARGET.PREFIX_STR)
        for path in cls.get_all_page_paths():
            cnt = path.read(encoding='utf8')
            cnt = cnt.replace('href="/', 'href="/%s/' % TARGET.PREFIX_STR)
            with open(path, 'w', encoding='utf8') as f:
                f.write(cnt)

    @classmethod
    def get_all_page_paths(cls):
        return [p for p in PATH.RENDERED.walk() if p.endswith("index.html")]


@Adfd.subcommand('info')
class AdfdInfo(cli.Application):
    def main(self):
        msg = ""
        allowedForums = [
            "%s (%s)" % (DB_WRAPPER.get_forum(fId).forum_name, fId)
            for fId in SITE.ALLOWED_FORUM_IDS]
        msg += "allowed Forums:\n    %s" % ("\n    ".join(allowedForums))
        print(msg)


def main():
    try:
        Adfd.run()
    except KeyboardInterrupt:
        log.info('stopped by user')
