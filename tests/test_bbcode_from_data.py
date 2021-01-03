import logging

import pytest

from adfd.parse import AdfdParser, ADFD_PARSER
from adfd.process import RE

log = logging.getLogger(__name__)


# TODO adapt to known tags and re add
UNSEMANTIC = [
    ("[B]hello world[/b]", "<strong>hello world</strong>"),
    ("[b][i]test[/i][/b]", "<strong><em>test</em></strong>"),
    ("[b][i]test[/b][/i]", "<strong><em>test</em></strong>"),
    ("[b]hello [i]world[/i]", "<strong>hello <em>world</em></strong>"),
    ("[b]hello [ world[/b]", "<strong>hello [ world</strong>"),
    ("[b]]he[llo [ w]orld[/b]", "<strong>]he[llo [ w]orld</strong>"),
    ("[b]hello [] world[/b]", "<strong>hello  world</strong>"),
    # ('[b]hello [] world[/b]', '<strong>hello [] world</strong>'),
    ("[b\n oops [i]i[/i] forgot[/b]", "[b\n oops <em>i</em> forgot"),
    (
        "[ b ] hello [u] world [/u] [ /b ]",
        '<strong> hello <span style="text-decoration: underline;"> '
        "world </span> </strong>",
    ),
    ("[/asdf][/b]", "[/asdf]"),
    ("[b]over[i]lap[/b]ped[/i]", "<strong>over<em>lap</em></strong>ped"),
    ("line one[hr]line two", "line one<hr>\nline two"),
    (
        "[color=red]hey now [url=apple.com]link[/url][/color]",
        '<span style="color:red;">hey now <a '
        'href="http://apple.com">link</a></span>',
    ),
    ("[color red]this is red[/color]", '<span style="color:red;">this is red</span>'),
    ("[color]nothing[/color]", "nothing"),
    ("[color=<script></script>]xss[/color]", '<span style="color:inherit;">xss</span>'),
    ("[COLOR=red]hello[/color]", '<span style="color:red;">hello</span>'),
    (
        '[color="red; font-size:1000px;"]test[/color]',
        '<span style="color:red;">test</span>',
    ),
    ("[color=#f4f4C3 barf]hi[/color]", '<span style="color:#f4f4C3;">hi</span>'),
    ("[color='red']single[/color]", '<span style="color:red;">single</span>'),
]

