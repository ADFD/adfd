import re
import plumbum

try:
    from adfd.db.cred import _DB_URL
except ImportError:
    _DB_URL = "mysql://user:password@localhost/dbname"


DB_URL = _DB_URL + '?charset=utf8'
"""Important! See: http://goo.gl/rGuQey"""

HERE = plumbum.LocalPath(__file__).up()


class SLUG(object):
    PUNCT = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')


class PATH(object):
    PROJECT = HERE.up(2) / 'adfd'
    IMPORTS = PROJECT / 'adfd' / 'content' / 'imported'
    TEST_DATA = PROJECT / 'adfd' / 'tests' / 'data'
