import os
import socket

import plumbum

import yaml

_PROJECT = plumbum.LocalPath(__file__).dirname.up()
_PACKAGE = _PROJECT / 'adfd'

try:
    _CNF = yaml.safe_load(open(_PROJECT / 'cnf.yml'))
except:
    class _CNF:
        def __getitem__(self, item):
            if item == 'useFile':
                return True

            return None

    _CNF = _CNF()


class INFO:
    IS_DEV_BOX = socket.gethostname() == '1bo'
    IS_CI = 'CI' in os.environ


class NAME:
    STATIC = 'static'
    CONTENT = 'content'
    ROOT = '_root'
    BBCODE = 'bbcode'


class TARGET:
    DOMAIN = _CNF['remoteHost']
    HOME = plumbum.LocalPath('/home')
    TOOL_PATH = HOME / 'adfd'
    PREFIX_STR = 'privat/neu'
    WWW = HOME / 'www'
    CHECKOUT_PATH = WWW / PREFIX_STR


class PATH:
    PROJECT = _PROJECT
    SITE = _PACKAGE / 'site'
    SEMANTIC = SITE / 'semantic'
    STATIC = SITE / NAME.STATIC
    ROOT_FILES = STATIC / '_root'
    VIEW = SITE / 'view'
    _DEV_BOX_RENDERED = _PROJECT / '..' / 'static'
    RENDERED = _DEV_BOX_RENDERED if INFO.IS_DEV_BOX else TARGET.CHECKOUT_PATH
    BBCODE_BACKUP = RENDERED / 'bbcode-sources'
    LAST_UPDATE = RENDERED / 'last_updated'


class APP:
    CSS_PATH = 'dist/semantic.css'
    CSS_MIN_PATH = 'dist/semantic.min.css'
    JS_PATH = 'dist/semantic.js'
    JS_MIN_PATH = 'dist/semantic.min.js'


class SITE:
    MAIN_CONTENT_FORUM_ID = 54
    ALLOWED_FORUM_IDS = [4, 6, 15, 16, 19, 32, 50, 57, 53, 56, 43]
    # TODO import Lob Topic 9324
    STRUCTURE_TOPIC_ID = _CNF['structureTopicId']
    PLACEHOLDER_TOPIC_ID = 12265
    IGNORED_CONTENT_TOPICS = [PLACEHOLDER_TOPIC_ID, STRUCTURE_TOPIC_ID]
    STRUCTURE_PATH = PATH.SITE / (_CNF['structurePath'] or 'structure.yml')
    STATIC_ARTICLES_PATH = PATH.STATIC / 'content' / 'articles'
    USE_FILE = _CNF['useFile']
    APP_PORT = 5000
    FROZEN_PORT = APP_PORT + 1
    META_TAG = 'meta'
    CODE_TAG = 'code'
    TOPIC_REL_PATH_PATTERN = "http://adfd.org//austausch/viewtopic.php?t=%s"
    IGNORED_TAG_ELEMENTS = [
        'inhalt', 'seroxat', 'ergänzung', 'david', 'anmerkung', 'link',
        'halbwegs', 'ad', 'wieder',
        ":", ".", "..."]


class DB:
    USER = _CNF['user']
    PW = _CNF['pw']
    LOCAL_ROOT_PW = _CNF['localRootPw']
    NAME = _CNF['name']
    REMOTE_HOST = _CNF['remoteHost']
    _dbHost = REMOTE_HOST if _CNF['useRemoteDb'] else 'localhost'
    URL = "mysql://%s:%s@%s/%s" % (USER, PW, _dbHost, NAME)
    DUMP_PATH = PATH.PROJECT / _CNF['relDumpPath']


class VIRTENV:
    FOLDER = '/home/.pyenv/versions/adfd/bin'
    ACTIVATE_SCRIPT = 'activate_this.py'
    ACTIVATE_THIS_SRC = '/home/adfd/adfd/site/' + ACTIVATE_SCRIPT
    ACTIVATE_THIS_SCRIPT = FOLDER + '/' + ACTIVATE_SCRIPT
    ADFD_BIN = FOLDER + '/adfd'
    PIP_BIN = FOLDER + '/pip'
