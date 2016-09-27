import io
import logging
import re

from adfd.cnf import SITE
from adfd.model import Topic, Node, CategoryNode, ArticleNode
from adfd.utils import ordered_yaml_load
from boltons.iterutils import remap
from bs4 import BeautifulSoup
from cached_property import cached_property

log = logging.getLogger(__name__)


class Navigator:
    SUB = ('<div class="menu">', '</div>')

    pathNodeMap = {}

    def __init__(self):
        self.structure = remap(self.load_structure(), visit=self.create_nodes)
        root = next(iter(self.structure))
        self.pathNodeMap['/'] = root
        self.menu = self.structure[root]
        self.lastPath = '/'

    def generate_navigation(self, newPath=""):
        self._elems = []
        self._recursive_add_elems(self.menu)
        log.info("%s -> %s", self.lastPath, newPath)
        # FIXME setting to active does not translate into active class yet!
        self.pathNodeMap[self.lastPath].isActive = False
        self.pathNodeMap[newPath].isActive = True
        self.lastPath = newPath
        soup = BeautifulSoup("\n".join(self._elems), 'html.parser')
        return soup.prettify()

    def _recursive_add_elems(self, node, prefix='', isSubMenu=False):
        if isinstance(node, dict):
            for category, val in node.items():
                relPath = self.get_rel_path(category, prefix)
                catElems = category.get_nav_elems(relPath, isSubMenu)
                self._add_elem(catElems[0])
                self._add_elem(self.SUB[0])
                self._recursive_add_elems(val, prefix=relPath, isSubMenu=True)
                self._add_elem(self.SUB[1])
                self._add_elem(catElems[1])
        elif isinstance(node, list):
            for e in node:
                self._recursive_add_elems(e, prefix=prefix)
        elif isinstance(node, Node):
            relPath = self.get_rel_path(node, prefix)
            catElems = node.get_nav_elems(relPath, isSubMenu)
            self._add_elem("".join(catElems))
        else:
            raise Exception("%s" % (type(node)))

    def get_rel_path(self, node, prefix):
        """adds it to the map as side effect"""
        relPath = prefix + "/" + node.slug
        if relPath not in self.pathNodeMap:
            self.pathNodeMap[relPath] = node
        return relPath

    def _add_elem(self, text):
        self._elems.append(text)

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

    @staticmethod
    def load_structure():
        if SITE.USE_FILE:
            return ordered_yaml_load(stream=open(SITE.STRUCTURE_PATH))

        topic = Topic(SITE.STRUCTURE_TOPIC_ID)
        regex = re.compile(r'\[code\](.*)\[/code\]', re.MULTILINE | re.DOTALL)
        match = regex.search(topic.posts[0].content)
        stream = io.StringIO(match.group(1))
        return ordered_yaml_load(stream=stream)