KITCHEN_SINK = (
    (
        "<http://foo.com/bla_bla>",
        '&lt;<a href="http://foo.com/bla_bla">http://foo.com/bla_bla</a>&gt;',
    ),
    ("hello :[ world", "hello :[ world"),
    ("[tag][soup][/tag]", "[tag][soup][/tag]"),
    ("[list]\n[*]one\n[*]two\n[/list]", "<ul><li>one</li><li>two</li></ul>"),
    (
        "[list=1]\n[*]one\n[*]two\n[/list]",
        '<ol style="list-style-type:decimal;"><li>one</li><li>two</li></ol>',
    ),
    (
        "[list] [*]Entry 1 [*]Entry 2 [*]Entry 3   [/list]",
        "<ul><li>Entry 1</li><li>Entry 2</li><li>Entry 3</li></ul>",
    ),
    (
        "[list]\n[*]item with[code]some\ncode[/code] and text after[/list]",
        "<ul><li>item with<pre><code>some\ncode</code></pre>\n "
        "and text after</li></ul>",
    ),
    (
        "[code python]lambda code: [code] + [1, 2][/code]",
        "<pre><code>lambda code: [code] + [1, 2]</code></pre>",
    ),
    (">> hey -- a dash...", "&gt;&gt; hey &ndash; a dash&#8230;"),
    (
        "[url]http://foo.com/s.php?some--data[/url]",
        '<a href="http://foo.com/s.php?some--data">http://foo.com/s.php'
        "?some--data</a>",
    ),
    ("[url=apple.com]link[/url]", '<a href="http://apple.com">link</a>'),
    (
        "www.apple.com blah foo.com/bar",
        '<a href="http://www.apple.com">www.apple.com</a> blah <a '
        'href="http://foo.com/bar">foo.com/bar</a>',
    ),
    ('[url="<script>alert(1);</script>"]xss[/url]', ""),
    ("[URL=apple.com]link[/URL]", '<a href="http://apple.com">link</a>'),
    ("[url=relative/url.html]link[/url]", '<a href="relative/url.html">link</a>'),
    ("[url=/absolute/url.html]link[/url]", '<a href="/absolute/url.html">link</a>'),
    ("[url=test.html]page[/url]", '<a href="test.html">page</a>'),
    # Tests to make sure links don't get cosmetic replacements.
    (
        "[url=http://test.com/my--page]test[/url]",
        '<a href="http://test.com/my--page">test</a>',
    ),
    (
        "http://test.com/my...page(c)",
        '<a href="http://test.com/my...page(c)">http://test.com/my...page(' "c)</a>",
    ),
    (
        "multiple http://apple.com/page link http://foo.com/foo--bar test",
        'multiple <a href="http://apple.com/page">http://apple.com/page</a> '
        'link <a href="http://foo.com/foo--bar">http://foo.com/foo--bar</a> '
        "test",
    ),
    (
        '[url=http://foo.com]<script>alert("XSS");</script>[/url]',
        '<a href="http://foo.com">&lt;script&gt;alert('
        "&quot;XSS&quot;);&lt;/script&gt;</a>",
    ),
    (
        "[url]123\" onmouseover=\"alert('Hacked');[/url]",
        '<a href="123&quot; onmouseover=&quot;alert('
        '&#39;Hacked&#39;);">123&quot; onmouseover=&quot;alert('
        "&#39;Hacked&#39;);</a>",
    ),
    ('[url]javascript:alert("XSS");[/url]', ""),
    ("[url]\x01javascript:alert(1)[/url]", ""),
    ("[url]javascript\x01:alert(1)[/url]", ""),
    ("[url]vbscript:alert(1)[/url]", ""),
    (
        'http://www.google.com"onmousemove="alert(\'XSS\');"',
        '<a href="http://www.google.com%22onmousemove=%22alert('
        '\'XSS\')">http://www.google.com"onmousemove="alert('
        "'XSS')</a>;&quot;",
    ),
    (
        "[url=data:text/html;base64,"
        "PHNjcmlwdD5hbGVydCgiMSIpOzwvc2NyaXB0Pg==]xss[/url]",
        "",
    ),
    (
        "http://github.com/ http://example.org http://github.com/dcwatson/",
        '<a href="http://github.com/">http://github.com/</a> <a '
        'href="http://example.org">http://example.org</a> <a '
        'href="http://github.com/dcwatson/">http://github.com/dcwatson/</a>',
    ),
)

LINKS = [
    "http://foo.com/blah_blah",
    "(Something like http://foo.com/blah_blah)",
    "http://foo.com/blah_blah_(wikipedia)",
    "http://foo.com/more_(than)_one_(parens)",
    "(Something like http://foo.com/blah_blah_(wikipedia))",
    "http://foo.com/blah_(wikipedia)#cite-1",
    "http://foo.com/blah_(wikipedia)_blah#cite-1",
    "http://foo.com/(something)?after=parens",
    "http://foo.com/blah_blah.",
    "http://foo.com/blah_blah/.",
    "<http://foo.com/blah_blah>",
    "<http://foo.com/blah_blah/>",
    "http://foo.com/blah_blah,",
    "http://www.extinguishedscholar.com/wpglob/?p=364.",
    "<tag>http://example.com</tag>",
    "Just a www.example.com link.",
    "http://example.com/something?with,commas,in,url, but not at end",
    "bit.ly/foo",
    "http://asdf.xxxx.yyyy.com/vvvvv/PublicPages/Login.aspx?ReturnUrl",
    "=%2fvvvvv%2f(asdf@qwertybean.com/qwertybean)",
]

