from adfd.cnf import PATH
from adfd.model import CategoryNode
from adfd.site.navigation import Navigator


def dump_db_articles_to_db_cache():
    n = Navigator()
    PATH.DB_CACHE.delete()
    PATH.DB_CACHE.mkdir()
    for x in n.allNodes:
        path = (PATH.DB_CACHE / x.identifier).with_suffix(".bbcode")
        if isinstance(x, CategoryNode) or not isinstance(x.identifier, int):
            continue
        print(f"dumping {x.identifier} to {path}")
        path.write(x._bbcode)


if __name__ == "__main__":
    dump_db_articles_to_db_cache()
