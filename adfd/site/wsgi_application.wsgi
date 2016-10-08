import sys

sys.path.insert(0, '/home/adfd/')
# noinspection PyUnresolvedReferences
from adfd.site.controller import app as application
from adfd.cnf import VIRTENV

with open(VIRTENV.ACTIVATE_THIS_SCRIPT) as file_:
    exec(file_.read(), dict(__file__=VIRTENV.ACTIVATE_THIS_SCRIPT))
