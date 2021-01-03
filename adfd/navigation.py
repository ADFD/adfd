import logging
import re
from functools import cached_property
from typing import List

import yaml
from boltons.iterutils import remap
from bs4 import BeautifulSoup

from adfd import configure_logging, metadata, process
from adfd.cnf import ADFD, RUNS_ON
from adfd.model import ArticleNode, CategoryNode, DbArticleContainer, Node

log = logging.getLogger(__name__)


class Navigator:
    def __init__(self):
        self._reset()

    def _reset(self):
        log.info("RESET NAVIGATOR")
        self.isPopulated = False
        self.identifierNodeMap = {}
        self.pathNodeMap = {}
        self.yamlKeyNodeMap = {}
        self.last_update = "never"
        self.orphanNodes = []
        self.activeNode = None

    def populate(self):
        log.info("populate navigation")
        self._reset()
        self.structure = self.load_structure()
        remap(self.structure, visit=self.visit)
        self.root = self.yamlKeyNodeMap[next(iter(self.structure))]
        self.menu = self.root.children
        self.isPopulated = True
        self._populate_orphan_nodes()
        self.last_update = process.date_from_timestamp()
        log.info("navigation populated")

    def get_node(self, key) -> Node:
        try:
            return self.pathNodeMap[f"/{key}"]
        except Exception as e:
            return CategoryNode(f"/{key} -> {type(e)}({e.args})")

    @cached_property
    def allNodes(self) -> List[Node]:
        if not self.isPopulated:
            self.populate()
        return sorted([n for n in self.pathNodeMap.values()])

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
            self.pathNodeMap[node.relPath] = node
            self.identifierNodeMap[node.identifier] = node
            log.info(f"{node.relPath} ({node.identifier})")
        return key, value

    def _populate_orphan_nodes(self):
        if not RUNS_ON.DEVBOX:
            log.warning("not on dev box: not populating orphan nodes")
            return

        from adfd.db.lib import DB_WRAPPER

        log.debug("populating orphan nodes")
        for topic_id in DB_WRAPPER.get_topic_ids(ADFD.MAIN_CONTENT_FORUM_ID):
            if (
                topic_id not in self.identifierNodeMap
                and topic_id not in ADFD.IGNORED_CONTENT_TOPICS
            ):
                node = ArticleNode(topic_id, isOrphan=True)
                log.info(f"{node.relPath} ({node.identifier})")
                self.identifierNodeMap[node.identifier] = node
                self.orphanNodes.append(node)

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

    @staticmethod
    def load_structure():
        if ADFD.USE_FILE:
            structure = ADFD.STRUCTURE_PATH.read()
        else:
            content = DbArticleContainer(ADFD.STRUCTURE_TOPIC_ID)
            structure = metadata.extract_from_bbcode(ADFD.CODE_TAG, content.raw_bbcode)
        assert structure, f"empty structure ({ADFD.USE_FILE})"
        return yaml.safe_load(structure)

    def replace_links(self, html):
        soup = BeautifulSoup(html, "html5lib")
        for link in soup.findAll("a"):
            url = link["href"]
            ui = UrlInformer(url)
            if ui.pointsToObsoleteLocation:
                log.warning("obsolete url: %s", ui.url)
            if ui.pointsToTopic:
                targetNode = self.identifierNodeMap.get(ui.topicId)
                if not targetNode:
                    continue
                if targetNode.relPath in self.pathNodeMap:
                    link.attrs["href"] = targetNode.relPath
                else:
                    log.warning(f"link to topic not on web page: {url}")
        # remove extra tags - very ugly, but simple and works
        return (
            str(soup)
            .replace("<html><head></head><body>", "")
            .replace("</body></html>", "")
        )


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
            if not RUNS_ON.DEVBOX:
                raise NotImplementedError("cache needs a higher level wraper for this")

            from adfd.db.lib import DB_WRAPPER

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
    configure_logging("INFO")
    _nav = Navigator()
    _nav.populate()
    for idx, this in enumerate(sorted(node for node in _nav.allNodes)):
        print(idx, this.relPath, this.isOrphan)
