import logging
import pytest

from plumbum import LocalPath

from adfd.article import Article

log = logging.getLogger(__name__)


@pytest.fixture(scope='module', autouse=True)
def article_class_with_test_path(request):
    oldArticlesPath = Article.SRC_PATH
    Article.SRC_PATH = LocalPath(__file__).up() / 'data' / 'content'
    log.info('serving articles from %s' % (Article.SRC_PATH))

    def finalizer():
        Article.SRC_PATH = oldArticlesPath

    request.addfinalizer(finalizer)


class TestArticle(object):
    def test_rel_path(self):
        a = Article('test-kitchen-sink')
        assert 'Lorem ipsum dolor sit amet' in a.content
        assert isinstance(a.md, dict)

    def test_topic_id_path(self):
        a = Article(1)
        assert a.content == (
            "söme text from first pöst\n\nsome text from second post\n")
        assert isinstance(a.md, dict)

    def test_slug_transliteration(self):
        a = Article(1)
        assert a.title == 'Söme snaßy Tätle'
        assert a.slug == 'soeme-snassy-taetle'
