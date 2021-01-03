import pytest

from adfd.model import ArticleContainer
from adfd.navigation import Navigator
from adfd.parse import ADFD_PARSER
from adfd.scripts.check_readiness import ReadinessChecker


@pytest.mark.xfail(reason="not ready")
def test_readiness():
    rc = ReadinessChecker(Navigator(), verbosity=1)
    print(rc.report)
    assert rc.is_ready


class TestUnknownTags:
    _nodes = Navigator().allNodes
    ARTICLE_NODES = [
        node for node in _nodes if isinstance(node.contcon, ArticleContainer)
    ]
    _IGNORED_TAGS = []
    # _IGNORED_TAGS = [
    #     "inhalt",
    #     "seroxat",
    #     "ergänzung",
    #     "david",
    #     "anmerkung",
    #     "link",
    #     "halbwegs",
    #     "ad",
    #     "wieder",
    #     "11c",
    #     ":",
    #     ".",
    #     "..",
    #     "...",
    # ]

    @pytest.mark.xfail(reason="not all ready")
    @pytest.mark.usefixtures("adfd_strict")
    @pytest.mark.parametrize(
        "node", ARTICLE_NODES, ids=lambda node: f"{node.title} / {node.identifier}"
    )
    def test_ensure_no_unknown_tags(self, node):
        unknown_tags = ADFD_PARSER.tokenize(node.raw_bbcode, get_unknowns=True)
        unknown_tags = {
            t for t in unknown_tags if t not in self._IGNORED_TAGS and not t.isnumeric()
        }
        assert not unknown_tags
