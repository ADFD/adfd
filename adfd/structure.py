import json
import logging
from collections import OrderedDict

from plumbum import LocalPath

from adfd.content import Metadata
from adfd.cst import EXT


log = logging.getLogger(__name__)


class Structure(object):
    """fetch structure from meta data in finalized files"""
    def __init__(self, rootPath, structureDstPath):
        self.rootPath = LocalPath(rootPath)
        self.structureDstPath = structureDstPath

    def dump_structure(self):
        pageMap = self.create_page_map(self.rootPath)
        self.jsonify_structure(pageMap)

    @classmethod
    def create_page_map(cls, rootPath):
        pages = OrderedDict()
        for path in rootPath.walk(lambda n: n.endswith(EXT.META)):
            md = Metadata(path=path)
            curDict = None
            for part in md.relPath.split('/'):
                if part not in pages:
                    pages[part] = OrderedDict()
                curDict = pages[part]
            # noinspection PyUnboundLocalVariable
            curDict[part] = md.relFilePath
        return pages

    def jsonify_structure(self, pageMap):
        log.debug(str(pageMap))
        with open(self.structureDstPath, 'w') as fp:
            json.dump(pageMap, fp)

if __name__ == '__main__':
    from adfd.cli import AdfdCntFinalize

    AdfdCntFinalize('bla').main()
