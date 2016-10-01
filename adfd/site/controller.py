import logging

from adfd.cnf import PATH, SITE, APP
from adfd.site.navigation import Navigator
from bs4 import BeautifulSoup
from flask import render_template, send_from_directory, Flask
from flask.ext.frozen import os
from plumbum.machines import local

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

navigator = None
""":type: Navigator"""


@app.before_first_request
def before_first_request():
    global navigator
    if not navigator:
        navigator = Navigator()


@app.context_processor
def inject_dict_for_all_templates():
    return dict(APP=APP)


# TODO add sourcelink and show bbcode
# TODO add link to original post on ADFD
# TODO add showing of meta data info (authors, date, etc)

@app.route('/')
@app.route('/<path:path>/')
def path_route(path=''):
    # fixme adapt to semantic UI
    for specialDir in ['js', 'stylesheets']:
        if path.startswith(specialDir):
            return send_from_directory(specialDir, os.path.basename(path))

    node = navigator.pathNodeMap[path]
    navigation = navigator.menuAsString
    html = render_template('page.html', node=node, navigation=navigation)
    # html = BeautifulSoup(html, 'html.parser').prettify()
    return html


@app.route('/article/<int:topicId>/')
@app.route('/article/<path:identifier>/')
def article(topicId=None, identifier=None):
    raise Exception("%s, %s" % (topicId, identifier))
    # todo get Node from identifier or topicId
    # page = Page(topicId, topic.md, topic.html)
    # return render_template('page.html', page=page)
    pass

# todo /favicon.ico


@app.route('/robots.txt')
def robots_txt():
    if os.getenv('APP_TARGET') != 'live':
        return "User-agent: *\nDisallow: /\n"

    # TODO exclude bad robots
    return "User-agent: *\nDisallow:\n"


def run_devserver(projectPath=PATH.PROJECT, port=SITE.APP_PORT):
    with local.cwd(projectPath):
        log.info("serving on http://localhost:%s", port)
        app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    run_devserver()
