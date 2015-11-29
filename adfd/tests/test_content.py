import logging
import pytest

from plumbum import LocalPath

from adfd import cst
from adfd.content import TopicFinalizer, Metadata, prepare

log = logging.getLogger(__name__)


@pytest.fixture()
def fakeRawPath(request):
    fakePath = LocalPath(__file__).dirname / 'data' / 'content'
    fakeRawPath = fakePath / cst.DIR.RAW

    def finalizer():
        pass

    request.addfinalizer(finalizer)
    return fakeRawPath


class TestPreparator(object):
    def test_preparation(self, fakeRawPath):
        prepare(fakeRawPath)


class TestArticle(object):
    def test_topic_id_path(self):
        a = TopicFinalizer(1)
        assert a.content == (
            "söme text from first pöst\n\n\nsome text from second post\n")
        assert isinstance(a.md, Metadata)

    def test_slug_transliteration(self):
        a = TopicFinalizer(1)
        assert a.md.title == 'Söme snaßy Tätle'
        assert a.md.slug == 'soeme-snassy-taetle'


class TestMetadata(object):
    def test_populate_from_text(self):
        text = 'bla\n[meta]title: supertitle[/meta]\nblubb'
        md = Metadata(text=text)
        assert md.title == 'supertitle'
