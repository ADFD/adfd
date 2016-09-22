import logging

from adfd.db.phpbb_classes import Topic
from adfd.exc import TopicDoesNotExist
from flask import render_template, send_from_directory, Flask
from flask.ext.flatpages import FlatPages, Page
from flask.ext.frozen import os
from plumbum import LocalPath
from plumbum.machines import local
from werkzeug.utils import cached_property

from adfd.cnt.metadata import PageMetadata
from adfd.cst import PATH, EXT, APP
from adfd.site.navigation import Navigator, get_yaml_structure

log = logging.getLogger(__name__)


class FlatPagesWithDbAccess(FlatPages):
    def get(self, path, default=None):
        try:
            topic = Topic(int(path))
            return NoRenderPageWithAdfdMetadata(path, topic.md, topic.html)
        except TopicDoesNotExist:
            return None

        except ValueError:
            return super().get(path, default=None)


class NoRenderPageWithAdfdMetadata(Page):
    def __init__(self, path, meta, body):
        super().__init__(path, meta, body, None)

    @cached_property
    def meta(self):
        return self._meta

    @cached_property
    def html(self):
        return self.body


class NoRenderAdfdMetadataFlatPages(FlatPagesWithDbAccess):
    def _parse(self, content, path):
        mdPath = (LocalPath(self.root) / path).with_suffix(EXT.META)
        meta = PageMetadata(path=mdPath)
        assert meta.exists, meta._path
        return NoRenderPageWithAdfdMetadata(path, meta, content)

app = Flask(
    __name__, template_folder=PATH.TEMPLATES, static_folder=PATH.STATIC,
    # static_url_path='/assets'
)

pages = NoRenderAdfdMetadataFlatPages(app)

# TODO breadcrumbs
navigator = Navigator(get_yaml_structure())


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

    navigation = navigator.get_navigation(path)
    indexPath = 'index' if not path else "%s/index" % path
    page = pages.get_or_404(indexPath)
    return render_template('page.html', page=page, navigation=navigation)


@app.route('/article/<int:topicId>/')
def article(topicId):
    page = pages.get_or_404(topicId)
    return render_template('page.html', page=page)


@app.route('/tag/<string:tag>/')
def tag(tag):
    tagged = [p for p in pages if tag in p.meta.get('tags', [])]
    return render_template('tag.html', pages=tagged, tag=tag)


def run_devserver(projectPath=PATH.PROJECT, port=APP.PORT):
    with local.cwd(projectPath):
        log.info("serving on http://localhost:%s", port)
        app.run(port=port)
