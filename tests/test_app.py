from flexmock import flexmock
import pytest

from adfd.site.controller import app, navigator


@pytest.fixture
def tc():
    app.config['TESTING'] = True
    return app.test_client()


class TestApp:
    def test_basic(self, tc):
        navMock = flexmock(navigator)
        navMock.should_receive('populate').once()
        navMock.should_receive('pathNodeMap')\
            .and_return({"/": flexmock(article=flexmock())})
        navMock.should_receive('menuAsString').and_return("")
        rv = tc.get('/')
        txt = rv.data.decode()
        assert 'body' in txt
