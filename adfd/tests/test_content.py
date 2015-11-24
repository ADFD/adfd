import logging
import pytest

from plumbum import LocalPath

from adfd import cst
from adfd.content import Article, Metadata

log = logging.getLogger(__name__)


@pytest.fixture(scope='module', autouse=True)
def article_class_with_test_path(request):
    fakePath = LocalPath(__file__).dirname / 'data' / 'content'
    log.info('serving articles from %s' % (fakePath))
    oldTopicsPath = cst.PATH.TOPICS
    oldStaticPath = cst.PATH.STATIC
    cst.PATH.TOPICS = fakePath / cst.DIR.TOPICS
    cst.PATH.STATIC = fakePath / cst.DIR.STATIC

    def finalizer():
        cst.PATH.TOPICS = oldTopicsPath
        cst.PATH.STATIC = oldStaticPath

    request.addfinalizer(finalizer)


class TestArticle(object):
    def test_rel_path(self):
        a = Article('test-kitchen-sink')
        assert 'Lorem ipsum dolor sit amet' in a.content
        assert isinstance(a.md, Metadata)

    def test_topic_id_path(self):
        a = Article(1)
        a.remove_prepared_files()
        assert a.content == (
            "söme text from first pöst\n\nsome text from second post\n")
        assert isinstance(a.md, Metadata)

    def test_slug_transliteration(self):
        a = Article(1)
        a.remove_prepared_files()
        assert a.title == 'Söme snaßy Tätle'
        assert a.slug == 'soeme-snassy-taetle'


class TestMetadata(object):
    def test_populate_from_text(self):
        text = 'bla\n[meta]title: supertitle[/meta]\nblubb'
        md = Metadata(text=text)
        assert md.title == 'supertitle'
