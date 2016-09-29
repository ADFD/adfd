import sys

sys.path.insert(0, '/home/adfd/')
from adfd.site.views import app as application

path = '/home/.pyenv/versions/adfd/activate_this.py'
with open(path) as file_:
    exec(file_.read(), dict(__file__=path))
