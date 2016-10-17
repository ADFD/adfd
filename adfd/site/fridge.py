import logging

from adfd.cnf import NAME
from adfd.site.controller import NAV
from adfd.utils import configure_logging

log = logging.getLogger(__name__)


def path_route():
    if not NAV.isPopulated:
        NAV.populate()
    for path, node in NAV.pathNodeMap.items():
        if not node.hasContent:
            log.info("nothing to render for %s -> %r", path, node)
            continue

        for prefix in ['', NAME.BBCODE]:
            log.info("yield %s", path)
            yield {'path': path}

            if prefix:
                prefixedPath = "/%s" % NAME.BBCODE
                if path != "/":
                    prefixedPath += path
                log.info("yield %s", prefixedPath)
                yield {'path': prefixedPath}


if __name__ == '__main__':
    configure_logging("INFO")
    for r in path_route():
        print(r)
