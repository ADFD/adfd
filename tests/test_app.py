from flexmock import flexmock
import pytest

from adfd.site.controller import app, NAV


@pytest.fixture
def tc():
    app.config['TESTING'] = True
    return app.test_client()


class TestApp:
    def test_basic(self, tc):
        navMock = flexmock(NAV)
        navMock.should_receive('pathNodeMap')\
            .and_return({"/": flexmock(article=flexmock())})
        navMock.should_receive('nav').and_return("")
        rv = tc.get('/')
        txt = rv.data.decode()
        assert 'body' in txt
