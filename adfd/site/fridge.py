import logging
import shutil

import flask_frozen
from plumbum import local, LocalPath

from adfd.cnf import PATH, INFO, TARGET
from adfd.site.wsgi import NAV, app

log = logging.getLogger(__name__)


class Fridge:
    def __init__(self):
        self.clean()
        self.configure_app_for_freezing()
        self.freezer = flask_frozen.Freezer(app)
        self.freezer.register_generator(path_route)

    def freeze(self):
        self.freeze_urls()
        self.deliver_static_root_files()
        self.remove_clutter()
        self.write_bbcode_sources()
        if not INFO.IS_DEV_BOX:
            self.fix_staging_paths()
        print(f"ADFD site successfully frozen at {PATH.RENDERED}!")

    @staticmethod
    def clean():
        shutil.rmtree(PATH.RENDERED, ignore_errors=True)
        PATH.RENDERED.mkdir()

    @classmethod
    def configure_app_for_freezing(cls):
        app.config.update(
            FREEZER_DESTINATION=PATH.RENDERED,
            FREEZER_RELATIVE_URLS=True,
            FREEZER_REMOVE_EXTRA_FILES=True,
            FREEZER_DESTINATION_IGNORE=[".git*", "*.idea"],
        )

    def freeze_urls(self):
        with local.cwd(PATH.PROJECT):
            log.info(f"freezing {app.config}")
            frozenURLs = self.freezer.freeze()
        log.info("frozen urls are:\n%s", "\n".join(frozenURLs))

    @classmethod
    def deliver_static_root_files(cls):
        for path in [p for p in PATH.ROOT_FILES.walk() if p.is_file()]:
            path.copy(PATH.RENDERED)

    @classmethod
    def remove_clutter(cls):
        for rel_path in [
            "static/_root",
            "static/content",
        ]:
            assert not rel_path.startswith("/"), rel_path
            path = PATH.RENDERED / rel_path
            assert path.exists(), path
            log.info(f"remove clutter: {path}")
            path.delete()

    # FIXME adapt to use db-cache
    @classmethod
    def write_bbcode_sources(cls):
        PATH.BBCODE_BACKUP.mkdir()
        for node in NAV.allNodes:
            if not node.hasArticle:
                continue

            if isinstance(node.identifier, str):
                identifier = LocalPath(node.identifier).name
            else:
                identifier = "%05d.bbcode" % node.identifier
            path = PATH.BBCODE_BACKUP / identifier
            log.info("save sources %s", node.relPath)
            path.write(node._bbcode, encoding="utf8")

    @classmethod
    def fix_staging_paths(cls):
        log.warning("prefix %s - changing links", TARGET.PREFIX_STR)
        for path in cls.get_all_page_paths():
            cnt = path.read(encoding="utf8")
            cnt = cnt.replace('href="/', 'href="/%s/' % TARGET.PREFIX_STR)
            with open(path, "w", encoding="utf8") as f:
                f.write(cnt)

    @classmethod
    def get_all_page_paths(cls):
        return [p for p in PATH.RENDERED.walk() if p.endswith("index.html")]


def path_route():  # same name as route function in wsgi.py
    if not NAV.isPopulated:
        NAV.populate()
    for path in NAV.pathNodeMap:
        log.info(path)
        yield {"path": path}


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    Fridge().freeze()
