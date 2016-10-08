import os
import socket

import plumbum

import yaml

_PROJECT = plumbum.LocalPath(__file__).dirname.up()
_PACKAGE = _PROJECT / 'adfd'

try:
    _CNF = yaml.safe_load(open(_PACKAGE / 'cnf.yml'))
except:
    class _CNF:
        def __getitem__(self, item):
            if item == 'useFile':
                return True

            return None

    _CNF = _CNF()


class NAME:
    STATIC = 'static'
    CONTENT = 'content'
    ROOT = '_root'
    BBCODE = 'bbcode'


class PATH:
    PROJECT = _PROJECT
    SITE = _PACKAGE / 'site'
    STATIC = SITE / NAME.STATIC
    ROOT_FILES = STATIC / '_root'
    VIEW = SITE / 'view'
    RENDERED = _PROJECT / '..' / 'static'


class APP:
    CSS_PATH = 'dist/semantic.css'
    CSS_MIN_PATH = 'dist/semantic.min.css'
    JS_PATH = 'dist/semantic.js'
    JS_MIN_PATH = 'dist/semantic.min.js'


class SITE:
    ALLOWED_FORUM_IDS = [4, 6, 15, 16, 19, 32, 50, 57, 53, 54, 56, 43]
    ALLOWED_TOPIC_IDS = [9324]
    STRUCTURE_TOPIC_ID = _CNF['structureTopicId']
    STRUCTURE_PATH = PATH.SITE / (_CNF['structurePath'] or 'structure.yml')
    STATIC_ARTICLES_PATH = PATH.STATIC / 'content' / 'articles'
    USE_FILE = _CNF['useFile']
    APP_PORT = 5000
    META_TAG = 'meta'
    CODE_TAG = 'code'
    VIEWTOPIC_PATTERN = "http://adfd.org/austausch/viewtopic.php?t=%s"


class DB:
    USER = _CNF['user']
    PW = _CNF['pw']
    NAME = _CNF['name']
    REMOTE_HOST = _CNF['remoteHost']
    _dbHost = REMOTE_HOST if _CNF['useRemoteDb'] else 'localhost'
    URL = "mysql://%s:%s@%s/%s" % (USER, PW, _dbHost, NAME)
    DUMP_PATH = PATH.PROJECT / _CNF['relDumpPath']


class TARGET:
    DOMAIN = _CNF['remoteHost']
    VIRT_ENV_BIN_PATH_STR = '/home/.pyenv/versions/adfd/bin'
    ADFD_BIN = VIRT_ENV_BIN_PATH_STR + '/adfd'
    PIP_BIN = VIRT_ENV_BIN_PATH_STR + '/pip'
    HOME = plumbum.LocalPath('/home')
    WWW = HOME / 'www'
    TOOL = HOME / 'adfd'
    PREFIX_STR = 'privat/neu'
    IS_TESTING = socket.gethostname() == '1bo' or 'CI' in os.environ
    STAGING = PATH.RENDERED if IS_TESTING else WWW / PREFIX_STR
