import os
import socket

import plumbum
import yaml

_HERE = plumbum.LocalPath(__file__).dirname
_PROJECT_PATH = _HERE.up()


class RUNS_ON:
    CI = bool(os.getenv("CI"))
    DEVBOX = not CI and "mj13" not in socket.gethostname()


_CONFIG_PATH = _PROJECT_PATH / "cnf.yml"
if not _CONFIG_PATH.exists():

    class _CNF:
        def __getitem__(self, item):
            if item == "useFile":
                return True

            return None

    _CNF = _CNF()
else:
    _CNF = yaml.safe_load(_CONFIG_PATH.read())


class NAME:
    ARTICLES = "articles"
    ATTACHMENTS = "attachments"
    BBCODE = "bbcode"
    DB_CACHE = "db-cache"
    FROZEN = "frozen"
    IMG = "img"
    WEB = "web"
    STATIC = "_static"


class EXT:
    BBCODE = f".{NAME.BBCODE}"
    MD = ".md.json"


class TARGET:
    DOMAIN = _CNF["remoteHost"]
    HOME = plumbum.LocalPath("/home")
    TOOL_PATH = HOME / "adfd"
    PREFIX_STR = "privat/neu"
    WWW = HOME / "www"
    CHECKOUT_PATH = WWW / PREFIX_STR  # FIXME html is now at PATH.FROZEN
    VENV_PIP_PATH = "/home/.pyenv/versions/adfd/bin/pip"


class PATH:
    PROJECT = _PROJECT_PATH
    WEB = _HERE / NAME.WEB
    VIEW_VANILLA = WEB / "view-vanilla"
    VIEW_SEMANTIC = WEB / "view-semantic"
    VIEW_TAILWIND = WEB / "view-tailwind"
    SITE_REPO = PROJECT.up() / "site"
    ARTICLES = SITE_REPO / NAME.ARTICLES
    DB_CACHE = SITE_REPO / NAME.DB_CACHE
    IMG = SITE_REPO / NAME.IMG
    FROZEN = SITE_REPO / NAME.FROZEN
    STATIC_FILES = SITE_REPO / "_static"
    RENDERED_ATTACHMENTS = STATIC_FILES / NAME.ATTACHMENTS


class APP:
    MY_CSS_FILE_NAME = "adfd.css"


class ADFD:
    MAIN_CONTENT_FORUM_ID = 54
    ALLOWED_FORUM_IDS = [4, 6, 15, 16, 19, 32, 50, 57, 53, 56, 43]
    STRUCTURE_TOPIC_ID = 12109
    PLACEHOLDER_TOPIC_ID = 12265
    IGNORED_CONTENT_TOPICS = [PLACEHOLDER_TOPIC_ID, STRUCTURE_TOPIC_ID]
    STRUCTURE_PATH = PATH.WEB / "structure.yml"
    USE_FILE = _CNF["useFile"]
    APP_PORT = 5000
    FROZEN_PORT = APP_PORT + 1
    META_TAG = "meta"
    CODE_TAG = "code"
    REPO_URL = "https://github.com/ADFD/site/tree/master"
    FORUM_VIEWTOPIC_URL = "https://adfd.org/austausch/viewtopic.php"
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
