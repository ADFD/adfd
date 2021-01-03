"""
## cache

    @property
    def isForeign(self):
        return self.container_md["isForeign"]

    @property
    def isImported(self):
        return self.container_md["isImported"]

    @cached_property
    def isSane(self):
        try:
            return (
                self.identifier != ADFD.PLACEHOLDER_TOPIC_ID
                and isinstance(self.raw_bbcode, str)
                and isinstance(self.title, str)
                and isinstance(self.relPath, str)
            )
        except Exception as e:
            log.warning(f"{self.identifier} is not sane ({e})")
            return False

## Navigator

    @cached_property
    def readyForPrimeTime(self):
        return not len(self.openIssues)

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

"""
import logging
import re
from typing import Iterable

from adfd.model import CachedArticleContainer, ArticleContainer
from adfd.navigation import Navigator
from adfd.parse import ADFD_PARSER

log = logging.getLogger(__name__)


class ReadinessChecker:
    class ArticleReadinessInformer:
        def __init__(self, article):
            self.article = article
            self.is_ready = True
            self.report = None

    def __init__(self, navigator: Navigator, verbosity=0):
        self.verbosity = verbosity
        self.navigator = navigator
        self.report = ""

    def check_readiness(self):
        articles = [
            n.contcon
            for n in self.navigator.allNodes
            if isinstance(n.contcon, ArticleContainer)
        ]
        informers = []
        for article in articles:
            assert isinstance(article, CachedArticleContainer), article
            informers.append(self.create_readiness_report(article))
        for informer in informers:
            node = self.navigator.get_node(informer.article.identifier)
            if not node:
                log.debug(f"ignore {informer.article} - not in structure")
                continue
            if not informer.is_ready:
                self.is_ready = False
                self.report += f"\n\n{informer.report}"

    def create_readiness_report(
        self, article: CachedArticleContainer
    ) -> ArticleReadinessInformer:
        informer = self.ArticleReadinessInformer(article)
        out = [f"{article.identifier} / {article.title}"]
        raw_bbcode = article.raw_bbcode
        raw_html = ADFD_PARSER.to_html(raw_bbcode)
        replaced_html = self.navigator.replace_links(raw_html)
        if self.verbosity == 1:
            out.append(f"RAW BBCODE:\n\n{raw_bbcode}\n\n")
            out.append(f"RAW HTML:\n\n{raw_html}\n\n")
            out.append(f"REPLACED HTML:\n\n{replaced_html}\n\n")
        smilies = self._get_smilies(raw_bbcode)
        if "[mod=" in article.raw_bbcode:
            out.append("Has open todos!")
            informer.is_ready = False
        if smilies:
            informer.is_ready = False
            out.append(f"smilies: {smilies}")
        if article.md._invalid_keys:
            informer.is_ready = False
            out.append(f"unknown metadata keys: {article.md._invalid_keys}")
        informer.report = "\n".join(out)
        return informer

    @staticmethod
    def _get_smilies(bbcode: str) -> Iterable[str]:
        match = re.search(r"(:[^\s/\[\].@]*?:)", bbcode)
        return match.groups() if match else ()


# TODOs
# def isForeign(self) -> bool:
#     return self._firstPost.dbp.forum_id != ADFD.MAIN_CONTENT_FORUM_ID
#
# # FIXME isForeign vs isImported only one is needed
# def isImported(self) -> bool:
#     return self._firstPost.dbp.forum_id == ADFD.MAIN_CONTENT_FORUM_ID

# if self.unknownMetadata:
#     content = (
#             self._UNKNOWN_METADATA_PATT % ", ".join(self.unknownMetadata) + content
#     )


if __name__ == "__main__":
    rr = ReadinessChecker(Navigator())
    rr.check_readiness()
    assert rr.is_ready
