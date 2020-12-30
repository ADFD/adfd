import pytest
from bs4 import BeautifulSoup

from adfd.model import Node
from adfd.web.navigation import Navigator
from adfd.web.navigation_in_page import InPageNav


@pytest.fixture(name="nav", scope="session")
def populate_nav():
    nav = Navigator()
    nav.populate()
    return nav


def test_replace_links(nav):
    node = nav.get_node("")
    # this topic has a pendant in the structure so should be replaced
    internal_url = "http://adfd.org/austausch/viewtopic.php?f=54&t=12301"
    assert internal_url in node._rawHtml
    # this topic is not in the structure yet, so shouldn't be replaced
    external_url = "http://adfd.org/austausch/viewtopic.php?f=54&t=11232"
    assert external_url in node._rawHtml
    html = nav.replace_links(node._rawHtml)
    # make sure that the beautiful soup remnants are gone
    assert all(
        t not in html
        for t in ["<html>", "<head>", "</head>", "<body>", "</body>", "</html>"]
    ), html
    # not a fan that this is replaced but links still seem to work
    external_url_replaced = "http://adfd.org/austausch/viewtopic.php?f=54&amp;t=11232"
    assert external_url_replaced in html
    internal_url_replaced = "/adfd/information-fuer-angehoerige"
    assert internal_url_replaced in html


def test_in_page_nav():
    n = Node("structure")
    ipn = InPageNav(BeautifulSoup(n.html, "html5lib"))
    ipn.create_in_page_nav()
    assert len(ipn.topHeaders) == 4
    assert len(ipn.topHeaders[1].children) == 2
