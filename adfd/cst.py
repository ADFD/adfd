import tempfile

import plumbum

try:
    from adfd.db.local_settings import _dbUrl, _contentRoot
except ImportError:
    _dbUrl = "mysql://user:password@localhost/dbname"
    _contentRoot = tempfile.gettempdir()


DB_URL = _dbUrl
# If you don't provide encoding, I will. See: http://goo.gl/rGuQey
if 'charset' not in DB_URL:
    DB_URL += '?charset=utf8'

_CONTENT_ROOT = plumbum.LocalPath(_contentRoot)


class EXT:
    IN = '.bbcode'
    OUT = '.html'
    META = '.meta'


class DIR:
    RAW = 'raw'
    """folders containing topics one file per post + metadata for each post"""
    PREPARED = 'prepared'
    """merged single file raw articles and merged single file metadata"""
    FINAL = 'final'
    """rendered and structured result with additional category metadata"""


class NAME:
    CATEGORY = 'category'
    INDEX = 'index'
    PAGE = 'page'


class PAGE:
    ROOT = 'root'
