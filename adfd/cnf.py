import plumbum


class APP:
    PORT = 5000


class PATH:
    PROJECT = plumbum.LocalPath(__file__).dirname.up()
    OUTPUT = PROJECT / 'output'
    SITE = PROJECT / 'adfd' / 'site'
    TEMPLATES = SITE / 'templates'
    FOUNDATION = SITE / 'foundation'
    STATIC = FOUNDATION / 'dist' / 'assets'


class SITE:
    STRUCTURE_TOPIC_ID = 12109
    STRUCTURE_PATH = PATH.SITE / "structure.yml"
    USE_FILE = False
