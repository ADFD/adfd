import logging
import pprint

from adfd.site.navigation import Navigator, UrlInformer
from bs4 import BeautifulSoup
from pip._vendor import requests

log = logging.getLogger(__name__)


def test_dead_links():
    problemsMap = {}
    seenLinks = set()
    nav = Navigator()
    nav.populate()
    for identifier, node in nav.identifierNodeMap.items():
        soup = BeautifulSoup(node.html, 'html5lib')
        for link in soup.findAll('a'):
            ui = UrlInformer(link.get('href'))
            if ui.isRelative or ui.isMail or ui.url in seenLinks:
                continue

            seenLinks.add(ui.url)
            log.info("test '%s'", ui.url)
            try:
                response = requests.get(ui.url, timeout=5, verify=False)
                if response.status_code != 200:
                    problemsMap[ui.url] = response
            except Exception as e:
                problemsMap[ui.url] = e
    pprint.pprint(problemsMap)
    assert not problemsMap
