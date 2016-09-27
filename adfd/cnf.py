import plumbum

import yaml

_PROJECT = plumbum.LocalPath(__file__).dirname.up()
_PACKAGE = _PROJECT / 'adfd'

try:
    _CNF = yaml.safe_load(open(_PACKAGE / 'cnf.yml'))
except:
    class _CNF:
        def __getitem__(self, item):
            return None

    _CNF = _CNF()


class NAME:
    STATIC = 'static'


class PATH:
    PROJECT = _PROJECT
    SITE = _PACKAGE / 'site'
    STATIC = SITE / NAME.STATIC
    TEMPLATES = SITE / 'templates'
    FROZEN = _PROJECT / '.frozen'


class APP:
    CSS_PATH = 'dist/semantic.css'
    CSS_MIN_PATH = 'dist/semantic.min.css'
    JS_PATH = 'dist/semantic.js'
    JS_MIN_PATH = 'dist/semantic.min.js'


class SITE:
    ALLOWED_FORUM_IDS = [4, 6, 15, 16, 19, 32, 50, 57, 53, 54, 43]
    ALLOWED_TOPIC_IDS = [9324]
    STRUCTURE_TOPIC_ID = _CNF['structureTopicId']
    STRUCTURE_PATH = PATH.SITE / (_CNF['structurePath'] or 'structure.yml')
    USE_FILE = _CNF['useFile'] or True
    APP_PORT = 5000


class DB:
    USER = _CNF['user']
    PW = _CNF['pw']
    NAME = _CNF['name']
    REMOTE_HOST = _CNF['remoteHost']
    _dbHost = REMOTE_HOST if _CNF['useRemoteDb'] else 'localhost'
    URL = "mysql://%s:%s@%s/%s" % (USER, PW, _dbHost, NAME)
    DUMP_PATH = PATH.PROJECT / _CNF['relDumpPath']
