# -*- coding: utf-8 -*-
import re
from adfd import bbcode


class AdfdParser(bbcode.Parser):
    def __init__(self, *args, **kwargs):
        super(AdfdParser, self).__init__(*args, **kwargs)
        self._add_simple_formatters()
        self._add_color_formatter()
        self._add_list_formatter()
        self._add_quote_formatter()
        self._add_url_formatter()
        self._add_header_formatters()

    def _add_simple_formatters(self):
        self.add_simple_formatter('br', '<br>', standalone=True)
        self.add_simple_formatter('b', '<strong>%(value)s</strong>')
        self.add_simple_formatter(
            'center', '<div style="text-align:center;">%(value)s</div>')
        self.add_simple_formatter(
            'code', '<code>%(value)s</code>', render_embedded=False,
            transform_newlines=False, swallow_trailing_newline=True)
        self.add_simple_formatter('hr', '<hr>', standalone=True)
        self.add_simple_formatter('i', '<em>%(value)s</em>')
        self.add_simple_formatter('s', '<strike>%(value)s</strike>')
        self.add_simple_formatter('u', '<u>%(value)s</u>')
        self.add_simple_formatter('sub', '<sub>%(value)s</sub>')
        self.add_simple_formatter('sup', '<sup>%(value)s</sup>')

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
        return '<span style="color:%(color)s;">%(value)s</span>' % {
            'color': color,
            'value': value}

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
        list_type = (
            options['list'] if (options and 'list' in options) else '*')
        css_opts = {
            '1': 'decimal', '01': 'decimal-leading-zero',
            'a': 'lower-alpha', 'A': 'upper-alpha',
            'i': 'lower-roman', 'I': 'upper-roman'}
        tag = 'ol' if list_type in css_opts else 'ul'
        css = (' style="list-style-type:%s;"' % css_opts[list_type] if
               list_type in css_opts else '')
        return '<%s%s>%s</%s>' % (tag, css, value, tag)

    def _add_header_formatters(self):
        # self.add_simple_formatter('h1', '<h1>%(value)s</h1>')
        for i in range(1, 6):
            self.add_simple_formatter(
                'h%d' % (i), '<h%d>%%(value)s</h%d>' % (i+1, i+1))

    def _add_quote_formatter(self):
        self.add_formatter(
            'quote', self._render_quote, transform_newlines=False,
            strip=True, swallow_trailing_newline=True)

    # noinspection PyUnusedLocal
    @staticmethod
    def _render_quote(name, value, options, parent, context):
        author = (options['quote'] if (options and 'quote' in options) else '')
        cite = "<footer><cite>%s</cite></footer>" % (author) if author else ''
        return '<blockquote>%s%s</blockquote>' % (value, cite)

    def _add_url_formatter(self):
        self.add_formatter(
            'url', self._render_url, replace_links=False,
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
        if '://' not in href and bbcode._domain_re.match(href):
            href = 'http://' + href
        return '<a href="%s">%s</a>' % (href.replace('"', '%22'), value)
