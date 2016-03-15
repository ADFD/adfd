import logging

from flask.ext.flatpages import FlatPages, Page
from plumbum import LocalPath, local
from werkzeug.utils import cached_property

from adfd.content import PageMetadata
from adfd.conf import EXT

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


def deploy(outputPath, target):
    """Synchronize static website contents with a remote target

    :type outputPath: LocalPath or str
    :type target: _Target
    """
    """sycnhronize static website with target"""
    rsync = local['rsync']
    args = ('-av', str(outputPath) + '/', target.path)
    log.info('run rsync%s', args)
    rsyncOutput = rsync(*args)
    log.info("rsync result:\n%s", rsyncOutput)
