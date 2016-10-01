import collections as col
import logging

from boltons.iterutils import remap

from adfd.model import CategoryNode, ArticleNode, StructureLoader

log = logging.getLogger(__name__)


class Navigator:
    def __init__(self):
        self.pathNodeMap = {}
        self.identifierNodeMap = {}
        self.yamlKeyNodeMap = {}

        self.structure = StructureLoader.load()
        self.rootKey = next(iter(self.structure))
        # fixme do this only with remap
        # self.pathNodeMap = {"/": self.root}
        # self.identifierNodeMap = {self.root.identifier: self.root}
        self.thingy = self.transform(self.structure)

    def transform(self, menu):
        return remap(menu, visit=self.visit, enter=self.enter, exit=self.exit)

    def visit(self, path, key, value):
        print('visit(%r, %r, %r)' % (path, key, value))
        node = None
        if isinstance(key, str):
            node = self.get_cat_node(key=key)
        elif isinstance(value, (int, str)):
            node = ArticleNode(value)
        if path and node:
            cat = self.get_cat_node(path=path)
            cat.children.append(node)
        else:
            print('empty_visit(%r, %r, %r)' % (path, key, value))
        return key, value

    def get_cat_node(self, key=None, path=None):
        key = key or path[-1]
        try:
            return self.yamlKeyNodeMap[key]

        except KeyError:
            key = key if not isinstance(key, int) else path[-2]
            try:
                return self.yamlKeyNodeMap[key]

            except KeyError:
                cat = CategoryNode(key)
                self.yamlKeyNodeMap[key] = cat
                return cat

    def enter(self, path, key, value):
        print('enter(%r, %r, %r)' % (path, key, value))
        try:
            iter(value)
        except TypeError:
            return value, False
        if isinstance(value, str):
            return value, False
        elif isinstance(value, col.Mapping):
            return value.__class__(), col.ItemsView(value)
        elif isinstance(value, col.Sequence):
            return value.__class__(), enumerate(value)
        elif isinstance(value, col.Set):
            return value.__class__(), enumerate(value)
        return value, False

    def exit(self, path, key, oldParent, newParent, newItems):
        print('exit(%r, %r, %r, %r, %r)' %
              (path, key, oldParent, newParent, newItems))
        ret = newParent
        if isinstance(newParent, col.MutableMapping):
            newParent.update(newItems)
        elif isinstance(newParent, col.Sequence):
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
