import logging

from flask import render_template, send_from_directory, Flask
from flask.ext.frozen import os
from plumbum.machines import local
from werkzeug.utils import cached_property

from adfd.cnf import PATH, APP
from adfd.db.model import Topic
from adfd.site.navigation import Navigator, get_yaml_structure

log = logging.getLogger(__name__)

# TODO ever needed on server? static_url_path='/assets'
app = Flask(
    __name__, template_folder=PATH.TEMPLATES, static_folder=PATH.STATIC)
# FIXME Why do I set the root path to the very root? Needed?
app.root_path = str(PATH.PROJECT)
app.config.update(
    DEBUG=True,
    FREEZER_DESTINATION=str(PATH.FROZEN),
    FREEZER_RELATIVE_URLS=True)

navigator = Navigator(get_yaml_structure())


class Page(object):
    def __init__(self, path, meta, html):
        self.path = path
        self.html = html
        self.meta = meta

    def __repr__(self):
        return '<Page %r>' % self.path

    @cached_property
    def html(self):
        return self.html

    def __html__(self):
        """In a template: ``{{ page }}`` == ``{{ page.html|safe }}``."""
        return self.html

    def __getitem__(self, name):
        """Shortcut for accessing metadata.

        ``page['title']`` == ``{{ page.title }}`` == ``page.meta['title']``.
        """
        return self.meta[name]


@app.route('/')
@app.route('/<path:path>/')
def page(path=''):
    for specialDir in ['js', 'stylesheets']:
        if path.startswith(specialDir):
            return send_from_directory(specialDir, os.path.basename(path))

    path = "/" + path  # FIXME Why is this necessary?
    navigation = navigator.get_navigation(path)
    topic = navigator.pathNodeMap[path].topic
    page = Page(path, topic.md, topic.html)
    return render_template('page.html', page=page, navigation=navigation)


@app.route('/article/<int:topicId>/')
def article(topicId):
    topic = Topic(int(topicId))
    page = Page(topicId, topic.md, topic.html)
    return render_template('page.html', page=page)


@app.route('/robots.txt')
def robots_txt():
    if os.getenv('APP_TARGET') != 'live':
        return "User-agent: *\nDisallow: /\n"

    # TODO exclude bad robots
    return "User-agent: *\nDisallow:\n"


def run_devserver(projectPath=PATH.PROJECT, port=APP.PORT):
    with local.cwd(projectPath):
        log.info("serving on http://localhost:%s", port)
        app.run(port=port)


if __name__ == '__main__':
    run_devserver()
