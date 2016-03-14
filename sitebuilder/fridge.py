import logging

from flask.ext.frozen import Freezer
from plumbum.machines import local

from sitebuilder.conf import PATH, NAME, TARGET
from sitebuilder.lib import deploy
from sitebuilder.views import app


log = logging.getLogger(__name__)


freezer = Freezer(app)


@freezer.register_generator
def page():
    from sitebuilder.views import navigator
    for url in navigator.allUrls:
        yield {'path': url}


def freeze(projectPath=PATH.PROJECT, pathPrefix=None):
    """

    :param projectPath: root of the project
    :param pathPrefix: for freezing when it's served not from root
    """
    log.info("freeze in: %s", projectPath)
    with local.cwd(projectPath):
        log.info("freezing %s", freezer)
        seenUrls = freezer.freeze()
        log.info("frozen urls are:\n%s", '\n'.join(seenUrls))
    if pathPrefix:
        for url in seenUrls:
            if url.endswith('/'):
                filePath = projectPath / NAME.OUTPUT / url[1:] / 'index.html'
                with open(filePath) as f:
                    content = f.read()
                    content = content.replace(
                        'href="/', 'href="/%s/' % (pathPrefix))
                with open(filePath, 'w') as f:
                    f.write(content)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    target = TARGET.get(TARGET.TEST)
    freeze(pathPrefix=target.prefix)
    deploy(PATH.PROJECT / NAME.OUTPUT, target)
