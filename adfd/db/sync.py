import logging
import os

from plumbum import SshMachine, local

log = logging.getLogger(__name__)

try:
    from adfd.secrets import DB
    NAME = DB.NAME
    USER = DB.USER
    PW = DB.PW
    DUMP_PATH = DB.DUMP_PATH
    REMOTE_HOST = DB.REMOTE_HOST
except ImportError:
    log.warning("no module with secrets found - using dummy values")
    NAME = "dummyname"
    USER = "dummyuser"
    PW = "dummypassword"
    DUMP_PATH = "/dummy/dump/path"
    REMOTE_HOST = "dummy-host.de"

log = logging.getLogger(__name__)


class DbSynchronizer:
    def __init__(self):
        self.sm = SshMachine(REMOTE_HOST)
        self.dumpName = NAME + '.dump'
        self.dumpDstPath = DUMP_PATH / self.dumpName

    def __del__(self):
        self.sm.close()

    def sync(self):
        self.dump()
        self.fetch()
        self.prepare_local_db()
        self.load_local_dump()

    def dump(self):
        log.info('dump db')
        self.sm['mysqldump'](
            self.argUser, self.argPw,
            NAME, '--result-file=%s' % (self.dumpName))

    def fetch(self):
        log.info('fetch %s -> %s', self.dumpName, self.dumpDstPath)
        self.sm.download(self.sm.path(self.dumpName), self.dumpDstPath)

    def prepare_local_db(self):
        log.info('prepare local db privileges')
        cmds = [
            "DROP DATABASE IF EXISTS %s" % (NAME),
            "CREATE DATABASE IF NOT EXISTS %s" % (NAME),
            ("GRANT USAGE ON *.* TO %s@localhost IDENTIFIED BY '%s'" %
             (USER, PW)),
            ("GRANT ALL PRIVILEGES ON %s.* TO %s@localhost" %
             (NAME, USER)),
            "FLUSH PRIVILEGES"]
        local['mysql']('-uroot', '-e', "; ".join(cmds))

    def load_local_dump(self):
        log.info('load local dump from %s', self.dumpDstPath)
        os.system(
            "mysql %s %s %s < %s" %
            (self.argUser, self.argPw, NAME, self.dumpDstPath))
        # piping does not work!?
        # local['mysql'](
        #     self.argUser, '-plar', NAME) < self.localDumpPath

    @property
    def argUser(self):
        return '-u%s' % (USER)

    @property
    def argPw(self):
        return '-p%s' % (PW)
