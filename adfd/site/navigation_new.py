import collections as col
import logging

from boltons.iterutils import remap

from adfd.model import CategoryNode, ArticleNode, StructureLoader

log = logging.getLogger(__name__)


class Navigator:
    def __init__(self):
        self.pathNodeMap = {}
        self.identifierNodeMap = {}
        self.yamlKeyNodeMap = {}

        self.structure = StructureLoader.load()
        self.rootKey = next(iter(self.structure))
        # fixme do this only with remap
        # self.pathNodeMap = {"/": self.root}
        # self.identifierNodeMap = {self.root.identifier: self.root}
        self.populate()
        self.root = self.yamlKeyNodeMap[self.rootKey]

    def populate(self):
        return remap(self.structure, visit=self.visit)

    def visit(self, path, key, value):
        print('visit(%r, %r, %r)' % (path, key, value))
        node = None
        if isinstance(key, str):
            node = self.get_cat_node(key=key)
            node.parents = self.get_parent_nodes(path)
        elif isinstance(value, (int, str)):
            node = ArticleNode(value)
        if path and node:
            cat = self.get_cat_node(path=path)
            cat.children.append(node)
        return key, value

    def get_parent_nodes(self, path):
        parents = []
        for elem in path:
            if isinstance(elem, int):
                continue

            parents.append(self.get_cat_node(key=elem))
        return parents

    def get_cat_node(self, key=None, path=None):
        key = key or path[-1]
        try:
            return self.yamlKeyNodeMap[key]

        except KeyError:
            key = key if not isinstance(key, int) else path[-2]
            try:
                return self.yamlKeyNodeMap[key]

            except KeyError:
                cat = CategoryNode(key)
                self.yamlKeyNodeMap[key] = cat
                return cat
