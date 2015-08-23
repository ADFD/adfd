from plumbum import LocalPath
import pytest
from adfd.article import Article


@pytest.fixture(scope='module', autouse=True)
def article_class_with_test_path(request):
    oldArticlesPath = Article.ARTICLES_PATH
    Article.ARTICLES_PATH = LocalPath(__file__).up() / 'data' / 'articles'

    def finalizer():
        Article.ARTICLES_PATH = oldArticlesPath

    request.addfinalizer(finalizer)


class TestArticle(object):
    def test_rel_path(self):
        a = Article('kitchen-sink')
        assert 'Lorem ipsum dolor sit amet' in a.content
        assert isinstance(a.metadataDict, dict)

    def test_topic_id_path(self):
        a = Article(1)
        assert a.content == ("some text from first post\n\n"
                             "some text from second post\n")
        assert isinstance(a.metadataDict, dict)
