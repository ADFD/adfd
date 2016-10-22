import codecs
import re
import time
from datetime import datetime

from pyphen import Pyphen


class RE:
    URL = re.compile(
        r'(?im)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)'
        r'(?:[^\s()<>]+|\([^\s()<>]+\))'
        r'+(?:\([^\s()<>]+\)|[^\s`!()\[\]{};:\'".,<>?]))')
    """
    from http://daringfireball.net/2010/07/improved_regex_for_matching_urls
    Only support one level of parentheses - was failing on some URLs.
    See http://www.regular-expressions.info/catastrophic.html
    """
    DOMAIN = re.compile(
        r'(?im)(?:www\d{0,3}[.]|[a-z0-9.\-]+[.]'
        r'(?:com|net|org|edu|biz|gov|mil|info|io|name|me|tv|us|uk|mobi))')
    """
    For the URL tag, try to be smart about when to append a missing http://.
    If the given link looks like a domain, add a http:// in front of it,
    otherwise leave it alone (be a relative path, a filename, etc.).
    """


def extract_from_bbcode(tag, content):
    rString = r'\[%s\](.*)\[/%s\]' % (tag, tag)
    regex = re.compile(rString, re.MULTILINE | re.DOTALL)
    match = regex.search(content)
    try:
        return match.group(1)
    except AttributeError:
        pass
        # log.warning("no [%s] in %s[...]" % (tag, content[:50]))

# TODO needed?
def hyphenate(text, hyphen='&shy;'):
    py = Pyphen(lang='de_de')
    words = text.split(' ')
    return ' '.join([py.inserted(word, hyphen=hyphen) for word in words])


# TODO needed?
def untypogrify(text):
    def untypogrify_char(c):
        return '"' if c in ['“', '„'] else c

    return ''.join([untypogrify_char(c) for c in text])


def date_from_timestamp(timestamp=None):
    timestamp = timestamp or time.time()
    return datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y (%H:%M Uhr)')


class _Slugifier:
    """Turn sentences into slugs to be used in names and URLs"""
    SEP = '-'

    def __init__(self):
        # noinspection PyUnresolvedReferences
        import translitcodec  # register new codec for slugification

        self.splitter = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')

    def __call__(self, text):
        words = []
        for word in self.splitter.split(text.lower()):
            word = codecs.encode(word, 'translit/long')
            if word:
                words.append(word)
        return self.SEP.join(words)


slugify = _Slugifier()
