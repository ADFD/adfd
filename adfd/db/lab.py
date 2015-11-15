from adfd.db.export import Forum, SoupKitchen, Topic
from adfd.db.utils import obj_attr


def soup_kitchen():
    sk = SoupKitchen()
    # print(sk.fetch_topic_ids_from_forum(6))
    # print(sk.fetch_post_ids_from_topic(10397))
    print(sk.fetch_post(115499).post_text)
    # print(sk.get_username(0))
    assert 0


def forum():
    f = Forum(35)
    print(obj_attr(f))


def topic():
    t = Topic(9403)
    print(obj_attr(t))

if __name__ == '__main__':
    # forum()
    topic()
