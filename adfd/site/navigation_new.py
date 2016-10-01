import io
import logging
import re
from collections import (
    Mapping, MutableMapping, Sequence, Set, ItemsView, OrderedDict)

from boltons.iterutils import remap
import yaml

from adfd.cnf import SITE
from adfd.model import CategoryNode, ArticleNode

log = logging.getLogger(__name__)


class Navigator:
    def __init__(self):
        self.pathNodeMap = {}
        self.identifierNodeMap = {}
        self.structure = StructureLoader.load()

    def transform(self):
        remap(self.structure,
              visit=self.visit, enter=self.enter, exit=self.exit)

    @staticmethod
    def visit(path, key, value):
        print('visit(%r, %r, %r)' % (path, key, value))
        if isinstance(key, str):
            key = CategoryNode(key)
        elif isinstance(value, int):
            value = ArticleNode(value)
        return key, value

    @staticmethod
    def enter(path, key, value):
        print('enter(%r, %r, %r)' % (path, key, value))
        try:
            iter(value)
        except TypeError:
            return value, False
        if isinstance(value, str):
            return value, False
        elif isinstance(value, Mapping):
            return value.__class__(), ItemsView(value)
        elif isinstance(value, Sequence):
            return value.__class__(), enumerate(value)
        elif isinstance(value, Set):
            return value.__class__(), enumerate(value)
        return value, False

    @staticmethod
    def exit(path, key, oldParent, newParent, newItems):
        print('exit(%r, %r, %r, %r, %r)' %
              (path, key, oldParent, newParent, newItems))
        ret = newParent
        if isinstance(newParent, MutableMapping):
            newParent.update(newItems)
        elif isinstance(newParent, Sequence):
            values = [v for i, v in newItems]
            try:
                # noinspection PyUnresolvedReferences
                newParent.extend(values)
            except AttributeError:
                ret = newParent.__class__(values)  # tuples
        # elif isinstance(newParent, Set):
        #     values = [v for i, v in newItems]
        #     try:
        #         # noinspection PyUnresolvedReferences
        #         newParent.update(newItems)
        #     except AttributeError:
        #         ret = newParent.__class__(values)  # frozensets
        else:
            raise RuntimeError('unexpected iterable: %r' % type(newParent))

        return ret


class StructureLoader:
    @classmethod
    def load(cls):
        if SITE.USE_FILE:
            return cls.ordered_yaml_load(stream=open(SITE.STRUCTURE_PATH))

        from adfd.model import Post
        post = Post(SITE.STRUCTURE_POST_ID)
        # FIXME extract to function/method extract_tag_content and reuse
        regex = re.compile(r'\[code\](.*)\[/code\]', re.MULTILINE | re.DOTALL)
        match = regex.search(post.content)
        stream = io.StringIO(match.group(1))
        return cls.ordered_yaml_load(stream=stream)

    @classmethod
    def ordered_yaml_load(cls, stream):
        class OrderedLoader(yaml.SafeLoader):
            pass

        def construct_mapping(loader, node):
            loader.flatten_mapping(node)
            return OrderedDict(loader.construct_pairs(node))

        # noinspection PyUnresolvedReferences
        OrderedLoader.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            construct_mapping)
        return yaml.load(stream, OrderedLoader)
