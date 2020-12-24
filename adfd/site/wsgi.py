import logging
import os

import flask
from plumbum.machines import local

from adfd.cnf import INFO, NAME, PATH, SITE
from adfd.process import date_from_timestamp
from adfd.site.navigation import Navigator

app = flask.Flask(__name__, template_folder=PATH.VIEW, static_folder=PATH.STATIC)
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "I only need that for flash()"

LAST_UPDATE: str
NAV = Navigator()


@app.before_first_request
def _before_first_request():
    global LAST_UPDATE
    try:
        LAST_UPDATE = PATH.LAST_UPDATE.read(encoding="utf8")
    except FileNotFoundError:
        LAST_UPDATE = date_from_timestamp()

    NAV.populate()


@app.context_processor
def inject_dict_for_all_templates():
    return dict(NAV=NAV, LAST_UPDATE=LAST_UPDATE, IS_DEV=INFO.IS_DEV_BOX)


@app.route("/")
@app.route("/<path:path>/")
def path_route(path=""):
    bbcode_is_active = False
    if path.startswith(NAME.BBCODE):
        bbcode_is_active = True
        path = path.partition("/")[-1]
    node = NAV.get_node(path)
    node.bbcode_is_active = bbcode_is_active
    node.requestPath = flask.request.path
    # TODO set active path (can be done on node directly)
    return flask.render_template("content-container.html", node=node)


@app.route("/bbcode/article/<topicId>/")
@app.route("/bbcode/article/<path:path>/")
@app.route("/article/<topicId>/")
@app.route("/article/<path:path>/")
def article_route(topicId=None, path=None):
    identifier = topicId or path
    bbcode_is_active = flask.request.path[1:].startswith(NAME.BBCODE)
    try:
        identifier = int(identifier)
    except ValueError:
        pass
    node = NAV.identifierNodeMap[identifier]
    node.bbcode_is_active = bbcode_is_active
    node.requestPath = flask.request.path
    return flask.render_template("content-container.html", node=node)


@app.route("/check/")
def check_route():
    return flask.render_template("check.html", NAV=NAV)


@app.route("/all-articles/")
def articles_all_route():
    return flask.render_template("articles-container.html")


@app.route("/reset")
def reset_route():
    NAV.populate()
    flask.flash("navigator repopulated")
    return flask.redirect(flask.url_for(".path_route", path="/")), 301


def run_devserver():
    app.config.update(DEBUG=True)
    fmt = logging.Formatter(
        "%(asctime)s - %(name)s:%(lineno)s [%(process)d|%(thread)d] %(levelname)s: "
        "%(message)s"
    )
    log = logging.getLogger()
    log.handlers[0].setFormatter(fmt)
    if INFO.IS_DEV_BOX:
        original_render_template = flask.render_template

        def pretty_render_template(template_name_or_list, **context):
            import flask
            from bs4 import BeautifulSoup

            result = original_render_template(template_name_or_list, **context)
            return BeautifulSoup(result, "html5lib").prettify()

        flask.render_template = pretty_render_template
        os.environ["WERKZEUG_DEBUG_PIN"] = "off"
    with local.cwd(PATH.PROJECT):
        host = "0.0.0.0"
        app.logger.info(f"serving on http://{host}:{SITE.APP_PORT}")
        app.run(host=host, port=SITE.APP_PORT)


if __name__ == "__main__":
    run_devserver()
