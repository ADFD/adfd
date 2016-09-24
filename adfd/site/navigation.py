import io
import logging
import re

from adfd.cst import SITE
from adfd.db.model import Topic
from adfd.utils import slugify, ordered_yaml_load
from boltons.iterutils import remap
from cached_property import cached_property

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
    GLOBAL = ('<ul class="vertical medium-horizontal menu" '
              'data-responsive-menu="drilldown medium-dropdown">', '</ul>')
    MAIN = ('<ul class="submenu menu vertical" data-submenu>', '</ul>')
    CAT = ('<a href="%s">%s', '</a>')
    CAT_ACT = ('<a style="text-weight: bold;" href="%s">%s', '</a>')
    SUB = ('<li class="has-submenu">', '</li>')
    ELEM = ('<li><a href="%s">%s', '</a></li>')
    ELEM_ACT = ('<li style="text-weight: bold;"><a href="%s">%s', '</a></li>')

    pathNodeMap = {}

    def __init__(self, yamlStructure):
        self.structure = remap(yamlStructure, visit=self.create_nodes)
        root = next(iter(self.structure))
        self.pathNodeMap['/'] = root
        self.menu = self.structure[root]
        self.depth = 1
        self.lastPath = '/'

    def get_navigation(self, newPath=""):
        self._elems = []
        self._recursive_add_elems(self.menu)
        self.pathNodeMap[self.lastPath].isActive = False
        self.pathNodeMap[newPath].isActive = True
        self.lastPath = newPath
        return "\n".join(self._elems)

    @cached_property
    def allUrls(self):
        if not hasattr(self, '_elems'):
            self.get_navigation()
        return list(self.pathNodeMap.keys())

    @cached_property
    def allTopics(self):
        return list([n.topic for n in self.pathNodeMap.values()])

    def _recursive_add_elems(self, node, prefix=''):
        self._add_elem(self.GLOBAL[0] if self.depth == 1 else self.MAIN[0])
        self.depth += 1
        if isinstance(node, dict):
            for category, val in node.items():
                self._add_elem(self.SUB[0])
                relPath = prefix + "/" + category.slug
                if relPath not in self.pathNodeMap:
                    self.pathNodeMap[relPath] = category
                pattern = self.CAT_ACT if category.topic.isActive else self.CAT
                text = pattern[0] % (relPath, category.name) + pattern[1]
                self._add_elem(text)
                self._recursive_add_elems(val, prefix=relPath)
                self._add_elem(self.SUB[1])
        elif isinstance(node, list):
            for e in node:
                self._recursive_add_elems(e, prefix=prefix)
        elif isinstance(node, Node):
                relPath = prefix + "/" + node.slug
                if relPath not in self.pathNodeMap:
                    self.pathNodeMap[relPath] = node
                pattern = self.ELEM_ACT if node.topic.isActive else self.ELEM
                text = pattern[0] % (relPath, node.name) + pattern[1]
                self._add_elem(text)
        else:
            raise Exception("%s" % (type(node)))
        self.depth -= 1
        self._add_elem(self.GLOBAL[1] if self.depth == 1 else self.MAIN[1])

    def _add_elem(self, text):
        spaces = ' ' * (4 * (self.depth - 1)) if self.depth > 1 else ""
        self._elems.append(spaces + text)

    @staticmethod
    def create_nodes(_, key, value):
        if isinstance(key, str):
            key = CategoryNode(key)
        elif isinstance(value, int):
            value = ArticleNode(value)
        return key, value


def get_yaml_structure():
    if SITE.USE_FILE:
        stream = open(SITE.STRUCTURE_PATH)
    else:
        topic = Topic(SITE.STRUCTURE_TOPIC_ID)
        regex = re.compile(r'\[code\](.*)\[/code\]', re.MULTILINE | re.DOTALL)
        match = regex.search(topic.posts[0].content)
        stream = io.StringIO(match.group(1))
    return ordered_yaml_load(stream=stream)
