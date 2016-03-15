import pytest
from plumbum import LocalPath

from sitebuilder.views import app


@pytest.fixture
def tc():
    app.config['TESTING'] = True
    app.config['FLATPAGES_ROOT'] = (
        str(LocalPath(__file__).dirname.up(2) / 'adfd/tests/data/fake_final'))
    return app.test_client()


class TestApp:
    def test_basic(self, tc):
        rv = tc.get('/')
        txt = rv.data.decode()
        assert 'body' in txt
