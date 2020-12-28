import json
import logging
import shutil
from typing import List

import flask_frozen
from plumbum import local, SshMachine, LocalPath, ProcessExecutionError

from adfd import configure_logging
from adfd.cnf import PATH, INFO, TARGET, EXT, NAME
from adfd.db.schema import PhpbbAttachment
from adfd.model import DbArticleContainer
from adfd.site.wsgi import NAV, app

log = logging.getLogger(__name__)


class Fridge:
    def __init__(self):
        self.clean()
        self.configure_app_for_freezing()
        self.freezer = flask_frozen.Freezer(app)
        self.freezer.register_generator(path_route)

    def freeze(self):
        dump_db_articles_to_file_cache()
        self.freeze_urls()
        self.deliver_static_root_files()
        self.deliver_cached_attachments()
        if not INFO.IS_DEV_BOX:
            self.fix_staging_paths()
        print(f"ADFD site successfully frozen at {PATH.FROZEN}!")

    @staticmethod
    def clean():
        shutil.rmtree(PATH.FROZEN, ignore_errors=True)
        PATH.FROZEN.mkdir()

    @classmethod
    def configure_app_for_freezing(cls):
        app.config.update(
            FREEZER_DESTINATION=PATH.FROZEN,
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
        for path in [p for p in PATH.SITE_REPO.list() if p.is_file()]:
            path.copy(PATH.FROZEN)

    @classmethod
    def deliver_cached_attachments(cls):
        """copy all attachments to static attachments folder.

        This has a pretty ugly restriction, but currently this is the easiest
        way to implement it: all attachment filenames need to be globally unique.

        The reason why it is this way, is that the bbcode parser only has access to
        the filename and renders this with the attachment path. Anything else would mean
        that the renderer would need to know which post the file is attached to, this
        would be a big change, so the globally uniqueness requirement seems less bad.
        """
        PATH.RENDERED_ATTACHMENTS.delete()
        PATH.RENDERED_ATTACHMENTS.mkdir()
        paths: List[LocalPath] = PATH.DB_CACHE // "**/attachments/*"
        for attachment in paths:
            dst = PATH.RENDERED_ATTACHMENTS / attachment.name
            try:
                attachment.copy(dst, overwrite=False)
            except TypeError as e:
                if "File exists" not in e.args[0]:
                    raise

                log.warning(f"[IGNORE] duplicate {attachment}")
                duplicates = PATH.DB_CACHE // f"**/{NAME.ATTACHMENTS}/{attachment.name}"
                raise Exception(f"duplicate filename: {duplicates}")

        # TODO when this is in production: fail if any *.missing.txt attachment present

    @classmethod
    def fix_staging_paths(cls):
        log.warning("prefix %s - changing links", TARGET.PREFIX_STR)
        all_page_paths = [p for p in PATH.FROZEN.walk() if p.endswith("index.html")]
        for path in all_page_paths:
            cnt = path.read(encoding="utf8")
            cnt = cnt.replace('href="/', 'href="/%s/' % TARGET.PREFIX_STR)
            with open(path, "w", encoding="utf8") as f:
                f.write(cnt)


def path_route():  # same name as route function in wsgi.py
    if not NAV.isPopulated:
        NAV.populate()
    for path in NAV.pathNodeMap:
        log.info(path)
        yield {"path": path}


def dump_db_articles_to_file_cache():
    """This creates a structure that CachedArticleContainer can read.

    This also serves as a way to see how articles changed over time, as they will
    be committed to the same repos as the rendered page.
    """
    PATH.DB_CACHE.delete()
    PATH.DB_CACHE.mkdir()
    NAV.populate()
    for node in NAV.allNodes:
        container = node._container
        if type(container) != DbArticleContainer:  # no subclasses wanted here!
            log.info(f"skip {container}")
            continue

        post_base_path = PATH.DB_CACHE / node.identifier
        post_base_path.mkdir()
        container_md_path = post_base_path / f"{node.identifier}{EXT.MD}"
        container_md_path.write(json.dumps(container._attrs_for_md_cache(), indent=4))
        for idx, post in enumerate(container._posts):
            post_path = post_base_path / post.id
            post_path = post_path.with_suffix(EXT.BBCODE)
            post_path.write(post.content)
            post_md_path = post_path.with_suffix(EXT.MD)
            post_md_path.write(
                json.dumps(post._attrs_for_cache(isFirstPost=idx == 0), indent=4)
            )
            if post.attachments:
                fetch_attachments(post.attachments, post_base_path)
        log.info(f"dumped {container} to {post_base_path}")


def fetch_attachments(attachments: List[PhpbbAttachment], base_path: LocalPath):
    attachments_path = base_path / "attachments"
    attachments_path.mkdir()
    with SshMachine(TARGET.DOMAIN) as remote:
        remote_files_path = remote.path("~", "www", "austausch", "files")
        for attachment in attachments:
            src = remote_files_path / attachment.physical_filename
            dst = attachments_path / attachment.real_filename
            log.info(f"{src} -> {dst}")
            try:
                remote.download(src, dst)
            except ProcessExecutionError as e:
                if "No such file or directory" not in e.stderr:
                    raise
                log.warning(f"[IGNORE] image not found: {src}")
                dst.with_suffix(".missing.txt").write(attachment.physical_filename)


if __name__ == "__main__":
    configure_logging("WARNING")
    Fridge().freeze()
