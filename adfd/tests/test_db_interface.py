from adfd.cst import DB_URL


def test_db_connection_sets_encoding():
    """This has bitten me and it's not in VCS, so I check it here"""
    assert DB_URL.endswith('?charset=utf8')
