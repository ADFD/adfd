import pytest

from adfd.site.controller import app


@pytest.fixture
def tc():
    app.config['TESTING'] = True
    return app.test_client()


class TestApp:
    def test_basic(self, tc):
        rv = tc.get('/')
        txt = rv.data.decode()
        assert 'body' in txt
