import io
import logging
import re
from collections import OrderedDict
from functools import cached_property
from typing import List

import yaml
from boltons.iterutils import remap
from bs4 import BeautifulSoup

from adfd.cnf import SITE
from adfd.db.lib import DB_WRAPPER
from adfd.model import ArticleNode, CategoryNode, DbArticleContainer, Node
from adfd.process import extract_from_bbcode, date_from_timestamp

log = logging.getLogger(__name__)


class Navigator:
    def __init__(self):
        self.identifierNodeMap = {}
        self.isPopulated = False
        self.pathNodeMap = {}
        self.yamlKeyNodeMap = {}
        self.orphanNodes = []

    def populate(self):
        log.info("populate navigation")
        self._reset()
        self.structure = self.load_structure()
        remap(self.structure, visit=self.visit)
        self.root = self.yamlKeyNodeMap[next(iter(self.structure))]
        self.menu = self.root.children
        self.isPopulated = True
        self.orphanNodes = self._populate_orphan_nodes()
        self.last_update = date_from_timestamp()
        log.info("navigation populated")

    def _reset(self):
        log.info("RESET NAVIGATOR")
        self.isPopulated = False
        self.pathNodeMap = {}
        self.yamlKeyNodeMap = {}
        self.orphanNodes = []

    def get_node(self, key) -> Node:
        try:
            return self.pathNodeMap[f"/{key}"]
        except Exception as e:
            msg = f"/{key} -> {type(e)}({e.args})"
            log.error(msg, exc_info=True)
            return CategoryNode(msg)

    def get_target_node(self, topicId) -> Node:
        return self.identifierNodeMap.get(topicId)

    @cached_property
    def readyForPrimeTime(self):
        return not len(self.openIssues)

    @cached_property
    def allNodes(self) -> List[Node]:
        if not self.isPopulated:
            self.populate()
        return sorted([n for n in self.pathNodeMap.values()])

    @cached_property
    def saneNodes(self):
        return sorted([n for n in self.allNodes if n.isSane])

    @cached_property
    def dirtyNodes(self):
        return [n for n in self.saneNodes if n.isDirty]

    @cached_property
    def foreignNodes(self):
        return [n for n in self.saneNodes if n.isForeign]

    @cached_property
    def todoNodes(self):
        return [n for n in self.saneNodes if n.hasTodos]

    @cached_property
    def smilieNodes(self):
        return [n for n in self.saneNodes if n.hasSmilies]

    @cached_property
    def hasBrokenNodes(self):
        return len(self.allNodes) != len(self.saneNodes)

    @cached_property
    def brokenBBCodeNodes(self):
        return [n for n in self.allNodes if n.bbcodeIsBroken]

    @cached_property
    def brokenMetadataNodes(self):
        return [n for n in self.saneNodes if n.hasBrokenMetadata]

    @cached_property
    def openIssues(self):
        return (
            self.dirtyNodes
            + self.foreignNodes
            + self.todoNodes
            + self.smilieNodes
            + self.brokenBBCodeNodes
            + self.brokenMetadataNodes
        )

    @cached_property
    def nav(self):
        return "".join([str(m) for m in self.menu])

    def visit(self, path, key, value):
        log.debug(f"visit({path!r}, {key!r}, {value!r})")
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
            self.add_new_node_to_structure(node)
        return key, value

    def _populate_orphan_nodes(self):
        log.debug("populating orphan nodes")
        for topic_id in DB_WRAPPER.get_topic_ids(SITE.MAIN_CONTENT_FORUM_ID):
            if (
                topic_id not in self.identifierNodeMap
                and topic_id not in SITE.IGNORED_CONTENT_TOPICS
            ):
                node = ArticleNode(topic_id, isOrphan=True)
                self.add_new_node_to_structure(node)

    def add_new_node_to_structure(self, node):
        self.pathNodeMap[node.relPath] = node
        self.identifierNodeMap[node.identifier] = node
        log.info(
            f"{'[ORPHAN] ' if node.isOrphan else ' '}{node.title} ({node.identifier})"
        )

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
        cls,
        path=SITE.STRUCTURE_PATH,
        topicId=SITE.STRUCTURE_TOPIC_ID,
        useFile=SITE.USE_FILE,
    ):
        class OrderedLoader(yaml.SafeLoader):
            def __init__(self, stream):
                # noinspection PyUnresolvedReferences
                self.add_constructor(
                    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                    self.construct_ordered_mapping,
                )
                super().__init__(stream)

            @staticmethod
            def construct_ordered_mapping(loader, node):
                loader.flatten_mapping(node)
                return OrderedDict(loader.construct_pairs(node))

        def ordered_yaml_load(stream):
            return yaml.load(stream, OrderedLoader)

        if useFile:
            return ordered_yaml_load(stream=open(path, encoding="utf8"))

        content = DbArticleContainer(topicId)
        yamlContent = extract_from_bbcode(SITE.CODE_TAG, content._bbcode)
        return ordered_yaml_load(stream=io.StringIO(yamlContent))

    def replace_links(self, html):
        soup = BeautifulSoup(html, "html5lib")
        for link in soup.findAll("a"):
            url = link["href"]
            ui = UrlInformer(url)
            if ui.pointsToObsoleteLocation:
                log.warning("obsolete url: %s", ui.url)
            if ui.pointsToTopic:
                targetNode = self.get_target_node(ui.topicId)
                if not targetNode:
                    continue
                link.attrs["href"] = targetNode.relPath
        # Note remove extra tags - very ugly, but simple and works
        txt = str(soup)
        txt = txt.replace("<html><head></head><body>", "")
        txt = txt.replace("</body></html>", "")
        return txt


class UrlInformer:
    DOMAINS = [
        "adfd.org",
        "adfd.de",
        "antidepressiva-absetzen.de",
        "psychopharmaka-absetzen.de",
    ]
    BOARD_FOLDER = "austausch"
    OBSOLETE_FOLDERS = ["wiki", "forum"]
    VIEWTOPIC = "viewtopic.php"

    def __init__(self, url):
        self.url = url

    @cached_property
    def topicId(self):
        topicIdMatch = re.search(r"t=(\d*)", self.url)
        if topicIdMatch:
            return int(topicIdMatch.group(1))

        postIdMatch = re.search(r"p=(\d*)", self.url)
        if postIdMatch:
            postId = postIdMatch.group(1)
            return int(DB_WRAPPER.get_post(postId).topic_id)

    @cached_property
    def pointsToTopic(self):
        return self.pointsToForum and self.VIEWTOPIC in self.url

    @cached_property
    def pointsToObsoleteLocation(self):
        return self.isOneOfUs and any(
            "/%s/" % f in self.url for f in self.OBSOLETE_FOLDERS
        )

    @cached_property
    def pointsToForum(self):
        return self.isOneOfUs and self.BOARD_FOLDER in self.url

    @cached_property
    def isOneOfUs(self):
        return self.isRelative or any(d in self.url for d in self.DOMAINS)

    @cached_property
    def isRelative(self):
        return any(self.url.startswith(prefix) for prefix in ["#", "/"])

    @cached_property
    def isMail(self):
        return self.url.startswith("mailto:")


if __name__ == "__main__":
    # log.setLevel(logging.DEBUG)
    _nav = Navigator()
    _nav.populate()
    for idx, node in enumerate(sorted(node for node in _nav.allNodes)):
        print(idx, node.relPath)
