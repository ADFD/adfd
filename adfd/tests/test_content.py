import logging
import pytest

from plumbum import LocalPath

from adfd import cst
from adfd.conf import PATH
from adfd.content import TopicFinalizer, PageMetadata, prepare, TopicPreparator

log = logging.getLogger(__name__)


@pytest.fixture()
def fakePaths(request):
    fakePath = LocalPath(__file__).dirname / 'data' / 'content'
    fakeRawPath = fakePath / cst.DIR.RAW
    fakeDstPath = fakePath / cst.DIR.PREPARED
    oldPrepPath = PATH.CNT_PREPARED
    PATH.CNT_PREPARED = fakeDstPath

    def finalizer():
        PATH.CNT_PREPARED = oldPrepPath
        fakeDstPath.delete()

    request.addfinalizer(finalizer)
    return fakeRawPath, fakeDstPath


class TestPreparator(object):
    def test_preparation(self, fakePaths):
        prepare(*fakePaths)


class TestArticle(object):
    def test_topic_id_path(self, fakePaths):
        srcPath, dstPath = fakePaths

        p = TopicPreparator(srcPath / '00001', dstPath)
        p.prepare()
        a = TopicFinalizer(1)
        assert a.inContent == (
            "söme text from first pöst\n\n\nsome text from second post\n")
        assert isinstance(a.md, PageMetadata)

    def test_slug_transliteration(self, fakePaths):
        srcPath, dstPath = fakePaths
        p = TopicPreparator(srcPath / '00001', dstPath)
        p.prepare()
        a = TopicFinalizer(1)
        assert a.md.title == 'Söme snaßy Tätle'
        assert a.md.slug == 'soeme-snassy-taetle'


class TestMetadata(object):
    def test_populate_from_text(self):
        text = 'bla\n[meta]title: supertitle[/meta]\nblubb'
        md = PageMetadata(text=text)
        assert md.title == 'supertitle'
