"""
resolve links that point to the board but now should point to the
corresponding website article


* create anchor with the topic ID at the beginning of the article
* create anchors with the post ID at the beginning of the section
* create lookup table from all converted articles
* convert board links to website links
"""
from adfd.db.export import harvest_topic_ids
from adfd.site_description import SITE_DESCRIPTION

topicIds = harvest_topic_ids(SITE_DESCRIPTION)
print(topicIds)
