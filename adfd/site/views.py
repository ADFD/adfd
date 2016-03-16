import logging

from flask import render_template, send_from_directory, Flask
from flask.ext.frozen import os
from plumbum.machines import local

from adfd.cst import PATH, EXT, APP
from adfd.site.structure import Navigator
from adfd.site.lib import NoRenderAdfdMetadataFlatPages


log = logging.getLogger(__name__)


app = Flask(
    __name__,
    template_folder=PATH.TEMPLATES,
    static_folder=PATH.STATIC,
    # static_url_path='/assets'
)
"""":type: Flask"""


pages = NoRenderAdfdMetadataFlatPages(app)
"""":type: FlatPages"""


navigator = Navigator()
"""":type: Navigator"""


def config_app(appToCOnfig, pagesToConfig):
    appToCOnfig.root_path = str(PATH.PROJECT)
    appToCOnfig.config.update(
        DEBUG=True,
        FLATPAGES_ROOT=str(PATH.PAGES),
        FLATPAGES_EXTENSION=EXT.OUT,
        FLATPAGES_AUTO_RELOAD=True,
        FREEZER_DESTINATION=str(PATH.OUTPUT),
        FREEZER_RELATIVE_URLS=True)
    pagesToConfig.init_app(app)
    return appToCOnfig


config_app(app, pages)


@app.route('/')
@app.route('/<path:path>/')
def page(path=''):
    for specialDir in ['js', 'stylesheets']:
        if path.startswith(specialDir):
            return send_from_directory(specialDir, os.path.basename(path))

    navigation = navigator.generate_navigation(path)
    indexPath = 'index' if not path else "%s/index" % (path)
    page = pages.get_or_404(indexPath)
    return render_template('page.html', page=page, navigation=navigation)


@app.route('/tag/<string:tag>/')
def tag(tag):
    tagged = [p for p in pages if tag in p.meta.get('tags', [])]
    return render_template('tag.html', pages=tagged, tag=tag)


def run_devserver(projectPath=PATH.PROJECT, port=APP.PORT):
    with local.cwd(projectPath):
        log.info("serving on http://localhost:%s", port)
        app.run(port=port)


if __name__ == '__main__':
    run_devserver()
