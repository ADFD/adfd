import re
import time
from datetime import datetime

from boltons import strutils


class RE:
    URL = re.compile(
        r"(?im)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)"
        r"(?:[^\s()<>]+|\([^\s()<>]+\))"
        r'+(?:\([^\s()<>]+\)|[^\s`!()\[\]{};:\'".,<>?]))'
    )
    """
    from http://daringfireball.net/2010/07/improved_regex_for_matching_urls
    Only support one level of parentheses - was failing on some URLs.
    See http://www.regular-expressions.info/catastrophic.html
    """
    DOMAIN = re.compile(
        r"(?im)(?:www\d{0,3}[.]|[a-z0-9.\-]+[.]"
        r"(?:com|de|ch|at|net|org|edu|info|io|name|me|tv|us|uk|mobi))"
    )
    """
    For the URL tag, try to be smart about when to append a missing http://.
    If the given link looks like a domain, add a http:// in front of it,
    otherwise leave it alone (be a relative path, a filename, etc.).
    """


# TODO needed?
def hyphenate(text, hyphen="&shy;"):
    from pyphen import Pyphen  # FIXME move out if ever really used

    py = Pyphen(lang="de_de")
    words = text.split(" ")
    return " ".join([py.inserted(word, hyphen=hyphen) for word in words])


# TODO needed?
def untypogrify(text):
    def untypogrify_char(c):
        return '"' if c in ["“", "„"] else c

    return "".join([untypogrify_char(c) for c in text])


def date_from_timestamp(timestamp=None) -> str:
    timestamp = timestamp or time.time()
    return datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y (%H:%M Uhr)")


def slugify(text: str) -> str:
    return strutils.slugify(text, delim="-", lower=True, ascii=True).decode()
