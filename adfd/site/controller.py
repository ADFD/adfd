import logging
import os
import socket

from bs4 import BeautifulSoup
from flask import Flask, request, render_template, flash, redirect, url_for
from plumbum.machines import local

from adfd.cnf import PATH, SITE, APP, NAME
from adfd.site.navigation import Navigator

log = logging.getLogger(__name__)
app = Flask(__name__, template_folder=PATH.VIEW, static_folder=PATH.STATIC)
app.secret_key = "I actually don't need a secret key"
app.config['SESSION_TYPE'] = 'filesystem'
app.config.update(DEBUG=True)
navigator = Navigator()
LAST_UPDATE = None


@app.context_processor
def inject_dict_for_all_templates():
    return dict(APP=APP, VERSION=LAST_UPDATE)


@app.before_first_request
def populate_navigator():
    if not navigator.pathNodeMap:
        navigator.populate()
    global LAST_UPDATE
    if not LAST_UPDATE:
        LAST_UPDATE = PATH.LAST_UPDATE.read(encoding='utf8')
        # with local.cwd(PATH.RENDERED):
        #     ts = local['git']('show', '-s', '--format=%ct', 'HEAD')
        #     LAST_UPDATE = date_from_timestamp(float(ts))


def render_pretty(template_name_or_list, **context):
    result = render_template(template_name_or_list, **context)
    return BeautifulSoup(result, 'html5lib').prettify()


@app.route('/')
@app.route('/<path:path>/')
def path_route(path=''):
    bbcodeIsActive = False
    if path.startswith(NAME.BBCODE):
        bbcodeIsActive = True
        path = path.partition("/")[-1]
    node = navigator.pathNodeMap["/" + path]
    node.article.bbcodeIsActive = bbcodeIsActive
    node.article.requestPath = request.path
    # TODO set active path (can be done on node directly)
    navigation = navigator.menuAsString
    return render_pretty('page.html', navigation=navigation, node=node)


@app.route('/article/<int:topicId>/')
@app.route('/article/<path:identifier>/')
def article_route(topicId=None, identifier=None):
    if topicId:
        node = navigator.identifierNodeMap[topicId]
    else:
        node = navigator.pathNodeMap["/" + identifier]
    return render_pretty('page.html', node=node, article=node.article)


@app.route('/reset')
def reset_route():
    navigator.populate()
    flash("navigator repopulated")
    return redirect(url_for(".path_route", path="/"))


def run_devserver(projectPath=PATH.PROJECT, port=SITE.APP_PORT):
    if socket.gethostname() == '1bo':
        os.environ['WERKZEUG_DEBUG_PIN'] = 'off'
    with local.cwd(projectPath):
        log.info("serving on http://localhost:%s", port)
        app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    run_devserver()
