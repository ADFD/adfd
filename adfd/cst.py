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


class DIR(object):
    RAW = 'raw'
    PREPARED = 'prepared'
    HTML = 'html'
    STATIC = 'static'


class PATH(object):
    PROJECT = plumbum.LocalPath(__file__).up().up(2) / 'adfd'
    CODE = PROJECT / 'adfd'
    CONTENT = CONTENT_ROOT
    TEST_DATA = CODE / 'tests' / 'data'
