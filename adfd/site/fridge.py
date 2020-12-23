import logging

from adfd.cnf import NAME
from adfd.site.wsgi import NAV

log = logging.getLogger(__name__)


def path_route():
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
    for r in path_route():
        print(r)
