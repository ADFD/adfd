# -*- coding: utf-8 -*-
import logging
import re

from adfd import bbcode


log = logging.getLogger(__name__)


class AdfdPrimer(object):
    """Very stupid and rigid preprocessor/sanity checker for articles"""
    MIN_HEADER_LEN = len("[hx]A[/hx]")
    HEADER_START_PAT = r'\[h(\d)'
    HEADER_END_PAT = r'/h(\d)\]'
    QUOTE_START = '[quote]'
    QUOTE_END = '[/quote]'

    def __init__(self, text):
        self.text = text

    def add_paragraphs(self, lines):
        newTokens = []
        for line in lines:
            if line and self.is_paragraph(line):
                line = u"[p]%s[/p]" % (line)
            newTokens.append(line)
        return newTokens

    @property
    def primedText(self):
        quoted = self.format_quotes(self.strippedLines)
        paragraphed = self.add_paragraphs(quoted)
        return "\n".join(paragraphed)

    def is_paragraph(self, line):
        return not self.is_header_line(line) and not self.is_quote_marker(line)

    @classmethod
    def is_header_line(cls, line, strict=True):
        if len(line) < cls.MIN_HEADER_LEN:
            return False

        try:
            startMatcher = re.match(cls.HEADER_START_PAT, line[:3])
            endMatcher = re.match(cls.HEADER_END_PAT, line[-4:])
            matches = [m for m in [startMatcher, endMatcher] if m]
            if not matches:
                return False

            if len(matches) == 1:
                raise BadHeader(line)

            startLevel = startMatcher.group(1)
            endLevel = endMatcher.group(1)
            if startLevel != endLevel:
                raise BadHeader(line)

            return True

        except BadHeader:
            if strict:
                raise

        except Exception as e:
            log.error("%s exception while processing '%s'" % (type(e), line))
            raise

    @classmethod
    def is_quote_marker(cls, text):
        return cls.is_quote_start(text) or text == cls.QUOTE_END

    @property
    def strippedLines(self):
        """lines stripped of surrounding whitespace and last empty line"""
        lines = [t.strip() for t in self.text.split('\n')]
        if not lines[-1]:
            lines.pop()
        return lines

    @classmethod
    def format_quotes(cls, lines):
        qa = cls.QUOTE_START
        qe = cls.QUOTE_END
        mutatedLines = []
        for line in lines:
            if line.count('[quote') > 1 or line.count('/quote]') > 1:
                raise BadQuotes("Can't cope with more than one quote per line")

            if cls.is_quote_start(line):
                author = cls.get_quote_author(line)
                tag = u'[quote="%s"]' % (author) if author else cls.QUOTE_START
                line = line[len(tag):]
                mutatedLines.append(tag)
            mutatedLines.append(line.replace(qa, '').replace(qe, ''))
            if line.endswith(qe):
                mutatedLines.append(qe)
        return mutatedLines

    @classmethod
    def is_quote_start(cls, text):
        if text.startswith(cls.QUOTE_START):
            return True

        if cls.get_quote_author(text):
            return True

    @classmethod
    def get_quote_author(cls, text):
        if not text.startswith(cls.QUOTE_START[:-1]):
            return

        matcher = re.match('\[quote="(.*)"\].*', text)
        return matcher.group(1) if matcher else None


class BadHeader(Exception):
    pass


class BadQuotes(Exception):
    pass


class AdfdParser(bbcode.Parser):
    HEADER_TAGS = ['h%s' % (i) for i in range(1, 6)]

    def __init__(self, *args, **kwargs):
        super(AdfdParser, self).__init__(*args, **kwargs)
        self.add_default_formatters()
        self.add_custom_formatters()

    def format(self, data, **context):
        """Format input text using any installed renderers.

        Any context keyword arguments given here will be passed along to
        the render functions as a context dictionary.
        """
        tokens = self.fix_whitespace(self.tokenize(data))
        # data = self.add_sections(self.tokenize(data))
        _, tokens = Paragrafenreiter.wrap(0, tokens, '')
        return self._format_tokens(tokens, None, **context)

    def add_sections(self, tokens):
        """wrap all orphan data in <p> tags"""
        mutatedText = []
        hasNoSections = True
        idx = 0
        while idx < len(tokens):
            tokenType, tag, options, text = tokens[idx]
            if tag in self.HEADER_TAGS:
                if '/' in text:
                    mutatedText.append(text)
                    mutatedText.append("\n[section]")
                else:
                    if hasNoSections:
                        hasNoSections = False
                    else:
                        mutatedText.append("[/section]\n")
                    mutatedText.append(text)
            else:
                mutatedText.append(text)
            idx += 1
        text = "".join(mutatedText)
        if hasNoSections:
            text = "[section]\n%s[/section]\n" % (text)
        else:
            text += "[/section]\n"  # clode last section
        print text
        return text

    def fix_whitespace(self, tokens):
        """normalize text to only contain single or no empty lines"""
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
        self.add_simple_formatter('u', '<u>%(value)s</u>')
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
        return '<span style="color:%(color)s;">%(value)s</span>' % {
            'color': color,
            'value': value}

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


class Paragrafenreiter(object):
    START = AdfdParser.TOKEN_TAG_START
    END = AdfdParser.TOKEN_TAG_END
    BREAK = AdfdParser.TOKEN_NEWLINE
    DATA = AdfdParser.TOKEN_DATA
    P_START = (START, u'p', {}, u'[p]')
    P_END = (END, u'p', {}, u'[/p]')
    SECTIONING_START_TAGS = ['blockquote']

    @classmethod
    def wrap(cls, idx, tokens, endTagName):
        wrappedTokens = []
        while idx < len(tokens):
            curToken = tokens[idx]
            wrappedTokens.append(curToken)
            tType, name = curToken[:2]
            idx += 1
            if name in AdfdParser.HEADER_TAGS and tType == cls.START:
                curToken = tokens[idx]
                wrappedTokens.append(curToken)
                idx += 1
                curToken = tokens[idx]
                wrappedTokens.append(curToken)
                idx += 1
                wrappedTokens.append(cls.P_START)
                idx, consumedTokens = cls.wrap(idx, tokens, name)
                wrappedTokens.append(consumedTokens)
                wrappedTokens.append(cls.P_END)

            elif name == endTagName:
                break

            else:
                wrappedTokens.append(cls.P_START)
                idx, consumedTokens = cls.wrap(idx, tokens, name)
                wrappedTokens.append(consumedTokens)
                wrappedTokens.append(cls.P_END)

        return idx, wrappedTokens
