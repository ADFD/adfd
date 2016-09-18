import logging
import os

from plumbum import SshMachine, local

from adfd.secrets import DB


log = logging.getLogger(__name__)


class DbSynchronizer:
    def __init__(self):
        self.sm = SshMachine(DB.REMOTE_HOST)
        self.dumpName = DB.NAME + '.dump'
        self.dumpDstPath = DB.DUMP_PATH / self.dumpName

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
            DB.NAME, '--result-file=%s' % (self.dumpName))

    def fetch(self):
        log.info('fetch %s -> %s', self.dumpName, self.dumpDstPath)
        self.sm.download(self.sm.path(self.dumpName), self.dumpDstPath)

    def prepare_local_db(self):
        log.info('prepare local db privileges')
        cmds = [
            "DROP DATABASE IF EXISTS %s" % (DB.NAME),
            "CREATE DATABASE IF NOT EXISTS %s" % (DB.NAME),
            ("GRANT USAGE ON *.* TO "
             "%s@localhost IDENTIFIED BY '%s'" % (DB.USER, DB.PW)),
            ("GRANT ALL PRIVILEGES ON "
             "%s.* TO %s@localhost" % (DB.NAME, DB.USER)),
            "FLUSH PRIVILEGES"]
        local['mysql']('-uroot', '-e', "; ".join(cmds))

    def load_local_dump(self):
        log.info('load local dump from %s', self.dumpDstPath)
        os.system(
            "mysql %s %s %s < %s" %
            (self.argUser, self.argPw, DB.NAME, self.dumpDstPath))
        # piping does not work!?
        # local['mysql'](
        #     self.argUser, '-plar', DB.NAME) < self.localDumpPath

    @property
    def argUser(self):
        return '-u%s' % (DB.USER)

    @property
    def argPw(self):
        return '-p%s' % (DB.PW)
