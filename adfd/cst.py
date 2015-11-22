import re
import tempfile

import plumbum

try:
    from adfd.db.local_settings import _DB_URL, _CONTENT_ROOT
except ImportError:
    _DB_URL = "mysql://user:password@localhost/dbname"
    _CONTENT_ROOT = tempfile.gettempdir()


DB_URL = _DB_URL + '?charset=utf8'
"""Important! See: http://goo.gl/rGuQey"""
CONTENT_ROOT = plumbum.LocalPath(_CONTENT_ROOT)


class SLUG(object):
    PUNCT = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')


class EXT(object):
    BBCODE = '.bbcode'
    META = '.meta'


class FILENAME(object):
    CONTENT = 'content' + EXT.BBCODE
    META = 'meta' + EXT.META


class DIR(object):
    TOPICS = 'topics'
    RAW = 'raw'
    """exported bbcode like it looks when edited - each posts in a single file.

    It is not raw in the sense that it has the same format like stored in DB
    as this is quite different from what one sees in the editor, but from
    an editors perspective that does not matter, so this is considered raw
    """
    PREPARED = 'prepared'
    """prepared in a single file - still bbcode"""
    HTML = 'html'
    """the resulting html"""
    STATIC = 'static'


class PATH(object):
    PROJECT = plumbum.LocalPath(__file__).up().up(2) / 'adfd'
    TEST_DATA = PROJECT / 'adfd' / 'tests' / 'data'
    CONTENT = CONTENT_ROOT
    TOPICS = CONTENT / DIR.TOPICS
    STATIC = CONTENT / DIR.STATIC
