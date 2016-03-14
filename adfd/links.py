"""
resolve links that point to the board but now should point to the
corresponding website article


* create anchor with the topic ID at the beginning of the article
* create anchors with the post ID at the beginning of the section
* create lookup table from all converted articles
* convert board links to website links
"""


class LinkInformer:
    FORUM_LINK_HINT = 'adfd.org/austausch'

    def __init__(self, topics):
        """
        :type topics: list Topic
        """
        self.topics = topics

    def get_website_link(self, url):
        if self.FORUM_LINK_HINT not in url:
            return None


if __name__ == '__main__':
    from adfd.db.export import harvest_topic_ids
    from adfd.site_description import SITE_DESCRIPTION

    topicIds = harvest_topic_ids(SITE_DESCRIPTION)
    print(topicIds)
