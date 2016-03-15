class PostDoesNotExist(Exception):
    """A post with the given ID does not exist"""


class TopicDoesNotExist(Exception):
    """A topic contains no posts"""


class ForumDoesNotExist(Exception):
    """A forum does not exist"""


class ForumIsEmpty(Exception):
    """A forum contains no topics"""


class TopicNotFound(Exception):
    """A raw path of the topic is not found"""


class PathMissing(Exception):
    """Trying to dump a file without knowing the path"""


class NotAnAttribute(Exception):
    """A key is not an attribute"""


class NotOverridable(Exception):
    """A key is not configured as overridable overriden (e.g. postId)"""


class MutuallyExclusiveMetadata(Exception):
    """Two metadata values are set that are mutually exclusive"""
