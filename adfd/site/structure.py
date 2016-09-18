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


class Structure:
    """Description of a site structure as a tree of descriptions
    containing a list of descriptions and topic ids"""
    rootKey = "home"
    sep = "|"

    def __init__(self, rootKey, value):
        self.name, self.mainTopicId = self.get_data(rootKey)
        self.contents = []
        self.construct_description(value, self.contents)

    def __repr__(self):
        return "<%s | %s -> %s>" % (self.name, self.mainTopicId, self.contents)

    @classmethod
    def get_data(cls, data):
        sd = data.split("|")
        if len(sd) > 2:
            raise ValueError("Too many '%s' in %s" % (cls.sep, data))

        title = sd[0].strip()
        title = title if title.lower() != cls.rootKey else ""
        mainTopicId = int(sd[1].strip()) if len(sd) == 2 else 0
        return title, mainTopicId

    @classmethod
    def construct_description(cls, data, contents):
        if isinstance(data, list):
            for item in data:
                cls.construct_description(item, contents)
        elif isinstance(data, int):
            contents.append(data)
        else:
            assert isinstance(data, OrderedDict), data
            key = next(iter(data))
            contents.append(Structure(key, data[key]))
