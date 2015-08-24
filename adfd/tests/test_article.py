import logging
from plumbum import LocalPath
import pytest
from adfd.article import Article


log = logging.getLogger(__name__)


@pytest.fixture(scope='module', autouse=True)
def article_class_with_test_path(request):
    oldArticlesPath = Article.ARTICLES_PATH
    Article.ARTICLES_PATH = LocalPath(__file__).up() / 'data' / 'content'
    log.info('serving articles from %s' % (Article.ARTICLES_PATH))

    def finalizer():
        Article.ARTICLES_PATH = oldArticlesPath

    request.addfinalizer(finalizer)


class TestArticle(object):
    def test_rel_path(self):
        a = Article('test-kitchen-sink')
        assert 'Lorem ipsum dolor sit amet' in a.content
        assert isinstance(a.metadataDict, dict)

    def test_topic_id_path(self):
        a = Article(1)
        assert a.content == (
            "some text from first post\n\nsome text from second post\n")
        assert isinstance(a.metadataDict, dict)

    def test_slug_prefixing_is_idempotent(self):
        a1 = Article('test-kitchen-sink')
        originalDictItems = a1.metadataDict.items()
        assert a1.slug == 'test-kitchen-sink'
        a2 = Article('test-kitchen-sink', 'some/prefix')
        assert a2.slug == 'some/prefix/test-kitchen-sink'
        a2a = Article('test-kitchen-sink', 'some/prefix')
        assert a2a.slug == 'some/prefix/test-kitchen-sink'
        a3 = Article('test-kitchen-sink')
        assert a3.slug == 'test-kitchen-sink'
        assert a3.metadataDict.items() == originalDictItems
