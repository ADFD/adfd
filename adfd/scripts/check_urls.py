"""
# TODO
## URLS

* Harvest ALL urls (e.g. for link checking)
* Look at bbcode! <URL>...</URL> or <URL=...>...</URL>
* search for links to adfd.org/wissen and fix them
* search for links to antidepressiva-absetzen.de and fix them
* extract domain and use in autogenerated links
  (use link extraction in parser for that)
* add external, internal and forum link signifiers
"""
import asyncio
import logging

import async_timeout
from aiohttp import ClientSession
from bs4 import BeautifulSoup

from adfd.navigation import Navigator, UrlInformer

log = logging.getLogger(__name__)

# class Linker:
#     def __init__(self, link, postUrl=None, postLine=None):
#         self.link = link
#         self.postUrl = postUrl
#         self.postLine = postLine


def get_urls():
    nav = Navigator()
    nav.populate()
    seenLinks = set()
    for identifier, node in nav.identifierNodeMap.items():
        log.info(f"processing {identifier} | {node.relPath}")
        soup = BeautifulSoup(node.html, "html5lib")
        for link in soup.findAll("a"):
            candidate = link.get("href")
            if candidate.startswith("#"):
                continue  # internal anchorlink
            if not candidate.startswith("http"):
                continue  # TODO are these titles of navi links or a bug?
            ui = UrlInformer(candidate)
            if ui.isRelative or ui.isMail or ui.url in seenLinks:
                continue
            seenLinks.add(ui.url)
    return seenLinks


async def make_request(session, url):
    async with async_timeout.timeout(60):
        try:
            async with session.get(url) as response:
                return url, response
        except Exception as e:
            return url, e


async def check_urls(urls):
    brokenUrls = []
    async with ClientSession() as session:
        tasks = []
        for url in urls:
            coroutine = make_request(session, url)
            task = asyncio.ensure_future(coroutine)
            tasks.append(task)
            log.info(f"appended task for {url}")
        for url, result in await asyncio.gather(*tasks):
            if isinstance(result, Exception):
                brokenUrls.append((url, f"{type(result)}"))
            elif result.status != 200:
                brokenUrls.append((url, f"{result.status}: {result.reason}"))
    if brokenUrls:
        log.info(f"{len(brokenUrls)} are broken")
        for url, reason in brokenUrls:
            print(f"{url} -> {reason}")
    return brokenUrls


def run_check_links_loop(urls):
    loop = asyncio.get_event_loop()
    coroutine = check_urls(urls)
    future = asyncio.ensure_future(coroutine)
    loop.run_until_complete(future)


def check_site_urls():
    urls = get_urls()
    log.info(f"checking {len(urls)} urls ...")
    run_check_links_loop(urls)


if __name__ == "__main__":
    check_site_urls()
