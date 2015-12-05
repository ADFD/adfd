import tempfile

import plumbum

try:
    from adfd.db.local_settings import _dbUrl, _contentRoot
except ImportError:
    _dbUrl = "mysql://user:password@localhost/dbname"
    _contentRoot = tempfile.gettempdir()


DB_URL = _dbUrl + '?charset=utf8'
"""Important! See: http://goo.gl/rGuQey"""

CONTENT_ROOT = plumbum.LocalPath(_contentRoot)


class EXT(object):
    BBCODE = '.bbcode'
    META = '.meta'
    HTML = '.html'


class DIR(object):
    RAW = 'raw'
    PREPARED = 'prepared'
    FINAL = 'final'
    """the resulting html"""


class PAGE(object):
    ROOT = 'root'
