import logging
import os

from bs4 import BeautifulSoup
from flask import Flask, render_template
from plumbum.machines import local

from adfd.cnf import PATH, SITE, APP
from adfd.site.navigation import Navigator

log = logging.getLogger(__name__)
app = Flask(__name__, template_folder=PATH.VIEW, static_folder=PATH.STATIC)
app.config.update(DEBUG=True)
navigator = Navigator()


@app.context_processor
def inject_dict_for_all_templates():
    return dict(APP=APP)


@app.before_first_request
def populate_navigator():
    navigator.populate()


def render_pretty(template_name_or_list, **context):
    result = render_template(template_name_or_list, **context)
    return BeautifulSoup(result, 'html5lib').prettify()


@app.route('/')
@app.route('/<path:path>/')
def path_route(path=''):
    node = navigator.pathNodeMap["/" + path]
    # TODO set active path
    navigation = navigator.menuAsString
    return render_pretty('page.html', node=node, navigation=navigation)


@app.route('/article/<int:topicId>/')
@app.route('/article/<path:identifier>/')
def article_route(topicId=None, identifier=None):
    if topicId:
        node = navigator.identifierNodeMap[topicId]
    else:
        node = navigator.pathNodeMap["/" + identifier]
    return render_pretty('page.html', node=node)


@app.route('/robots.txt')
def robots_txt_route():
    if os.getenv(APP.ENV_TARGET) != 'live':
        return "User-agent: *\nDisallow: /\n"

    # TODO serve static file with bad robots excluded
    raise NotImplementedError


def run_devserver(projectPath=PATH.PROJECT, port=SITE.APP_PORT):
    with local.cwd(projectPath):
        log.info("serving on http://localhost:%s", port)
        app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    run_devserver()
