import sys

sys.path.insert(0, '/home/adfd/')

# noinspection PyUnresolvedReferences
from adfd.site.views import app as application

activate_this = '/home/.pyenv/versions/adfd'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
