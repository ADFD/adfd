class PostDoesNotExist(Exception):
    """A post with the given ID does not exist"""


class TopicDoesNotExist(Exception):
    """A topic contains no posts"""


class TopicNotAccessible(Exception):
    """A topic is in a private forum and not explicitly whitelisted"""


class NotAnAttribute(Exception):
    """A key is not an attribute"""


class NotOverridable(Exception):
    """A key is not configured as overridable overriden (e.g. postId)"""
