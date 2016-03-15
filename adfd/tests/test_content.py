import logging

import pytest
from plumbum import LocalPath

from adfd.conf import PATH, DIR
from adfd.content import TopicFinalizer, prepare_topics, TopicPreparator
from adfd.metadata import PageMetadata


log = logging.getLogger(__name__)


@pytest.fixture()
def fakePaths(request):
    fakePath = LocalPath(__file__).dirname / 'data' / 'content'
    fakeRawPath = fakePath / DIR.RAW
    fakeDstPath = fakePath / DIR.PREPARED
    oldPrepPath = PATH.CNT_PREPARED
    PATH.CNT_PREPARED = fakeDstPath

    def finalizer():
        PATH.CNT_PREPARED = oldPrepPath
        fakeDstPath.delete()

    request.addfinalizer(finalizer)
    return fakeRawPath, fakeDstPath


class TestPreparator:
    def test_preparation(self, fakePaths):
        prepare_topics(*fakePaths)


class TestFinalize:
    def test_topic_id_path(self, fakePaths):
        srcPath, dstPath = fakePaths
        p = TopicPreparator(srcPath / '00001', dstPath)
        p.prepare()
        a = TopicFinalizer(1)
        assert isinstance(a.md, PageMetadata)
        assert a.inContent == (
            "söme text from first pöst\n\n\nsome text from second post\n")

    def test_exclude_posts(self, fakePaths):
        srcPath, dstPath = fakePaths
        p = TopicPreparator(srcPath / '00002', dstPath)
        p.prepare()
        a = TopicFinalizer(2)
        assert isinstance(a.md, PageMetadata)
        assert 'as it is excluded' not in a.inContent

    def test_include_posts(self, fakePaths):
        srcPath, dstPath = fakePaths
        p = TopicPreparator(srcPath / '00003', dstPath)
        p.prepare()
        a = TopicFinalizer(3)
        assert isinstance(a.md, PageMetadata)
        assert 'as it is excluded' not in a.inContent

    def test_slug_transliteration(self, fakePaths):
        srcPath, dstPath = fakePaths
        p = TopicPreparator(srcPath / '00001', dstPath)
        p.prepare()
        a = TopicFinalizer(1)
        assert a.md.title == 'Söme snaßy Tätle'
        assert a.md.slug == 'soeme-snassy-taetle'


class TestMetadata:
    def test_populate_from_text(self):
        text = 'bla\n[meta]title: supertitle[/meta]\nblubb'
        md = PageMetadata(text=text)
        assert md.title == 'supertitle'
