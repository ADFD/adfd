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


class DIR(object):
    RAW = 'raw'
    PREPARED = 'prepared'
    FINAL = 'final'
    """the resulting html"""


class PATH(object):
    PROJECT = plumbum.LocalPath(__file__).up().up(2) / 'adfd'
    TEST_DATA = PROJECT / 'adfd' / 'tests' / 'data'
    CONTENT = CONTENT_ROOT
    CNT_RAW = CONTENT / DIR.RAW
    """exported bbcode like it looks when edited - each posts in a single file.

    It is not raw in the sense that it has the same format like stored in DB
    as this is quite different from what one sees in the editor, but from
    an editors perspective that does not matter, so this is considered raw
    """
    CNT_PREPARED = CONTENT / DIR.PREPARED
    """prepared in a file pair - contents as bbcode in one file + metadata"""
    CNT_FINAL = CONTENT / DIR.FINAL
    """the final structure that makes the website"""
