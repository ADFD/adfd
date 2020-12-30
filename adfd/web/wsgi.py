import os

import flask
from flask import send_from_directory
from plumbum.machines import local

from adfd.cnf import RUNS_ON, NAME, PATH, ADFD
from adfd.model import ArticleContainer
from adfd.web.navigation import Navigator

app = flask.Flask(
    __name__, template_folder=PATH.VIEW_VANILLA, static_folder=PATH.STATIC_FILES
)
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "I only need that for flash()"
NAV = Navigator()


@app.before_first_request
def _before_first_request():
    NAV.populate()


@app.context_processor
def inject_templates_namespace():
    return dict(
        NAV=NAV,
        NAME=NAME,
        IS_DEV=RUNS_ON.DEVBOX,
        IS_FREEZING="FREEZER_DESTINATION" in app.config,
    )


@app.route("/")
@app.route("/<path:path>/")
def path_route(path=""):
    bbcode_is_active = False
    if path.startswith(NAME.BBCODE):
        bbcode_is_active = True
        path = path.partition("/")[-1]
    if path == "nav-populate":
        NAV.populate()
        flask.flash("navigation re-populated")
        return flask.redirect("/")

    node = NAV.get_node(path)
    node.bbcode_is_active = bbcode_is_active
    node.requestPath = flask.request.path
    NAV.activeNode = node
    return flask.render_template("content-container.html", node=node)


@app.route("/favicon.ico")
def favicon():
    # FIXME replace with in-template rel links.
    #  https://www.w3.org/2005/10/howto-favicon
    return send_from_directory(
        directory=PATH.STATIC_FILES,
        filename="favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


def add_dev_routes():
    @app.route("/check/")
    def check_route():
        return flask.render_template("check.html", NAV=NAV)

    @app.route("/dump-db-cache/")
    def dump_db_cache_route():
        from adfd.web.fridge import dump_db_articles_to_file_cache

        dump_db_articles_to_file_cache()
        return flask.redirect(flask.url_for(".path_route", path="/"))

    @app.route("/all-articles/")
    def articles_all_route():
        nodes = [n for n in NAV.allNodes if isinstance(n._container, ArticleContainer)]
        return flask.render_template("article-collection-container.html", nodes=nodes)

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
        NAV.activeNode = node
        node.bbcode_is_active = bbcode_is_active
        node.requestPath = flask.request.path
        return flask.render_template("content-container.html", node=node)


def run_flask_server():
    """All routes defined in here won't be seen by the freezer."""
    app.config.update(DEBUG=True, TESTING=True)
    add_dev_routes()
    replace_render_template()
    if RUNS_ON.DEVBOX:
        os.environ["WERKZEUG_DEBUG_PIN"] = "off"
    host = "localhost"
    app.logger.info(f"serving on http://{host}:{ADFD.APP_PORT}")
    with local.cwd(PATH.PROJECT):
        app.run(host=host, port=ADFD.APP_PORT, debug=True)


def replace_render_template():
    from bs4 import BeautifulSoup

    def pretty_render_template(template_name_or_list, **context):

        result = original_render_template(template_name_or_list, **context)
        return BeautifulSoup(result, "html5lib").prettify()

    original_render_template = flask.render_template
    flask.render_template = pretty_render_template


if __name__ == "__main__":
    run_flask_server()
