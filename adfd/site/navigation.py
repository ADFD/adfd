import io
import logging
import re

from boltons.iterutils import remap
from bs4 import BeautifulSoup
from cached_property import cached_property

from adfd.cnf import SITE
from adfd.db.model import Topic
from adfd.utils import slugify, ordered_yaml_load

log = logging.getLogger(__name__)


class Node:
    SPEC = "N"

    def __init__(self, topicId, name=None):
        self.topicId = topicId
        self.isHome = name == ''
        self._name = name

    def __repr__(self):
        return "<%s(%s)>" % (self.SPEC, self.name)

    @cached_property
    def html(self):
        return self.topic.html

    @cached_property
    def link(self):
        return "http://adfd.org/austausch/viewtopic.php?t=%s" % self.topic.id

    @cached_property
    def name(self):
        return self._name or self.topic.subject

    @cached_property
    def slug(self):
        """:rtype: str"""
        return slugify(self.name) if not self.isHome else ''

    @cached_property
    def topic(self):
        """:rtype: adfd.db.model.Topic"""
        return Topic(self.topicId)


class CategoryNode(Node):
    SPEC = "C"

    def __init__(self, data):
        super().__init__(*self._parse(data))

    @classmethod
    def _parse(cls, data):
        sep = "|"
        sd = data.split(sep)
        if len(sd) > 2:
            raise ValueError("Too many '%s' in %s" % (sep, data))

        title = sd[0].strip()
        title = title if title != "Home" else ""
        mainTopicId = int(sd[1].strip()) if len(sd) == 2 else 0
        return mainTopicId, title


class ArticleNode(Node):
    SPEC = "A"


class Navigator:
    CAT_MAIN = ('<div class="ui simple dropdown item"><a href="%s">%s</a>'
                ' <i class="dropdown icon"></i>', '</div>')
    CAT_SUB = ('<div class="item"><i class="dropdown icon">'
               ' </i><a href="%s">%s</a>', '</div>')
    # TODO highlight active
    CAT_MAIN_ACT =CAT_MAIN
    CAT_SUB_ACT =CAT_SUB
    SUB = ('<div class="menu">', '</div>')
    ELEM = ('<a class="item" href="%s">%s', '</a>')
    ELEM_ACT = ELEM

    pathNodeMap = {}

    def __init__(self, yamlStructure):
        self.structure = remap(yamlStructure, visit=self.create_nodes)
        root = next(iter(self.structure))
        self.pathNodeMap['/'] = root
        self.menu = self.structure[root]
        self.lastPath = '/'

    def get_navigation(self, newPath=""):
        self._elems = []
        self._recursive_add_elems(self.menu)
        self.pathNodeMap[self.lastPath].isActive = False
        self.pathNodeMap[newPath].isActive = True
        self.lastPath = newPath
        soup = BeautifulSoup("\n".join(self._elems), 'html.parser')
        return soup.prettify()

    def _recursive_add_elems(self, node, prefix='', isSubMenu=False):
        if isinstance(node, dict):
            for category, val in node.items():
                relPath = self.get_rel_path(category, prefix)
                cat = self.get_cat_pattern(isSubMenu, category.topic.isActive)
                self._add_elem(cat[0] % (relPath, category.name))
                self._add_elem(self.SUB[0])
                self._recursive_add_elems(val, prefix=relPath, isSubMenu=True)
                self._add_elem(self.SUB[1])
                self._add_elem(cat[1])
        elif isinstance(node, list):
            for e in node:
                self._recursive_add_elems(e, prefix=prefix)
        elif isinstance(node, Node):
            relPath = self.get_rel_path(node, prefix)
            elem = self.ELEM_ACT if node.topic.isActive else self.ELEM
            text = elem[0] % (relPath, node.name) + elem[1]
            self._add_elem(text)
        else:
            raise Exception("%s" % (type(node)))

    def get_cat_pattern(self, isSubMenu, isActive):
        if isSubMenu:
            return self.CAT_SUB_ACT if isActive else self.CAT_SUB

        return self.CAT_MAIN_ACT if isActive else self.CAT_MAIN

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
            self.get_navigation()
        return list(self.pathNodeMap.keys())

    @cached_property
    def allTopics(self):
        if not hasattr(self, '_elems'):
            self.get_navigation()
        return list([n.topic for n in self.pathNodeMap.values()])

    @staticmethod
    def create_nodes(_, key, value):
        if isinstance(key, str):
            key = CategoryNode(key)
        elif isinstance(value, int):
            value = ArticleNode(value)
        return key, value


def get_yaml_structure():
    if SITE.USE_FILE:
        return ordered_yaml_load(stream=open(SITE.STRUCTURE_PATH))

    topic = Topic(SITE.STRUCTURE_TOPIC_ID)
    regex = re.compile(r'\[code\](.*)\[/code\]', re.MULTILINE | re.DOTALL)
    match = regex.search(topic.posts[0].content)
    stream = io.StringIO(match.group(1))
    return ordered_yaml_load(stream=stream)
