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
from collections import OrderedDict

from adfd.cnf import SITE
from adfd.exc import NotAnAttribute
from adfd.parse import extract_from_bbcode

log = logging.getLogger(__name__)


class PageMetadata:
    ATTRIBUTES = [
        'allAuthors',
        'isExcluded',
        'firstPostOnly',
        'oldTopicId',
        'linkText',
        'useTitles',
        # 'tags',
    ]

    def __init__(self, kwargs=None, text=None):
        """WARNING: all public attributes are written as meta data"""
        self.allAuthors = []
        self.isExcluded = False
        """add this set to ``True`` to a post that should be excluded"""
        self.linkText = None  # TODO needed?
        """text that should be used if linked to here"""
        self.firstPostOnly = True
        """If this is ``True`` in any post only this post wil be used."""
        self.oldTopicId = None
        """ID of the topic that the article originated from"""
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
            self._update(key, value)

    def _update(self, key, value):
        key = key.strip()
        value = str(value).strip()
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        log.debug('%s: %s -> %s', self.__class__.__name__, key, value)
        setattr(self, key, value)
