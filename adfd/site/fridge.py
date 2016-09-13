import logging

from flask.ext.frozen import Freezer
from plumbum.machines import local

from adfd.cst import PATH, TARGET
from adfd.site.lib import deploy
from adfd.site.views import app, navigator


log = logging.getLogger(__name__)


freezer = Freezer(app)


@freezer.register_generator
def page():
    for url in navigator.allUrls:
        yield {'path': url}


def freeze(pathPrefix=None):
    """:param pathPrefix: for freezing when it's served not from root"""
    log.info("freeze in: %s", PATH.PROJECT)
    with local.cwd(PATH.PROJECT):
        log.info("freezing %s", freezer)
        seenUrls = freezer.freeze()
        log.info("frozen urls are:\n%s", '\n'.join(seenUrls))
    if pathPrefix:
        for url in seenUrls:
            if url.endswith('/'):
                filePath = PATH.OUTPUT / url[1:] / 'index.html'
                with open(filePath) as f:
                    content = f.read()
                    content = content.replace(
                        'href="/', 'href="/%s/' % (pathPrefix))
                with open(filePath, 'w') as f:
                    f.write(content)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    target = TARGET.get(TARGET.TEST)
    freeze(target.prefix)
    deploy(PATH.OUTPUT, target)
