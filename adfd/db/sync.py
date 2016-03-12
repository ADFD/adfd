import logging
import os

from plumbum import SshMachine, LocalPath, local

from adfd.db.local_settings import DB

log = logging.getLogger(__name__)


class DbSynchronizer:
    def __init__(self, db=DB):
        self.db = db
        self.sm = SshMachine(self.db.SSH_HOST)
        self.dumpName = self.db.NAME + '.dump'
        self.localDumpPath = LocalPath(__file__).up() / self.dumpName

    def __del__(self):
        self.sm.close()

    def sync_db(self):
        self.dump()
        self.fetch()
        self.prepare_local_db()
        self.load_local_dump()

    def dump(self):
        log.info('dump db')
        self.sm['mysqldump'](
            self.argUser, self.argPw,
            self.db.NAME, '--result-file=%s' % (self.dumpName))

    def fetch(self):
        log.info('fetch %s -> %s', self.dumpName, self.localDumpPath)
        self.sm.download(self.sm.path(self.dumpName), self.localDumpPath)

    def prepare_local_db(self):
        log.info('prepare local db privileges')
        cmds = [
            "DROP DATABASE IF EXISTS %s" % (self.db.NAME),
            "CREATE DATABASE IF NOT EXISTS %s" % (self.db.NAME),
            ("GRANT USAGE ON *.* TO "
             "%s@localhost IDENTIFIED BY '%s'" % (self.db.USER, self.db.PW)),
            ("GRANT ALL PRIVILEGES ON "
             "%s.* TO %s@localhost" % (self.db.NAME, self.db.USER)),
            "FLUSH PRIVILEGES"]
        local['mysql']('-uroot', '-e', "; ".join(cmds))

    def load_local_dump(self):
        log.info('load local dump from %s', self.localDumpPath)
        os.system(
            "mysql %s %s %s < %s" %
            (self.argUser, self.argPw, self.db.NAME, self.localDumpPath))
        # piping does not work!?
        # local['mysql'](
        #     self.argUser, '-plar', self.db.NAME) < self.localDumpPath

    @property
    def argUser(self):
        return '-u%s' % (self.db.USER)

    @property
    def argPw(self):
        return '-p%s' % (self.db.PW)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    DbSynchronizer().sync_db()
