import logging
from collections import OrderedDict

from adfd.cnf import SITE
from adfd.exc import NotAnAttribute
from adfd.parse import extract_from_bbcode

log = logging.getLogger(__name__)


class PageMetadata:
    """
    For overriding this directly from post contents the bbcode tag
    ``meta`` has to be defined on the board.

    The following settings to be done in ``adm/index.php?i=acp_bbcodes``
    define the tag and make it invisible if the post is viewed directly.

    BBCODE use:

        [meta]{TEXT}[/meta]

    BBCODE replacement:

        <span style="display: none;">[meta]{TEXT}[/meta]</span>
    """
    ATTRIBUTES = [
        'allAuthors',
        'author',
        'isExcluded',
        'linkText',
        'slug',
        'title',
        'useTitles',
    ]

    def __init__(self, kwargs=None, text=None):
        """WARNING: all public attributes are written as meta data"""
        self.allAuthors = None
        self.author = None
        self.authorId = None
        self.isExcluded = False
        self.linkText = None
        """text that should be used if linked to here ??? Needed?"""
        self.slug = None
        self.title = None
        self.useTitles = True
        assert kwargs or text
        self._populate_from_kwargs(kwargs)
        self._populate_from_text(text)

    def __repr__(self):
        return str(self.asDict)

    @property
    def asDict(self):
        dict_ = OrderedDict()
        for name in sorted(vars(self)):
            if name.startswith('_'):
                continue

            if name not in self.ATTRIBUTES:
                raise NotAnAttribute(name)

            attr = getattr(self, name)
            if not attr:
                continue

            if attr in ['True', 'False']:
                attr = True if attr == 'True' else False

            dict_[name] = attr
        return dict_

    def _populate_from_kwargs(self, kwargs):
        if not kwargs:
            return

        for key, value in kwargs.items():
            self._update(key, str(value))

    def _populate_from_text(self, text):
        if not text:
            return

        rawMd = extract_from_bbcode(SITE.META_TAG, text)
        if not rawMd:
            return

        lines = rawMd.split('\n')
        for line in lines:
            assert isinstance(line, str)  # pycharm is strange sometimes
            if not line.strip():
                continue

            key, value = line.split(':', maxsplit=1)
            self._update(key.strip(), value.strip())

    def _update(self, key, value):
        value = str(value).strip()
        log.debug('%s: %s -> %s', self.__class__.__name__, key, value)
        setattr(self, key, value)
