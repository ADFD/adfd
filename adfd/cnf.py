import plumbum


class APP:
    PORT = 5000


class PATH:
    PROJECT = plumbum.LocalPath(__file__).dirname.up()
    SITE = PROJECT / 'adfd' / 'site'
    FOUNDATION = SITE / 'foundation'
    STATIC = FOUNDATION / 'dist' / 'assets'
    TEMPLATES = SITE / 'templates'
    FROZEN = PROJECT / '.frozen'


class SITE:
    STRUCTURE_TOPIC_ID = 12109
    STRUCTURE_PATH = PATH.SITE / "structure.yml"
    USE_FILE = False
