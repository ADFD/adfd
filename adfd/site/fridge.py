import logging
import os
import shutil
import tempfile

import flask_frozen
from plumbum import local, LocalPath

from adfd.cnf import NAME, PATH, INFO, TARGET
from adfd.process import date_from_timestamp
from adfd.site.wsgi import NAV, app

log = logging.getLogger(__name__)


class AdfdFreezer:
    @classmethod
    def freeze(cls):
        buildPath = tempfile.mkdtemp()
        app.config.update(
            FREEZER_DESTINATION=PATH.RENDERED,
            FREEZER_RELATIVE_URLS=True,
            FREEZER_REMOVE_EXTRA_FILES=True,
            FREEZER_DESTINATION_IGNORE=[".git*", "*.idea"],
        )
        freezer = flask_frozen.Freezer(app)
        freezer.register_generator(path_route)
        with local.cwd(PATH.PROJECT):
            log.info("freezing %s", freezer)
            with open(PATH.LAST_UPDATE, "w", encoding="utf") as f:
                f.write(date_from_timestamp())
            seenUrls = freezer.freeze()
            log.info("frozen urls are:\n%s", "\n".join(seenUrls))
        cls.copytree(buildPath, PATH.RENDERED)
        cls.deliver_static_root_files()
        cls.remove_clutter()
        cls.write_bbcode_sources()
        if not INFO.IS_DEV_BOX:
            cls.fix_staging_paths()
        print("ADFD site successfully frozen!")

    @classmethod
    def deliver_static_root_files(cls):
        for path in [p for p in PATH.ROOT_FILES.walk() if p.is_file()]:
            path.copy(PATH.RENDERED)

    @classmethod
    def remove_clutter(cls):
        for path in [
            PATH.RENDERED / "static/_root",
            PATH.RENDERED / "reset",
        ]:
            path.delete()

    @classmethod
    def copytree(cls, src, dst, symlinks=False, ignore=None):
        if not os.path.exists(dst):
            os.makedirs(dst)
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                cls.copytree(s, d, symlinks, ignore)
            else:
                if (
                    not os.path.exists(d)
                    or os.stat(s).st_mtime - os.stat(d).st_mtime > 1
                ):
                    shutil.copy2(s, d)

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


def path_route():  # looks like the name is a must here
    if not NAV.isPopulated:
        NAV.populate()
    for path in NAV.pathNodeMap:
        for prefix in ["", NAME.BBCODE]:
            log.info(f"yield {path}")
            yield {"path": path}

            if prefix:
                prefixedPath = f"/{NAME.BBCODE}"
                if path != "/":
                    prefixedPath += path
                log.info(f"yield {prefixedPath}")
                yield {"path": prefixedPath}


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    AdfdFreezer.freeze()
