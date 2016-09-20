import logging

import pytest
from plumbum import LocalPath

from adfd.cnt.massage import TopicFinalizer
from adfd.cnt.metadata import PageMetadata
from adfd.cst import PATH, DIR


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


# TODO load filecontents in SQLITE db?
@pytest.mark.xfail(reason="switched to id based access")
class TestFinalize:
    def test_topic_id_path(self, fakePaths):
        srcPath, dstPath = fakePaths
        # TODO create topic from srcPath / '00001'
        # p = TopicPreparator(srcPath / '00001', dstPath)
        p.prepare()
        a = TopicFinalizer(1)
        assert isinstance(a.md, PageMetadata)
        assert a.inContent == (
            "söme text from first pöst\n\n\nsome text from second post\n")

    @pytest.mark.xfail(reason="should be tested directly on slug - not here")
    def test_slug_transliteration(self, fakePaths):
        # FIXME see xfail reason
        srcPath, dstPath = fakePaths
        # TODO create topic from srcPath / '00001'
        # p = TopicPreparator(srcPath / '00001', dstPath)
        p.prepare()
        a = TopicFinalizer(1)
        assert a.md.title == 'Söme snaßy Tätle'
        assert 'soeme-snassy-taetle' in a.md.slug


class TestMetadata:
    def test_populate_from_text(self):
        text = 'bla\n[meta]title: supertitle[/meta]\nblubb'
        md = PageMetadata(text=text)
        assert md.title == 'supertitle'
