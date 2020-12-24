import http.server
import logging
import socketserver

from plumbum import ProcessExecutionError, SshMachine, cli, local

from adfd.cnf import PATH, SITE, TARGET
from adfd.db.check_urls import check_site_urls
from adfd.db.lib import DB_WRAPPER
from adfd.db.sync import DbSynchronizer
from adfd.site import fridge
from adfd.site.wsgi import run_devserver

log = logging.getLogger(__name__)


def main():
    try:
        Adfd.run()
    except KeyboardInterrupt:
        log.info("stopped by user")


class Adfd(cli.Application):
    """All functions for the ADFD website"""

    logLevel = cli.SwitchAttr(["l", "log-level"], default="INFO", help="set log level")

    def main(self):
        if not self.nested_command:
            self.nested_command = (AdfdDev, ["adfd dev"])


@Adfd.subcommand("dev")
class AdfdDev(cli.Application):
    """Run local development server"""

    def main(self):
        run_devserver()


@Adfd.subcommand("db-sync")
class AdfdDbSync(cli.Application):
    """Dump DB on remote, download the dump and load it to the local DB."""

    def main(self):
        dbs = DbSynchronizer()
        dbs.sync()


@Adfd.subcommand("freeze")
class AdfdFreeze(cli.Application):
    """Freeze website to static files"""

    def main(self):
        fridge.AdfdFreezer.freeze()


@Adfd.subcommand("serve-frozen")
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


@Adfd.subcommand("info")
class AdfdInfo(cli.Application):
    def main(self):
        msg = ""
        allowedForums = [
            "{} ({})".format(DB_WRAPPER.get_forum(fId).forum_name, fId)
            for fId in SITE.ALLOWED_FORUM_IDS
        ]
        msg += "allowed Forums:\n    %s" % ("\n    ".join(allowedForums))
        print(msg)


@Adfd.subcommand("check-links")
class AdfdCheckLinks(cli.Application):
    """Check if all links from website are healthy"""

    def main(self):
        return check_site_urls()


# #############################################################################
# ######################### ESOTERIC SECTION ##################################
# #############################################################################


@Adfd.subcommand("xtra-db-fetch")
class AdfdDbFetch(cli.Application):
    """Fetch db dump from remote"""

    def main(self):
        dbs = DbSynchronizer()
        dbs.get_dump()


@Adfd.subcommand("xtra-db-load")
class AdfdDbLoad(cli.Application):
    """Load db dump into local db"""

    def main(self):
        dbs = DbSynchronizer()
        dbs.load_dump_into_local_db()


@Adfd.subcommand("xtra-pull-code")
class AdfdPullCode(cli.Application):
    def main(self):
        hostPip = "/home/.pyenv/versions/adfd/bin/pip"
        with local.cwd(PATH.PROJECT):
            print(local["git"]("pull"))
            print(local[hostPip]("install", "-U", "-e", PATH.PROJECT))


@Adfd.subcommand("xtra-deploy-code")
class AdfdDeployCode(cli.Application):
    def main(self):
        self.deploy_code()

    @classmethod
    def deploy_code(cls):
        remote = SshMachine(TARGET.DOMAIN)
        with remote.cwd(TARGET.TOOL_PATH):
            print(remote["git"]("pull"))
            print(remote[PATH.VENV_PIP]("install", "-U", "-e", "."))


@Adfd.subcommand("xtra-push-content")
class AdfdPushContent(cli.Application):
    def main(self):
        self.push_content()

    @classmethod
    def push_content(cls):
        with local.cwd(PATH.RENDERED):
            print(local["git"]("add", "."))
            try:
                print(local["git"]("commit", "-m", "new build"))
            except ProcessExecutionError as e:
                if "nothing to commit" in e.stdout:
                    log.warning("no changes -> nothing to commit")
                    return

                log.warning("commit failed: %s", e)
                return

            print(local["git"]("push"))


@Adfd.subcommand("xtra-deploy")
class AdfdDeploy(cli.Application):
    """Deploy code by pulling it from github"""

    def main(self):
        AdfdFreeze.freeze()
        AdfdPushContent.push_content()
        self.deploy_content()

    @classmethod
    def deploy_content(cls):
        remote = SshMachine(TARGET.DOMAIN)
        with remote.cwd(TARGET.CHECKOUT_PATH):
            print(remote["git"]("reset", "--hard"))
            print(remote["git"]("clean", "-f", "-d"))
            print(remote["git"]("pull"))
        with remote.cwd(TARGET.TOOL_PATH):
            print(remote["adfd"]("fix-staging-paths"))


@Adfd.subcommand("xtra-fix-staging-paths")
class AdfdFixStagingPaths(cli.Application):
    """fix paths for deployed site - only during dev - get rid of this later"""

    def main(self):
        fridge.AdfdFreezer.fix_staging_paths()
