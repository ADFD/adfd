# -*- coding: utf-8 -*-
import logging
import re


from adfd import bbcode

log = logging.getLogger(__name__)


class AdfdParser(bbcode.Parser):
    HEADER_TAGS = ['h%s' % (i) for i in range(1, 6)]

    def __init__(self, *args, **kwargs):
        try:
            self.data = kwargs.pop('data')
        except KeyError:
            self.data = None
        super(AdfdParser, self).__init__(*args, **kwargs)
        self.add_default_formatters()
        self.add_custom_formatters()
        if self.data:
            self.tokens = self.tokenize(self.data)
        else:
            self.tokens = None

    def to_html(self, data=None, **context):
        """Format input text using any installed renderers.

        Any context keyword arguments given here will be passed along to
        the render functions as a context dictionary.
        """
        if data:
            tokens = self.tokenize(data)
        else:
            tokens = self.tokens
        tokens = self.fix_whitespace(tokens)
        assert tokens
        return self._format_tokens(tokens, parent=None, **context)

    def fix_whitespace(self, tokens=None):
        """normalize text to only contain single or no empty lines"""
        tokens = tokens or self.tokens
        assert tokens
        fixedTokens = []
        lastToken = [None]
        for token in tokens:
            if token[0] == self.TOKEN_NEWLINE:
                if self.is_block_display_token(lastToken[1]):
                    continue

            if (lastToken[0] == self.TOKEN_NEWLINE and
                    token[0] == self.TOKEN_NEWLINE):
                    continue

            fixedTokens.append(token)
            lastToken = token
        return fixedTokens

    def add_default_formatters(self):
        self._add_simple_default_formatters()
        self._add_img_formatter()
        self._add_color_formatter()
        self._add_list_formatter()
        self._add_quote_formatter()
        self._add_url_formatter()

    def add_custom_formatters(self):
        self._add_simple_custom_formatters()
        self._add_bbvideo_formatter()
        self._add_header_formatters()
        self._add_section_formatter()

    def _add_simple_custom_formatters(self):
        self.add_simple_formatter('p', '<p>%(value)s</p>')
        self.add_simple_formatter('br', '<br>\n', standalone=True)
        self.add_simple_formatter('hr', '<hr>\n', standalone=True)
        # todo use foundation way for centering
        self.add_simple_formatter(
            'center', '<div style="text-align:center;">%(value)s</div>\n')

    def _add_simple_default_formatters(self):
        self.add_simple_formatter('b', '<strong>%(value)s</strong>')
        self.add_simple_formatter(
            'code', '<code>%(value)s</code>\n', render_embedded=False,
            transform_newlines=False, swallow_trailing_newline=True)
        self.add_simple_formatter('i', '<em>%(value)s</em>')
        self.add_simple_formatter('s', '<strike>%(value)s</strike>')
        self.add_simple_formatter(
            'u', '<span style="text-decoration: underline;">%(value)s</span>')
        self.add_simple_formatter('sub', '<sub>%(value)s</sub>')
        self.add_simple_formatter('sup', '<sup>%(value)s</sup>')

    def _add_bbvideo_formatter(self):
        self.add_formatter('BBvideo', self._render_bbvideo,
                           replace_links=False, replace_cosmetic=False)

    # noinspection PyUnusedLocal
    @staticmethod
    def _render_bbvideo(name, value, options, parent, context):
        width, height = options['bbvideo'].strip().split(',')
        dataMap = {'width': width, 'height': height, 'url': value}
        return (
            '<a href="%(url)s" class="bbvideo" '
            'data-bbvideo="%(width)s,%(height)s" '
            'target="_blank">%(url)s</a>' % (dataMap))

    def _add_color_formatter(self):
        self.add_formatter('color', self._render_color)

    # noinspection PyUnusedLocal
    @staticmethod
    def _render_color(name, value, options, parent, context):
        if 'color' in options:
            color = options['color'].strip()
        elif options:
            color = list(options.keys())[0].strip()
        else:
            return value

        match = re.match(r'^([a-z]+)|^(#[a-f0-9]{3,6})', color, re.I)
        color = match.group() if match else 'inherit'
        return '<span style="color:%s;">%s</span>' % (color, value)

    def _add_img_formatter(self):
        self.add_formatter(
            'img', self._render_img, replace_links=False,
            replace_cosmetic=False)

    # noinspection PyUnusedLocal
    @staticmethod
    def _render_img(name, value, options, parent, context):
        href = value
        # Only add http:// if it looks like it starts with a domain name.
        if '://' not in href and bbcode._domainRegex.match(href):
            href = 'http://' + href
        return '<img src="%s">' % (href.replace('"', '%22'))

    def _add_list_formatter(self):
        self.add_formatter(
            'list', self._render_list, transform_newlines=False,
            strip=True, swallow_trailing_newline=True)
        # Make sure transform_newlines = False for [*], so [code]
        # tags can be embedded without transformation.
        self.add_simple_formatter(
            '*', '<li>%(value)s</li>', newline_closes=True,
            transform_newlines=False, same_tag_closes=True, strip=True)

    # noinspection PyUnusedLocal
    @staticmethod
    def _render_list(name, value, options, parent, context):
        listType = (
            options['list'] if (options and 'list' in options) else '*')
        cssOpts = {
            '1': 'decimal', '01': 'decimal-leading-zero',
            'a': 'lower-alpha', 'A': 'upper-alpha',
            'i': 'lower-roman', 'I': 'upper-roman'}
        tag = 'ol' if listType in cssOpts else 'ul'
        css = (' style="list-style-type:%s;"' % cssOpts[listType] if
               listType in cssOpts else '')
        return '<%s%s>%s</%s>\n' % (tag, css, value, tag)

    def _add_header_formatters(self):
        for tag in self.HEADER_TAGS:
            demotedTag = tag[0] + str(int(tag[1]) + 1)
            self.add_simple_formatter(
                tag, '<%s>%%(value)s</%s>\n' % (demotedTag, demotedTag))

    def _add_quote_formatter(self):
        self.add_formatter(
            'quote', self._render_quote, transform_newlines=False,
            strip=True, swallow_trailing_newline=True)

    # noinspection PyUnusedLocal
    @staticmethod
    def _render_quote(name, value, options, parent, context):
        """see http://html5doctor.com/blockquote-q-cite/"""
        author = (options['quote'] if (options and 'quote' in options) else '')
        cite = "<footer><cite>%s</cite></footer>" % (author) if author else ''
        return '<blockquote>%s%s</blockquote>' % (value, cite)

    def _add_section_formatter(self):
        self.add_formatter(
            'section', self._render_section, transform_newlines=False,
            strip=True, swallow_trailing_newline=True)

    # noinspection PyUnusedLocal
    @staticmethod
    def _render_section(name, value, options, parent, context):
        return '<section>%s</section>' % (value)

    def _add_url_formatter(self):
        self.add_formatter('url', self._render_url, replace_links=False,
                           replace_cosmetic=False)

    # noinspection PyUnusedLocal
    @staticmethod
    def _render_url(name, value, options, parent, context):
        if options and 'url' in options:
            # Option values are not escaped for HTML output.
            href = bbcode._replace(
                options['url'], bbcode.REPLACE_ESCAPE)
        else:
            href = value
        # Completely ignore javascript: and data: "links".
        if (re.sub(r'[^a-z0-9+]', '', href.lower().split(':', 1)[0]) in
                ('javascript', 'data', 'vbscript')):
            return ''

        # Only add http:// if it looks like it starts with a domain name.
        if '://' not in href and bbcode._domainRegex.match(href):
            href = 'http://' + href
        return '<a href="%s">%s</a>' % (href.replace('"', '%22'), value)
