import tempfile

import plumbum

try:
    from adfd.db.local_settings import _dbUrl, _contentRoot
except ImportError:
    _dbUrl = "mysql://user:password@localhost/dbname"
    _contentRoot = tempfile.gettempdir()


DB_URL = _dbUrl + '?charset=utf8'
"""Important! See: http://goo.gl/rGuQey"""

_CONTENT_ROOT = plumbum.LocalPath(_contentRoot)


class EXT(object):
    IN = '.bbcode'
    OUT = '.html'
    META = '.meta'


class DIR(object):
    RAW = 'raw'
    PREPARED = 'prepared'
    FINAL = 'final'
    """the resulting html"""


class NAME(object):
    CATEGORY = 'category'


class PAGE(object):
    ROOT = 'root'
