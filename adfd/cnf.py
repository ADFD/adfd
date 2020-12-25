import os
import socket

import plumbum
import yaml

_PROJECT_PATH = plumbum.LocalPath(__file__).dirname.up()
_PACKAGE_PATH = _PROJECT_PATH / "adfd"
_CONFIG_PATH = _PROJECT_PATH / "cnf.yml"
_HOSTNAME = socket.gethostname()


class INFO:
    IS_CI = "CI" in os.environ
    IS_DEV_BOX = "mj13" not in _HOSTNAME


if not _CONFIG_PATH.exists():
    assert INFO.IS_CI or INFO.IS_DEV_BOX, _HOSTNAME

    class _CNF:
        def __getitem__(self, item):
            if item == "useFile":
                return True

            return None

    _CNF = _CNF()
else:
    _CNF = yaml.safe_load(open(_CONFIG_PATH))


class NAME:
    ARTICLES = "articles"
    DB_CACHE = "db-cache"
    STATIC = "static"
    CONTENT = "content"
    ROOT = "_root"
    BBCODE = "bbcode"


class EXT:
    BBCODE = f".{NAME.BBCODE}"
    MD = ".md.json"


class TARGET:
    DOMAIN = _CNF["remoteHost"]
    HOME = plumbum.LocalPath("/home")
    TOOL_PATH = HOME / "adfd"
    PREFIX_STR = "privat/neu"
    WWW = HOME / "www"
    CHECKOUT_PATH = WWW / PREFIX_STR


class PATH:
    PROJECT = _PROJECT_PATH
    SITE = _PACKAGE_PATH / "site"
    SEMANTIC = SITE / "semantic"
    STATIC = SITE / NAME.STATIC
    CONTENT = STATIC / NAME.CONTENT
    ARTICLES = CONTENT / NAME.ARTICLES
    DB_CACHE = CONTENT / NAME.DB_CACHE
    DB_CACHE_PERMANENT = CONTENT / f"{NAME.DB_CACHE}-permanent"
    ROOT_FILES = STATIC / "_root"
    VIEW = SITE / "view"
    _DEV_BOX_RENDERED = _PROJECT_PATH / ".." / NAME.STATIC
    RENDERED = _DEV_BOX_RENDERED if INFO.IS_DEV_BOX else TARGET.CHECKOUT_PATH
    BBCODE_BACKUP = RENDERED / "bbcode-sources"
    VENV_PIP = "/home/.pyenv/versions/adfd/bin/pip"


class APP:
    MY_CSS_FILE_NAME = "adfd.css"


class SITE:
    MAIN_CONTENT_FORUM_ID = 54
    ALLOWED_FORUM_IDS = [4, 6, 15, 16, 19, 32, 50, 57, 53, 56, 43]
    STRUCTURE_TOPIC_ID = _CNF["structureTopicId"]
    PLACEHOLDER_TOPIC_ID = 12265
    IGNORED_CONTENT_TOPICS = [PLACEHOLDER_TOPIC_ID, STRUCTURE_TOPIC_ID]
    STRUCTURE_PATH = PATH.SITE / (_CNF["structurePath"] or "structure.yml")
    STATIC_ARTICLES_PATH = PATH.STATIC / NAME.CONTENT / NAME.ARTICLES
    USE_FILE = _CNF["useFile"]
    APP_PORT = 5000
    FROZEN_PORT = APP_PORT + 1
    META_TAG = "meta"
    CODE_TAG = "code"
    TOPIC_REL_PATH_PATTERN = "http://adfd.org//austausch/viewtopic.php?t=%s"
    IGNORED_TAG_ELEMENTS = [
        "inhalt",
        "seroxat",
        "ergänzung",
        "david",
        "anmerkung",
        "link",
        "halbwegs",
        "ad",
        "wieder",
        "11c",
        ":",
        ".",
        "...",
    ]
    """FIXME these should all not be in square brackets to start with"""


class DB:
    USER = _CNF["user"]
    PW = _CNF["pw"]
    LOCAL_ROOT_PW = _CNF["localRootPw"]
    NAME = _CNF["name"]
    REMOTE_HOST = _CNF["remoteHost"]
    _dbHost = REMOTE_HOST if _CNF["useRemoteDb"] else "localhost"
    URL = f"mysql://{USER}:{PW}@{_dbHost}/{NAME}"
    DUMP_PATH = PATH.PROJECT / _CNF["relDumpPath"] / "dumps"
