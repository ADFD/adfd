import io
import logging
from collections import OrderedDict

from boltons.iterutils import remap
import yaml

from adfd.cnf import SITE
from adfd.parse import extract_from_bbcode
from adfd.model import CategoryNode, ArticleNode

log = logging.getLogger(__name__)


class Navigator:
    def __init__(self):
        self.pathNodeMap = {}
        self.identifierNodeMap = {}
        self.yamlKeyNodeMap = {}
        self.structure = StructureLoader.load()
        remap(self.structure, visit=self.visit)
        self.root = self.yamlKeyNodeMap[next(iter(self.structure))]
        self.menu = self.root.children

    @property
    def menuAsString(self):
        return "".join([str(m) for m in self.menu])

    def visit(self, path, key, value):
        # print('visit(%r, %r, %r)' % (path, key, value))
        node = None
        if isinstance(key, str):
            node = self.get_cat_node(key=key)
        elif isinstance(value, (int, str)):
            node = ArticleNode(value)
        if node:
            node.parents = self.get_parent_nodes(path)
            cat = self.get_cat_node(path=path)
            if cat:
                cat.children.append(node)
            self.pathNodeMap[node.relPath] = node
            self.identifierNodeMap[node.identifier] = node
        return key, value

    def get_parent_nodes(self, path):
        parents = []
        for elem in path:
            if isinstance(elem, int):
                continue

            parents.append(self.get_cat_node(key=elem))
        return parents

    def get_cat_node(self, key=None, path=None):
        if not key and not path:
            return None

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


class StructureLoader:
    class OrderedLoader(yaml.SafeLoader):
        def __init__(self, stream):
            # noinspection PyUnresolvedReferences
            self.add_constructor(
                yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                self.construct_ordered_mapping)
            super().__init__(stream)

        @staticmethod
        def construct_ordered_mapping(loader, node):
            loader.flatten_mapping(node)
            return OrderedDict(loader.construct_pairs(node))

    @classmethod
    def load(cls):
        if SITE.USE_FILE:
            return cls.ordered_yaml_load(stream=open(SITE.STRUCTURE_PATH))

        node = ArticleNode(SITE.STRUCTURE_TOPIC_ID)
        yamlContent = extract_from_bbcode(SITE.CODE_TAG, node.bbcode)
        return cls.ordered_yaml_load(stream=io.StringIO(yamlContent))

    @classmethod
    def ordered_yaml_load(cls, stream):
        return yaml.load(stream, cls.OrderedLoader)
