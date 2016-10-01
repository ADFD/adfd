import logging
from collections import (
    Mapping, MutableMapping, Sequence, Set, ItemsView)

from adfd.model import CategoryNode, ArticleNode, StructureLoader
from boltons.iterutils import remap

log = logging.getLogger(__name__)


class Navigator:
    def __init__(self):
        self.pathNodeMap = {}
        self.identifierNodeMap = {}
        self.structure = StructureLoader.load()

    def transform(self):
        return remap(self.structure,
                     visit=self.visit, enter=self.enter, exit=self.exit)

    @staticmethod
    def visit(path, key, value):
        print('visit(%r, %r, %r)' % (path, key, value))
        if isinstance(key, str):
            key = CategoryNode(key)
        elif isinstance(value, int):
            value = ArticleNode(value)
        elif isinstance(value, str):
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
