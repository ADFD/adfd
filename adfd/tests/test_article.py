from flexmock import flexmock


class TestPost(object):
    def test_url_refers_to_this(self):
        structure = (
            ('absetzen', (Topic(9913), )),
            ('heilen', (Topic(20), )),
            ('hilfen', (Topic(8997), )),)
        for path, infoBits in structure:
            for infObj in infoBits:
                print "%s %s" % (infObj, infObj.url_refers_to_this(
                    'http://www.adfd.org/austausch/viewtopic.php?f=46&t=20'))
                print "%s %s" % (infObj, infObj.url_refers_to_this(
                    'http://www.adfd.org/austausch/viewtopic.php?p=9954'))
                print "%s %s" % (infObj, infObj.url_refers_to_this(
                    'http://www.adfd.org/austausch/viewtopic.php?p=53'))
                print infObj.slug


class TestTopic(object):
    def test_url_refers_to_this(self):
        structure = (
            ('', (Topic(postIds=9950),
                  Topic(postIds=[9954]))),
            ('hintergrund', (Topic(postIds=96731), )),)
        for path, infoBits in structure:
            for infObj in infoBits:
                print "%s %s" % (infObj, infObj.url_refers_to_this(
                    'http://www.adfd.org/austausch/viewtopic.php?f=46&t=20'))
                print "%s %s" % (infObj, infObj.url_refers_to_this(
                    'http://www.adfd.org/austausch/viewtopic.php?p=9954'))
                print "%s %s" % (infObj, infObj.url_refers_to_this(
                    'http://www.adfd.org/austausch/viewtopic.php?p=53'))
                print infObj.slug
                print


class TestArticle(object):
    CONTENT = (
        '.. title: Willkommen im ADFD\n'
        '.. slug :  index \n'
        '.. date:   2012-03-30 23:00:00 UTC-03:00  \n'
        '.. tags: wahrheit\n'
        '.. author: Oliver Bestwalter\n'
        '.. link: http://adfd.org\n'
        '   \n'
        'asdasda')

    def test_slug(self):
        aMock = flexmock(Article)
        aMock.should_receive('content').and_return(self.CONTENT)
        a = Article('some/path')
        assert a.slug == 'index'

    def test_content(self):
        """just load this file and see if it arrives :)"""
        a = Article(__file__)
        assert 'just load this file and see if it arrives :)' in a.content

    def test_subject(self):
        """just load this file and see if it arrives :)"""
        oldVal = cst.SITE.IMPORT_PATH
        try:
            cst.SITE.IMPORT_PATH = plumbum.LocalPath('')
            a = Article(__file__)
        finally:
            cst.SITE.IMPORT_PATH = oldVal
        assert 'just load this file and see if it arrives :)' in a.content
