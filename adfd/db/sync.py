import logging
import os
from functools import cached_property

from plumbum import SshMachine, local

from adfd.cnf import DB, TARGET

log = logging.getLogger(__name__)


class DbSynchronizer:
    def __init__(self):
        self.name = DB.NAME + ".dump"
        self.dst_path = DB.DUMP_PATH / self.name
        self.arg_pwd = f"-p{DB.PW}"
        self.arg_user = f"-u{DB.USER}"

    def __del__(self):
        try:
            self.remote.close()
        except Exception:
            pass

    def sync(self):
        log.warning("doing the dance: takes ~10 minutes ...")
        self.get_dump()
        self.load_dump_into_local_db()

    def get_dump(self):
        self._dump_on_remote()
        self._fetch_from_remote()

    def load_dump_into_local_db(self):
        self._prepare_local_db()
        self._load_dump_locally()

    def _dump_on_remote(self):
        log.info("dump db")
        self.remote["mysqldump"](
            self.arg_user, self.arg_pwd, DB.NAME, f"--result-file={self.name}"
        )

    def _fetch_from_remote(self):
        log.info(f"fetch {self.name} -> {self.dst_path}")
        self.remote.download(self.remote.path(self.name), self.dst_path)

    @staticmethod
    def _prepare_local_db():
        log.info("prepare local db privileges")
        cmds = [
            f"DROP DATABASE IF EXISTS {DB.NAME}",
            f"CREATE DATABASE IF NOT EXISTS {DB.NAME}",
            f"CREATE USER IF NOT EXISTS {DB.USER}@localhost IDENTIFIED BY '{DB.PW}'",
            f"GRANT ALL ON *.* TO {DB.USER}@localhost",
            f"GRANT ALL PRIVILEGES ON {DB.NAME}.* TO {DB.USER}@localhost",
            "FLUSH PRIVILEGES",
        ]
        for cmd in cmds:
            log.debug(f"executing '{cmd}'")
            args = ["-uroot"]
            if DB.LOCAL_ROOT_PW:
                args.extend([f"-p{DB.LOCAL_ROOT_PW}"])
            args.extend(["-e", cmd + ";"])
            local["mysql"](*args)

    def _load_dump_locally(self):
        log.info(f"load local dump from {self.dst_path} (takes ~6 minutes)")
        os.system(f"mysql {self.arg_user} {self.arg_pwd} {DB.NAME} < {self.dst_path}")
        # piping does not work!?
        # local['mysql'](
        #     self.argUser, '-plar', NAME) < self.localDumpPath

    @cached_property
    def remote(self):
        return SshMachine(TARGET.DOMAIN)
