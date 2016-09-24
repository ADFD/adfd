import plumbum

import yaml

_PROJECT = plumbum.LocalPath(__file__).dirname.up()
_PACKAGE = _PROJECT / 'adfd'
_CNF = yaml.safe_load(open(_PACKAGE / 'cnf.yml'))


class PATH:
    PROJECT = _PROJECT
    SITE = _PACKAGE / 'site'
    STATIC = SITE / _CNF['webAssetsRelPath']
    TEMPLATES = SITE / 'templates'
    FROZEN = _PROJECT / '.frozen'


class SITE:
    STRUCTURE_TOPIC_ID = _CNF['structureTopicId']
    STRUCTURE_PATH = PATH.SITE / _CNF['structurePath']
    USE_FILE = _CNF['useFile']
    APP_PORT = 5000


class DB:
    USER = _CNF['user']
    PW = _CNF['pw']
    NAME = _CNF['name']
    REMOTE_HOST = _CNF['remoteHost']
    _dbHost = REMOTE_HOST if _CNF['useRemoteDb'] else 'localhost'
    URL = "mysql://%s:%s@%s/%s" % (USER, PW, _dbHost, NAME)
    DUMP_PATH = PATH.PROJECT / _CNF['relDumpPath']
