from adfd.cnf import PATH


def test_site_repo_is_available():
    """For many tests, site repo needs to be checked out"""
    print(PATH.SITE_REPO)
    print(PATH.SITE_REPO.up().list())
    assert (PATH.SITE_REPO / ".git").exists()
