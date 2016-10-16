import io
import logging
from collections import OrderedDict

from boltons.iterutils import remap
import yaml

from adfd.cnf import SITE
from adfd.parse import extract_from_bbcode
from adfd.model import CategoryNode, ArticleNode, DbContentContainer

log = logging.getLogger(__name__)


class Navigator:
    def __init__(self):
        self._reset()

    def populate(self):
        self._reset()
        self.structure = self.load_structure()
        remap(self.structure, visit=self.visit)
        self.root = self.yamlKeyNodeMap[next(iter(self.structure))]
        self.menu = self.root.children

    def _reset(self):
        self.pathNodeMap = {}
        self.identifierNodeMap = {}
        self.yamlKeyNodeMap = {}

    @property
    def allNodes(self):
        return sorted([n for n in self.pathNodeMap.values()])

    @property
    def dirtyNodes(self):
        return [n for n in self.allNodes if n.article.isDirty]

    @property
    def nav(self):
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

    @classmethod
    def load_structure(
            cls, path=SITE.STRUCTURE_PATH, topicId=SITE.STRUCTURE_TOPIC_ID,
            useFile=SITE.USE_FILE):
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

        def ordered_yaml_load(stream):
            return yaml.load(stream, OrderedLoader)

        if useFile:
            return ordered_yaml_load(stream=open(path, encoding='utf8'))

        content = DbContentContainer(topicId)
        yamlContent = extract_from_bbcode(SITE.CODE_TAG, content.bbcode)
        return ordered_yaml_load(stream=io.StringIO(yamlContent))
