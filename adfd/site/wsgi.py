import os

import flask
from flask import send_from_directory
from plumbum.machines import local

from adfd.cnf import INFO, NAME, PATH, SITE
from adfd.model import ArticleContainer
from adfd.site.navigation import Navigator

app = flask.Flask(__name__, template_folder=PATH.VIEW, static_folder=PATH.STATIC)
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "I only need that for flash()"
NAV = Navigator()


@app.before_first_request
def _before_first_request():
    NAV.populate()


@app.context_processor
def inject_dict_for_all_templates():
    return dict(NAV=NAV, NAME=NAME, IS_DEV=INFO.IS_DEV_BOX)


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
        return flask.render_template("content-container.html", node=None)

    node = NAV.get_node(path)
    node.bbcode_is_active = bbcode_is_active
    node.requestPath = flask.request.path
    # TODO set active path (can be done on node directly)
    return flask.render_template("content-container.html", node=node)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        directory=PATH.ROOT_FILES,
        filename="favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


def run_devserver():
    """All routes defined in here won't be seen by the freezer."""
    app.config.update(DEBUG=True, TESTING=True)

    @app.route("/check/")
    def check_route():
        return flask.render_template("check.html", NAV=NAV)

    @app.route("/dump-db-cache/")
    def dump_db_cache_route():
        from adfd.site.fridge import dump_db_articles_to_file_cache

        dump_db_articles_to_file_cache()
        return flask.redirect(flask.url_for(".path_route", path="/"))

    @app.route("/all-articles/")
    def articles_all_route():
        nodes = [n for n in NAV.allNodes if isinstance(n._container, ArticleContainer)]
        return flask.render_template("all-articles-container.html", nodes=nodes)

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

    if INFO.IS_DEV_BOX:
        original_render_template = flask.render_template

        def pretty_render_template(template_name_or_list, **context):
            from bs4 import BeautifulSoup

            result = original_render_template(template_name_or_list, **context)
            return BeautifulSoup(result, "html5lib").prettify()

        flask.render_template = pretty_render_template
        os.environ["WERKZEUG_DEBUG_PIN"] = "off"

    with local.cwd(PATH.PROJECT):
        host = "localhost"
        app.logger.info(f"serving on http://{host}:{SITE.APP_PORT}")
        app.run(host=host, port=SITE.APP_PORT, debug=True)


if __name__ == "__main__":
    run_devserver()
