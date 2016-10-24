class PostDoesNotExist(Exception):
    """A post with the given ID does not exist"""


class TopicDoesNotExist(Exception):
    """A topic contains no posts"""


class TopicNotAccessible(Exception):
    """A topic is in a private forum and not explicitly whitelisted"""
