import json
import logging

from adfd.cnf import PATH, EXT
from adfd.model import DbArticleContainer
from adfd.site.navigation import Navigator

log = logging.getLogger(__name__)


def dump_db_articles_to_db_cache():
    n = Navigator()
    PATH.DB_CACHE.delete()
    PATH.DB_CACHE.mkdir()
    for node in n.allNodes:
        container = node._container
        if not isinstance(container, DbArticleContainer):
            log.debug(f"skip {container}")
            continue

        assert isinstance(container, DbArticleContainer)
        base_path = PATH.DB_CACHE / node.identifier
        base_path.mkdir()
        print(f"dump {container} to {base_path}")
        container_md_path = base_path / f"{node.identifier}{EXT.MD}"
        container_md_path.write(json.dumps(container._attrs_for_md_cache(), indent=4))
        for idx, post in enumerate(container._posts):
            post_path = base_path / post.id
            post_path = post_path.with_suffix(EXT.BBCODE)
            post_path.write(post.content)
            post_md_path = post_path.with_suffix(EXT.MD)
            post_md_path.write(
                json.dumps(post._attrs_for_cache(isFirstPost=idx == 0), indent=4)
            )


if __name__ == "__main__":
    dump_db_articles_to_db_cache()
