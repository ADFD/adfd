import logging

from adfd.structure import Navigator, Container


log = logging.getLogger(__name__)


class TestNavigator:
    def test_elems(self):
        navi = Navigator()
        assert navi.elems
        assert navi.allUrls

    def test_active_element(self):
        navi = Navigator()
        navigation = navi.generate_navigation(
            '/bbcode/spezielle-bbcode-formatierungen')
        assert ('<li style="text-weight: bold;">'
                '<a href="/bbcode/spezielle-bbcode-formatierungen">'
                'Spezielle BBCode Formatierungen</a></li>') in navigation


class TestContainer:
    def test_categroy(self):
        c = Container('hintergruende/geschichte')
        print(c.isCategory)
        print(c.isPage)
        # print(c.find_categories())
        for cat in c.find_categories():
            print(cat.name, cat.md.weight)
        for cat in c.find_pages():
            print(cat.name, cat.md.weight)

        # print(c.find_categories())
        # print(c.find_pages())
        # print(obj_attr(p))
        # p = Page(path=LocalPath('bbcode'))
        # p = Page(path=LocalPath('bbcode/spezielle-bbcode-formatierungen'))
        # print(obj_attr(p))
        # print(obj_attr(p, excludeAttrs=['content']))
        # print(obj_attr(p2, excludeAttrs=['content']))