QUOTES = [
    ("[quote]bla[/quote]", "<blockquote><p>bla</p></blockquote>"),
    (
        "[quote]bla[quote]blubb[/quote][/quote]",
        "<blockquote><p>bla<blockquote><p>blubb</p>" "</blockquote></p></blockquote>",
    ),
    ("[quote]bla\n\nblubb[/quote]", "<blockquote><p>bla<br><br>blubb</p></blockquote>"),
    (
        "[quote] \r\ntesting\nstrip [/quote]",
        "<blockquote><p>testing<br>strip</p></blockquote>",
    ),
]


class TestAdfdParser:
    parser = ADFD_PARSER

    @pytest.mark.parametrize(("src", "expected"), KITCHEN_SINK)
    def test_format(self, src, expected):
        tokens = self.parser.tokenize(src)
        result = self.parser._format_tokens(tokens, None).strip()
        assert result == expected

    @pytest.mark.parametrize("link", LINKS)
    def test_links(self, link):
        link = link.strip()
        num = len(RE.URL.findall(link))
        assert num == 1, 'Found %d links in "%s"' % (num, link)

    @pytest.mark.xfail(reason="new quote format not yet clear")
    @pytest.mark.parametrize(("src", "expected"), QUOTES)
    def test_quotes(self, src, expected):
        tokens = self.parser.tokenize(src)
        result = self.parser._format_tokens(tokens, None).strip()
        assert result == expected

    def test_parse_opts(self):
        tag, opts = self.parser._parse_opts(
            'url="http://test.com/s.php?a=bcd efg"  popup'
        )
        assert tag == "url"
        assert opts == {"url": "http://test.com/s.php?a=bcd efg", "popup": ""}
        tag, opts = self.parser._parse_opts('tag sep="=" flag=1')
        assert tag == "tag"
        assert opts == {"sep": "=", "flag": "1"}
        tag, opts = self.parser._parse_opts(" quote opt1 opt2 author = Watson, Dan   ")
        assert tag == "quote"
        assert opts == {"author": "Watson, Dan", "opt1": "", "opt2": ""}
        tag, opts = self.parser._parse_opts("quote = Watson, Dan")
        assert tag == "quote"
        assert opts == {"quote": "Watson, Dan"}
        tag, opts = self.parser._parse_opts("""Quote='Dan "Darsh" Watson'""")
        assert tag == "quote"
        assert opts == {"quote": 'Dan "Darsh" Watson'}

    def test_strip(self):
        result = self.parser.strip(
            "[em]hello \n[mod]world[/mod][/em] -- []", strip_newlines=True
        )
        # NOTE that empty bracket pairs are also stripped ...
        assert result == "hello world -- "
        parser = AdfdParser(tagOpener="<", tagCloser=">", dropUnrecognized=True)
        result = parser.strip(
            '<div class="test"><b>hello</b> <pre>world</pre>'
            '<img src="test.jpg" /></div>'
        )
        assert result == "hello world"

    def test_linker(self):
        def _contextual_link(url, context):
            return '<a href="{}" target="_blank">{}</a>'.format(
                url,
                context["substitution"],
            )

        def _link(url):
            return _contextual_link(url, {"substitution": url})

        # Test noncontextual linker
        p = AdfdParser(linker=_link)
        s = p._format_tokens(p.tokenize("hello www.apple.com world"), None)
        assert s == (
            'hello <a href="www.apple.com" ' 'target="_blank">www.apple.com</a> world'
        )
        # Test contextual linker
        p = AdfdParser(linker=_contextual_link, linkerTakesContext=True)
        s = p._format_tokens(
            p.tokenize("hello www.apple.com world"), None, substitution="oh hai"
        )
        assert s == (
            'hello <a href="www.apple.com" ' 'target="_blank">oh hai</a> world'
        )

    def test_unicode(self):
        src = "[em]ƒünk¥ • §tüƒƒ[/em]"
        dst = "<em>ƒünk¥ • §tüƒƒ</em>"
        tokens = self.parser.tokenize(src)
        result = self.parser._format_tokens(tokens, None)
        assert result.strip() == dst
