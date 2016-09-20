import logging
import yaml
from collections import OrderedDict

from plumbum import LocalPath

log = logging.getLogger(__name__)


def get_structure():
    # TODO add possibility to load from a special Post
    dsc = ordered_load(open(LocalPath(__file__).dirname / 'structure.yml'))
    log.debug(dsc)
    rootKey = next(iter(dsc))
    structure = Structure(rootKey, dsc[rootKey])
    return structure


def ordered_load(stream, Loader=yaml.SafeLoader,
                 object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    # noinspection PyUnresolvedReferences
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


# Todo Generate Navigation from this as well

class Structure:
    """Recursive description of a site structure

    plan for navigation / structure hybrid

    * when building site description also build a mapping viewPath -> topicId
    * look up topic ID in FlatPagesWithDBAccess from path
    * done
    """
    rootKey = "home"
    sep = "|"

    def __init__(self, rootKey, value, weight=1):
        self.name, self.mainTopicId = self._parse(rootKey)
        self.weight = weight
        self.contents = []
        self._add_data(value, self.contents, weight)

    def __repr__(self):
        return ("<%s | %s -> %s (weight: %s)>" %
                (self.name, self.mainTopicId, self.contents, self.weight))

    # FIXME makes not much sense here, move to navigation
    # @property
    # def breadcrumbs(self):
    #     # TODO fetch titles
    #     crumbs = [self.mainTopicId]
    #     parent = self.parent
    #     while parent:
    #         crumbs.append(parent.mainTopicId)
    #         parent = parent.parent
    #     return list(reversed(crumbs))

    @classmethod
    def _parse(cls, data):
        sd = data.split("|")
        if len(sd) > 2:
            raise ValueError("Too many '%s' in %s" % (cls.sep, data))

        title = sd[0].strip()
        title = title if title.lower() != cls.rootKey else ""
        mainTopicId = int(sd[1].strip()) if len(sd) == 2 else 0
        return title, mainTopicId

    def _add_data(self, data, contents, weight):
        if isinstance(data, list):
            for idx, item in enumerate(data, start=1):
                self._add_data(item, contents, self.weight + idx)
        elif isinstance(data, int):
            contents.append(data)
        else:
            assert isinstance(data, OrderedDict), data
            key = next(iter(data))
            contents.append(Structure(key, data[key], weight))
