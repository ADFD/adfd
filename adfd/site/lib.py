import logging

from flask.ext.flatpages import FlatPages, Page
from plumbum import LocalPath
from werkzeug.utils import cached_property

from adfd.cnt.massage import PageMetadata
from adfd.cst import EXT

log = logging.getLogger(__name__)


class NoRenderPageWithAdfdMetadata(Page):
    @cached_property
    def meta(self):
        return self._meta

    @cached_property
    def html(self):
        return self.body


class NoRenderAdfdMetadataFlatPages(FlatPages):
    def _parse(self, content, path):
        mdPath = (LocalPath(self.root) / path).with_suffix(EXT.META)
        meta = PageMetadata(path=mdPath)
        assert meta.exists, meta._path
        meta.relPath = path  # FIXME is that used? Where?
        return NoRenderPageWithAdfdMetadata(path, meta, content, None)
