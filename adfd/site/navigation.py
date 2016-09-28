import io
import logging
import re
# noinspection PyPackageRequirements
import yaml
from collections import OrderedDict

from boltons.iterutils import remap
from bs4 import BeautifulSoup
from cached_property import cached_property

from adfd.cnf import SITE
from adfd.model import Node, CategoryNode, ArticleNode, Post

log = logging.getLogger(__name__)


class Navigator:
    def __init__(self):
        self.structure = remap(self.load_structure(), visit=self.create_nodes)
        self.root = next(iter(self.structure))
        self.menu = self.structure[self.root]
        self.pathNodeMap = {}
        self.elems = []

    def generate_navigation(self, activePath="/"):
        self._reset()
        self.activePath = activePath
        self._recursive_add_elems(self.menu)
        soup = BeautifulSoup("\n".join(self.elems), 'html.parser')
        return soup.prettify()

    def _reset(self):
        self.elems = []
        [node.reset() for node in self.pathNodeMap.values()]
        self.pathNodeMap = {"/": self.root}

    def _recursive_add_elems(self, obj, crumbs=None):
        log.info("generate nav for %s at %s", str(obj), str(crumbs))
        crumbs = crumbs or []
        if isinstance(obj, dict):
            for cat, val in obj.items():
                assert isinstance(cat, CategoryNode)
                self._update_node(cat, crumbs)
                self.elems.append(cat.navHtmlOpener)
                self.elems.append(cat.SUB_MENU_WRAPPER[0])
                self._recursive_add_elems(val, crumbs=crumbs + [cat])
                self.elems.append(cat.SUB_MENU_WRAPPER[1])
                self.elems.append(cat.navHtmlCloser)
        elif isinstance(obj, list):
            for e in obj:
                self._recursive_add_elems(e, crumbs=crumbs)
        else:
            assert isinstance(obj, Node), obj
            self._update_node(obj, crumbs)
            self.elems.append(obj.navHtml)

    def _update_node(self, node, crumbs):
        node.parents = crumbs
        relPath = node.relPath
        if relPath not in self.pathNodeMap:
            self.pathNodeMap[relPath] = node
        if self.activePath == relPath:
            node.isActive = True

    @cached_property
    def allUrls(self):
        if not hasattr(self, '_elems'):
            self.generate_navigation()
        return list(self.pathNodeMap.keys())

    @cached_property
    def allTopics(self):
        if not hasattr(self, '_elems'):
            self.generate_navigation()
        return list([n.topic for n in self.pathNodeMap.values()])

    @staticmethod
    def create_nodes(_, key, value):
        if isinstance(key, str):
            key = CategoryNode(key)
        elif isinstance(value, int):
            value = ArticleNode(value)
        return key, value

    @classmethod
    def load_structure(cls):
        if SITE.USE_FILE:
            return cls.ordered_yaml_load(stream=open(SITE.STRUCTURE_PATH))

        post = Post(SITE.STRUCTURE_POST_ID)
        # FIXME extract to function/method extract_tag_content and reuse
        regex = re.compile(r'\[code\](.*)\[/code\]', re.MULTILINE | re.DOTALL)
        match = regex.search(post.content)
        stream = io.StringIO(match.group(1))
        return cls.ordered_yaml_load(stream=stream)

    @classmethod
    def ordered_yaml_load(cls, stream):
        class OrderedLoader(yaml.SafeLoader):
            pass

        def construct_mapping(loader, node):
            loader.flatten_mapping(node)
            return OrderedDict(loader.construct_pairs(node))

        # noinspection PyUnresolvedReferences
        OrderedLoader.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            construct_mapping)
        return yaml.load(stream, OrderedLoader)
