"""
This makes it possible to transfer arbitrary data contained in the `meta` tag
from posts on the board to be used by the generator or in the website articles.

To make this work the bbcode tag ``meta`` has to be defined on the board.

The following settings to be done in ``adm/index.php?i=acp_bbcodes``
define the tag and make it invisible if the post is viewed directly.

BBCode use:

    [meta]{TEXT}[/meta]

Minimal BBCode replacement:

    <div>[meta]{TEXT}[/meta]</div>
"""
import logging

from adfd.cnf import ADFD
from adfd.process import extract_from_bbcode

log = logging.getLogger(__name__)


class PageMetadata:
    KEYS_FIRST_POST_ONLY = [
        "allAuthors",
        "firstPostOnly",
        "useTitles",
    ]
    KEYS_ALL_POSTS = [
        "isExcluded",
        "oldTopicId",
        "linkText",
        # TODO if published is set it should be the creationDate
        # (lastUpdate -> empty)
        # 'published',
        # 'tags',
    ]
    KEYS_FROM_DB_CACHE = ["postTime", "author", "subject", "isVisible"]
    KEYS = KEYS_FIRST_POST_ONLY + KEYS_ALL_POSTS + KEYS_FROM_DB_CACHE

    def __init__(self, kwargs=None, text=None):
        """WARNING: all public attributes are written as meta data"""
        self.allAuthors = ""
        self.isExcluded = False
        """add this set to ``True`` to a post that should be excluded"""
        self.linkText = None  # TODO needed?
        """text that should be used if linked to here"""
        self.firstPostOnly = True
        """If this is ``True`` in any post only this post wil be used."""
        self.oldTopicId = None
        """ID of the topic that the article originated from"""
        self.useTitles = True
        self.postTime = None
        self.isVisible = True
        self.author = ""
        self.subject = ""
        assert kwargs or text
        self._populate_from_kwargs(kwargs)
        self._populate_from_text(text)

    def __repr__(self):
        return str(self.as_dict)

    def __contains__(self, item):
        return item in self.as_dict

    @property
    def as_dict(self):
        return self._make_dict()

    def _make_dict(self, isFirstPost=True):
        d = {}
        for name in sorted(vars(self)):
            if not self.is_metadata(name):
                continue

            if not isFirstPost and name in self.KEYS_FIRST_POST_ONLY:
                continue

            attr = getattr(self, name)
            if not attr:
                continue

            if attr in ["True", "False"]:
                attr = True if attr == "True" else False

            d[name] = attr
        return d

    def is_metadata(self, name):
        return name in self.KEYS and not name.startswith("_")

    @property
    def _invalid_keys(self):
        return [
            name
            for name in vars(self)
            if name not in self.KEYS and not name.startswith("_")
        ]

    def _populate_from_kwargs(self, kwargs):
        if not kwargs:
            return

        for key, value in kwargs.items():
            self._update(key, str(value))

    def _populate_from_text(self, text):
        if not text:
            return

        raw_md = extract_from_bbcode(ADFD.META_TAG, text)
        if not raw_md:
            return

        lines = raw_md.split("\n")
        for line in lines:
            if not line.strip():
                continue

            key, value = line.split(":", maxsplit=1)
            self._update(key, value)

    def _update(self, key, value):
        key = key.strip()
        value = str(value).strip()
        if value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False
        log.debug(f"{self.__class__.__name__}: {key} -> {value}")
        setattr(self, key, value)
