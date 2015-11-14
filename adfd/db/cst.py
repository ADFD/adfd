import re
import plumbum

try:
    from adfd.db.cred import DB_URL
except ImportError:
    DB_URL = "mysql://user:password@localhost/dbname"
    raise Exception("Need DB_URL (like: %s)" % (DB_URL))


HERE = plumbum.LocalPath(__file__).up()
PROJECT_PATH = HERE.up(2) / 'adfd'


class ENC(object):
    IN = 'cp1252'  # used to decode input to bytes
    OUT = 'utf-8'  # used to encode bytes
    ALL = [IN, OUT]


class SLUG(object):
    PUNCT = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')


class SITE(object):
    EXPORT_PATH = PROJECT_PATH / 'content' / 'imported'
