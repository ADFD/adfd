import logging

from adfd.cnf import NAME
from adfd.site.controller import navigator

log = logging.getLogger(__name__)


def path_route():
    for path, node in navigator.pathNodeMap.items():
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
