import logging
import os
import socket

from adfd.cnf import PATH, SITE, APP, NAME
from adfd.site.navigation import Navigator
from adfd.utils import date_from_timestamp
from flask import Flask, render_template, url_for
from flask import request, flash, redirect
from plumbum.machines import local

log = logging.getLogger(__name__)

app = Flask(__name__, template_folder=PATH.VIEW, static_folder=PATH.STATIC)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = "I only need that for flash()"

LAST_UPDATE = None
IS_DEV = None
IS_FREEZING = None
NAV = Navigator()


# TODO activate if formatted HTML is wanted
# def render_template(template_name_or_list, **context):
#     from bs4 import BeautifulSoup
#     result = render_template(template_name_or_list, **context)
#     return BeautifulSoup(result, 'html5lib').prettify()


@app.context_processor
def inject_dict_for_all_templates():
    return dict(APP=APP, NAV=NAV, VERSION=LAST_UPDATE, IS_DEV=IS_DEV)


@app.before_first_request
def _before_first_request():
    global LAST_UPDATE
    try:
        LAST_UPDATE = PATH.LAST_UPDATE.read(encoding='utf8')
    except FileNotFoundError:
        LAST_UPDATE = date_from_timestamp()

    global IS_DEV
    # Todo activate condition when main dev phase is over
    IS_DEV = True  # 'FREEZER_DESTINATION' not in app.config
    global IS_FREEZING
    IS_FREEZING = "FREEZER_DESTINATION" in app.config
    global NAV
    NAV.populate()


@app.route('/')
@app.route('/<path:path>/')
def path_route(path=''):
    bbcodeIsActive = False
    if path.startswith(NAME.BBCODE):
        bbcodeIsActive = True
        path = path.partition("/")[-1]
    node = NAV.get_node(path)
    node.bbcodeIsActive = bbcodeIsActive
    node.requestPath = request.path
    # TODO set active path (can be done on node directly)
    return render_template('content-container.html', node=node)


@app.route('/bbcode/article/<topicId>/')
@app.route('/bbcode/article/<path:path>/')
@app.route('/article/<topicId>/')
@app.route('/article/<path:path>/')
def article_route(topicId=None, path=None):
    identifier = topicId or path
    bbcodeIsActive = False
    if request.path[1:].startswith(NAME.BBCODE):
        bbcodeIsActive = True
    try:
        identifier = int(identifier)
    except ValueError:
        pass
    node = NAV.identifierNodeMap[identifier]
    node.bbcodeIsActive = bbcodeIsActive
    node.requestPath = request.path
    return render_template('content-container.html', node=node)


@app.route('/check/')
def check_route():
    return render_template('check.html', NAV=NAV)


@app.route('/all-articles/')
def articles_all_route():
    return render_template('articles-container.html')


@app.route('/reset')
def reset_route():
    if IS_DEV and not IS_FREEZING:
        NAV.populate()
        flash("navigator repopulated")
    return redirect(url_for(".path_route", path="/")), 301


def run_devserver(projectPath=PATH.PROJECT, port=SITE.APP_PORT):
    app.config.update(DEBUG=True)
    if socket.gethostname() == '1bo':
        os.environ['WERKZEUG_DEBUG_PIN'] = 'off'
    with local.cwd(projectPath):
        log.info("serving on http://localhost:%s", port)
        app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    run_devserver()
