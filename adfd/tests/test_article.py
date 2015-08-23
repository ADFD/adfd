from adfd.article import Article


class TestArticle(object):
    def test_rel_path(self):
        a = Article('kitchen-sink')
        assert a.content
        assert isinstance(a.metadataDict, dict)

    def test_topic_id_path(self):
        a = Article(68)
        assert a.content
        assert isinstance(a.metadataDict, dict)
