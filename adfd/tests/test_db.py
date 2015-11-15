from adfd.db.export import Forum, SoupKitchen


def test_soup_kitchen():
    sk = SoupKitchen()
    # print(sk.fetch_topic_ids_from_forum(6))
    # print(sk.fetch_post_ids_from_topic(10397))
    print(sk.fetch_post(115499).post_text)
    # print(sk.get_username(0))
    assert 0


# def test_forum():
#     f = Forum(35)
#     print(f)
