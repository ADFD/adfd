"""
todo special handling for special posts/topics
* posts that should be embedded (e.g. in a slider)
* a topic that serves as glossary
"""
import logging
import os
import re
import subprocess
import time
import bbcode

from article import ENC


log = logging.getLogger(__name__)


def make_header(text, level=1):
    # todo make more intelligent and make it work for md and bbcode as well
    header = text
    overline = ''
    underline = ''
    if level == 1:
        overline = "=" * len(text)
        underline = "=" * len(text)
    if level == 2:
        underline = "=" * len(text)
    if level == 3:
        underline = "-" * len(text)
    if overline:
        header = "%s\n%s" % (overline, header)
    header = "%s\n%s" % (header, underline)
    return header


def make_link(text, url, ext):
    assert ext in ['rst', 'md', 'bb'], ext
    if ext == 'rst':
        return "`%s <%s>`_" % (text, url)

    if ext == 'md':
        return "[%s](%s)" % (text, url)

    return "[url=%s]%s[/url]" % (text, url)


# fixme where to put this?
# @property
# def content(self):
#     contentMetaDataPairs = []
#     for pm in self._postmen:
#         if pm.postId != self.firstPostId:
#             content += utils.make_header(pm.subject) + '\n\n'
#         content += pm.get_content(self.target) + '\n\n'
#     return content


# fixme where to put this?
def url_refers_to_this(url, topicId, postIds):
    if "t=%s" % (topicId) in url:
        return True

    if any("p=%s" % (postId) in url for postId in postIds):
        return True


# create nested folder structure inspiration
# def create_structure(self):
#     log.info('creating structure from %s', self.structure)
#     for contentPath, objs in self.structure:
#         for obj in objs:
#             relPath = self.get_rel_page_path(contentPath, obj.fileName)
#             self.relPathObjMap[relPath] = obj
#     log.debug("created %s", self.relPathObjMap)
#
#     def get_rel_page_path(self, contentPath, fileName):
#         return LocalPath(contentPath) / fileName


BBCODE_SANITY = [
    ('\[quote="(.*?)"\](.*?)\[\/quote\]', '[quote]\g<2>\n\n<!-CITE-> \g<1>[/quote]'),
]

MARKDOWN = [
    ('\[img\]\[(.*?)\]\((.*?)\)\[\/img\]', '![\g<1>](\g<2>)'),
]

HTML_TEXT = [
    ('\[img\]<a href="(.*?)">(.*?)</a>\[/img]',
     '<a href="\g<1>"><img src="\g<2>" /></a>'),
]

RESTRUCTURED_TEXT = [
    # see https://github.com/jgm/pandoc/issues/678
    # ('\|image(\d.*?)\|', '|image\g<1>|_'),
    ('<!-CITE->', '\n    --'), # citation swallowed by html
]

PANDOC_IS_CRAZY = [
    ('^\| (.*)', '\g<1>'),  # splatters | randomly at line starts !?
]

def replace(text, replacements, flags=re.DOTALL):
    for pattern, replacement in replacements:
        log.debug("'%s' -> '%s'\n%s", pattern, replacement, text)
        text = re.compile(pattern, flags=flags).sub(replacement, text)
        log.debug("applied\n%s\n%s", text, '#' * 120)
    return text


# Todo make this fetch from Article
class Postman(object):
    def __init__(self, post):
        if isinstance(post, int):
            # fixme fetch from file(s)
            post = fetch_post(post)
        self.p = post

    @property
    def saneBbCodeContent(self):
        return replace(self.p.preprocessedText, BBCODE_SANITY)

    @property
    def htmlText(self):
        return bbcode.render_html(self.saneBbCodeContent)

    @property
    def rstText(self):
        html = self.htmlText
        rst = self._transform_to(html, 'rst')
        rst = replace(rst, RESTRUCTURED_TEXT)
        rst = replace(
            rst, PANDOC_IS_CRAZY, flags=re.MULTILINE)
        return rst

    @property
    def markdownText(self):
        out = self._transform_to(self.htmlText, 'markdown')
        # out = out.replace('\\', '')  # todo necessary?
        return replace(out, MARKDOWN)

    def _transform_to(self, htmlSource, fmt):
        """markdown, rst, ..."""
        tmpPath = '/tmp/postman_%.20f.html' % time.time()
        htmlSource = replace(htmlSource, HTML_TEXT)
        with open(tmpPath, 'w') as f:
            f.write(htmlSource.encode(ENC.OUT))
        cmd = ['pandoc', tmpPath, '-f', 'html', '-t', fmt]
        out = unicode(subprocess.check_output(cmd).decode(ENC.OUT))
        os.remove(tmpPath)
        return out
