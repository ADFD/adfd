import logging
import os

from plumbum import SshMachine, local

from cached_property import cached_property

from adfd.cnf import DB, TARGET

log = logging.getLogger(__name__)


class DbSynchronizer:
    def __init__(self):
        self.closableSession = False
        self.dumpName = DB.NAME + '.dump'
        self.dumpDstPath = DB.DUMP_PATH / self.dumpName

    def __del__(self):
        if self.closableSession:
            self.remote.close()

    @cached_property
    def remote(self):
        remote = SshMachine(TARGET.DOMAIN)
        self.closableSession = True
        return remote

    def sync(self):
        self.get_dump()
        self.load_dump_into_local_db()

    def get_dump(self):
        self.dump_on_remote()
        self.fetch_from_remote()

    def load_dump_into_local_db(self):
        self.prepare_local_db()
        self.load_dump_locally()

    def dump_on_remote(self):
        log.info('dump db')
        self.remote['mysqldump'](
            self.argUser, self.argPw,
            DB.NAME, '--result-file=%s' % self.dumpName)

    def fetch_from_remote(self):
        log.info('fetch %s -> %s', self.dumpName, self.dumpDstPath)
        self.remote.download(self.remote.path(self.dumpName), self.dumpDstPath)

    @staticmethod
    def prepare_local_db():
        log.info('prepare local db privileges')
        cmds = [
            f"DROP DATABASE IF EXISTS %s" % DB.NAME,
            "CREATE DATABASE IF NOT EXISTS %s" % DB.NAME,
            ("CREATE USER %s@localhost IDENTIFIED BY '%s'" %
             (DB.USER, DB.PW)),
            ("GRANT ALL ON *.* TO %s@localhost" %
             DB.USER),
            ("GRANT ALL PRIVILEGES ON %s.* TO %s@localhost" %
             (DB.NAME, DB.USER)),
            "FLUSH PRIVILEGES"]
        for cmd in cmds:
            log.info("executing '%s'" % cmd)
            args = ['-uroot']
            if DB.LOCAL_ROOT_PW:
                args.extend(['-p%s' % DB.LOCAL_ROOT_PW])
            args.extend(['-e', cmd + ';'])
            local['mysql'](*args)

    def load_dump_locally(self):
        log.info('load local dump from %s', self.dumpDstPath)
        os.system(
            "mysql %s %s %s < %s" %
            (self.argUser, self.argPw, DB.NAME, self.dumpDstPath))
        # piping does not work!?
        # local['mysql'](
        #     self.argUser, '-plar', NAME) < self.localDumpPath

    @property
    def argUser(self):
        return '-u%s' % DB.USER

    @property
    def argPw(self):
        return '-p%s' % DB.PW
