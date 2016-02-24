import itertools
import re

from cached_property import cached_property
from pyphen import Pyphen
from typogrify.filters import amp, smartypants, initial_quotes, widont

from adfd.conf import PARSE, RE
from adfd.utils import Replacer


class TagOptions:
    tagName = None
    """name of the tag - all lowercase"""
    newlineCloses = False
    """a newline should automatically close this tag"""
    sameTagCloses = False
    """another start of the same tag should close this tag"""
    standalone = False
    """this tag does not have a closing tag"""
    renderEmbedded = True
    """tags should be rendered inside this tag"""
    transformNewlines = True
    """newlines should be converted to markup"""
    escapeHtml = True
    """HTML characters (<, >, and &) should be escaped inside this tag"""
    replaceLinks = True
    """URLs should be replaced with link markup inside this tag"""
    replaceCosmetic = True
    """perform cosmetic replacements (elipses, dashes, etc.) in tag"""
    strip = False
    """leading and trailing whitespace should be stripped inside tag"""
    swallowTrailingNewline = False
    """tag should swallow first trailing newline (i.e. for block elements)"""

    def __init__(self, tagName, **kwargs):
        self.tagName = tagName
        for attr, value in list(kwargs.items()):
            setattr(self, attr, bool(value))


class Token:
    @staticmethod
    def _escape_html(text):
        return Replacer.replace(text, Replacer.HTML_ESCAPE)

    # fixme likely not needed
    @staticmethod
    def _untypogrify(text):
        def untypogrify_char(c):
            return '"' if c in ['“', '„'] else c

        return ''.join([untypogrify_char(c) for c in text])

    @staticmethod
    def _hyphenate(text, hyphen='&shy;'):
        py = Pyphen(lang=PARSE.PYPHEN_LANG)
        words = text.split(' ')
        return ' '.join([py.inserted(word, hyphen=hyphen) for word in words])

    TEXT_TRANSFORMERS = [
        _escape_html, amp, smartypants, initial_quotes, widont, _hyphenate]

    def __init__(self, *args):
        self.type, self.tag, self.options, self._text = args
        self.isOpener = self.type == Parser.TOKEN_TAG_START
        self.isCloser = self.type == Parser.TOKEN_TAG_END
        self.isHeaderStart = self.isOpener and re.match("h\d", self.tag)
        self.isQuoteStart = self.isOpener and self.tag == "quote"
        self.isQuoteEnd = self.isCloser and self.tag == "quote"
        self.isListStart = self.isOpener and self.tag == "list"
        self.isListEnd = self.isCloser and self.tag == "list"
        self.isNewline = self.type == Parser.TOKEN_NEWLINE

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        if self.tag:
            return "<%s%s>" % ('/' if self.isCloser else '', self.tag)

        return "<%s>" % (self.text)

    @property
    def asTuple(self):
        return (self.type, self.tag, self.options, self.text)

    @cached_property
    def text(self):
        """enhance text with hyphenation and typogrification"""
        if not self._text:
            return self._text

        modifiedText = self._text
        for transformer in self.TEXT_TRANSFORMERS:
            modifiedText = transformer(modifiedText)
        return modifiedText


class Parser:
    TOKEN_TAG_START = 'start'
    TOKEN_TAG_END = 'end'
    TOKEN_NEWLINE = 'newline'
    TOKEN_DATA = 'data'

    def __init__(
            self, newline='\n', normalize_newlines=True,
            escapeHtml=False, replaceLinks=True,
            replaceCosmetic=True, tag_opener='[', tag_closer=']',
            linker=None, linker_takes_context=False, drop_unrecognized=False):
        self.tag_opener = tag_opener
        self.tag_closer = tag_closer
        self.newline = newline
        self.normalize_newlines = normalize_newlines
        self.recognized_tags = {}
        self.drop_unrecognized = drop_unrecognized
        self.escapeHtml = escapeHtml
        self.replaceCosmetic = replaceCosmetic
        self.replaceLinks = replaceLinks
        self.linker = linker
        self.linker_takes_context = linker_takes_context

    def add_formatter(self, tagName, render_func, **kwargs):
        """ Install render function for specified tag name.

        The render function should have the following signature:

            def render(tagName, value, options, parent, context)

        The arguments are as follows:

            tagName
                The name of the tag being rendered.
            value
                context between start and end tags (None for standalone tags).
                Depends on renderEmbedded tag option whether this has
                been rendered.
            options
                A dictionary of options specified on the opening tag.
            parent
                The parent TagOptions, if the tag is being rendered inside
                another tag, otherwise None.
            context
                The keyword argument dictionary passed into the format call.
        """
        options = TagOptions(tagName.strip().lower(), **kwargs)
        self.recognized_tags[options.tagName] = (render_func, options)

    def add_simple_formatter(self, tagName, format_string, **kwargs):
        """Install a formatter.

        Takes the tag options dictionary, puts a value key in it
        and uses it as a format dictionary to the given format string.
        """
        # noinspection PyUnusedLocal
        def _render(name, value, options, parent, context):
            fmt = {}
            if options:
                fmt.update(options)
            fmt.update({'value': value})
            return format_string % fmt
        self.add_formatter(tagName, _render, **kwargs)

    def _newline_tokenize(self, data):
        """
        Given a string that does not contain any tags, this function will
        return a list of NEWLINE and DATA tokens such that if you concatenate
        their data, you will have the original string.
        """
        parts = data.split('\n')
        tokens = []
        for num, part in enumerate(parts):
            if part:
                tokens.append((self.TOKEN_DATA, None, None, part))
            if num < (len(parts) - 1):
                tokens.append((self.TOKEN_NEWLINE, None, None, '\n'))
        return tokens

    def _parse_opts(self, data):
        """Parse options out of given a tag string.

        This function will parse any options and return a tuple of
        (tagName, options_dict).

        Options may be quoted in order to preserve spaces, and free-standing
        options are allowed. The tag name itself may also serve as an option
        if it is immediately followed by an equal
        sign. Here are some examples:

            quote author="Dan Watson"
                tagName=quote, options={'author': 'Dan Watson'}
            url="http://test.com/s.php?a=bcd efg" popup
                tagName=url, options={
                    'url': 'http://test.com/s.php?a=bcd efg', 'popup': ''}
        """
        name = None
        try:
            from collections import OrderedDict
            opts = OrderedDict()
        except:
            opts = {}
        in_value = False
        in_quote = False
        attr = ''
        value = ''
        attr_done = False
        for pos, ch in enumerate(data.strip()):
            if in_value:
                if in_quote:
                    if ch == in_quote:
                        in_quote = False
                        in_value = False
                        if attr:
                            opts[attr.lower()] = value.strip()
                        attr = ''
                        value = ''
                    else:
                        value += ch
                else:
                    if ch in ('"', "'"):
                        in_quote = ch
                    elif ch == ' ' and data.find('=', pos + 1) > 0:
                        # If there is no = after this, value may accept spaces
                        opts[attr.lower()] = value.strip()
                        attr = ''
                        value = ''
                        in_value = False
                    else:
                        value += ch
            else:
                if ch == '=':
                    in_value = True
                    if name is None:
                        name = attr
                elif ch == ' ':
                    attr_done = True
                else:
                    if attr_done:
                        if attr:
                            if name is None:
                                name = attr
                            else:
                                opts[attr.lower()] = ''
                        attr = ''
                        attr_done = False
                    attr += ch
        if attr:
            if name is None:
                name = attr
            opts[attr.lower()] = value.strip()
        return name.lower(), opts

    def _parse_tag(self, tag):
        """
        Given a tag string (characters enclosed by []), this function will
        parse any options and return a tuple of the form:
            (valid, tagName, closer, options)
        """
        if ((not tag.startswith(self.tag_opener)) or
                (not tag.endswith(self.tag_closer)) or
                ('\n' in tag) or ('\r' in tag)):
            return (False, tag, False, None)

        tagName = tag[len(self.tag_opener):-len(self.tag_closer)].strip()
        if not tagName:
            return (False, tag, False, None)

        closer = False
        opts = {}
        if tagName[0] == '/':
            tagName = tagName[1:]
            closer = True
        # Parse options inside the opening tag, if needed.
        if (('=' in tagName) or (' ' in tagName)) and not closer:
            tagName, opts = self._parse_opts(tagName)
        return (True, tagName.strip().lower(), closer, opts)

    def _tag_extent(self, data, start):
        """Find extent of a tag.

        Accounting for option quoting and new tags starting before the
        current one closes.

        Returns (found_close, end_pos) where valid is False if another tag
        started before this one closed.
        """
        in_quote = False
        for i in range(start + 1, len(data)):
            ch = data[i]
            if ch in ('"', "'"):
                if not in_quote:
                    in_quote = ch
                elif in_quote == ch:
                    in_quote = False
            if (not in_quote and
                    data[i:i + len(self.tag_opener)] == self.tag_opener):
                return i, False
            if (not in_quote and
                    data[i:i + len(self.tag_closer)] == self.tag_closer):
                return i + len(self.tag_closer), True
        return len(data), False

    def tokenize(self, data):
        """
        Tokenizes the given string. A token is a 4-tuple of the form:

            (token_type, tagName, tag_options, token_text)

            token_type
                TOKEN_TAG_START, TOKEN_TAG_END, TOKEN_NEWLINE or TOKEN_DATA
            tagName
                The name of the tag if token_type=TOKEN_TAG_*, otherwise None
            tag_options
                dict of options specified for TOKEN_TAG_START, otherwise None
            token_text
                The original token text
        """
        if self.normalize_newlines:
            data = data.replace('\r\n', '\n').replace('\r', '\n')
        pos = 0
        tokens = []
        while pos < len(data):
            start = data.find(self.tag_opener, pos)
            if start >= pos:
                # Check if there was data between this start and the last end
                if start > pos:
                    tl = self._newline_tokenize(data[pos:start])
                    tokens.extend(tl)
                    # noinspection PyUnusedLocal
                    pos = start

                # Find the extent of this tag, if it's ever closed.
                end, found_close = self._tag_extent(data, start)
                if found_close:
                    tag = data[start:end]
                    valid, tagName, closer, opts = self._parse_tag(tag)
                    # Make sure this is a well-formed, recognized tag,
                    # otherwise it's just data
                    if valid and tagName in self.recognized_tags:
                        if closer:
                            tokens.append(
                                (self.TOKEN_TAG_END, tagName, None, tag))
                        else:
                            tokens.append(
                                (self.TOKEN_TAG_START, tagName, opts, tag))
                    elif (valid and self.drop_unrecognized and
                          tagName not in self.recognized_tags):
                        # If we found a valid (but unrecognized) tag and
                        # self.drop_unrecognized is True, just drop it
                        pass
                    else:
                        tokens.extend(self._newline_tokenize(tag))
                else:
                    # We didn't find a closing tag, tack it on as text.
                    tokens.extend(self._newline_tokenize(data[start:end]))
                pos = end
            else:
                # No more tags left to parse.
                break
        if pos < len(data):
            tl = self._newline_tokenize(data[pos:])
            tokens.extend(tl)
        return tokens

    def _find_closing_token(self, tag, tokens, pos):
        """find the position of the closing token.

        Given the current tag options, a list of tokens, and the current
        position in the token list, this function will find the position of the
        closing token associated with the specified tag. This may be a closing
        tag, a newline, or simply the end of the list (to ensure tags are
        closed). This function should return a tuple of the form (end_pos,
        consume), where consume should indicate whether the ending token
        should be consumed or not.
        """
        embed_count = 0
        block_count = 0
        while pos < len(tokens):
            token_type, tagName, tag_opts, token_text = tokens[pos]
            if (tag.newlineCloses and token_type in
                    (self.TOKEN_TAG_START, self.TOKEN_TAG_END)):
                # If we're finding the closing token for a tag that is
                # closed by newlines, but there is an embedded tag that
                # doesn't transform newlines (i.e. a code tag that keeps
                # newlines intact), we need to skip over that.
                inner_tag = self.recognized_tags[tagName][1]
                if not inner_tag.transformNewlines:
                    if token_type == self.TOKEN_TAG_START:
                        block_count += 1
                    else:
                        block_count -= 1
            if (token_type == self.TOKEN_NEWLINE and tag.newlineCloses and
                    block_count == 0):
                # If for some crazy reason there are embedded tags that
                # both close on newline, the first newline will automatically
                # close all those nested tags.
                return pos, True
            elif (token_type == self.TOKEN_TAG_START and
                  tagName == tag.tagName):
                if tag.sameTagCloses:
                    return pos, False
                if tag.renderEmbedded:
                    embed_count += 1
            elif token_type == self.TOKEN_TAG_END and tagName == tag.tagName:
                if embed_count > 0:
                    embed_count -= 1
                else:
                    return pos, True
            pos += 1
        return pos, True

    def _link_replace(self, match, **context):
        """Callback for re.sub to replace link text with markup.

        Turns out using a callback function is actually faster than using
        backrefs, plus this lets us provide a hook for user customization.
        linker_takes_context=True means that the linker gets passed context
        like a standard format function.
        """
        url = match.group(0)
        if self.linker:
            if self.linker_takes_context:
                return self.linker(url, context)
            else:
                return self.linker(url)
        else:
            href = url
            if '://' not in href:
                href = 'http://' + href
            # Escape quotes to avoid XSS, let the browser escape the rest.
            return '<a href="%s">%s</a>' % (href.replace('"', '%22'), url)

    def _transform(self, data, escapeHtml, replaceLinks, replaceCosmetic,
                   **context):
        """Transforms the input string based on the options specified.

        Takes into account if option is enabled globally for this parser.
        """
        url_matches = {}
        if self.replaceLinks and replaceLinks:
            # If we're replacing links in the text (i.e. not those in [url]
            # tags) then we need to be careful to pull them out before doing
            # any escaping or cosmetic replacement.
            pos = 0
            while True:
                match = RE.URL.search(data, pos)
                if not match:
                    break

                # Replace any link with a token that we can substitute back
                # in after replacements.
                token = '{{ bbcode-link-%s }}' % len(url_matches)
                url_matches[token] = self._link_replace(match, **context)
                # noinspection PyUnresolvedReferences
                start, end = match.span()
                data = data[:start] + token + data[end:]
                # To be perfectly accurate, this should probably be
                # len(data[:start] + token), but start will work, because the
                # token itself won't match as a URL.
                pos = start
        if self.escapeHtml and escapeHtml:
            data = Replacer.replace(data, Replacer.HTML_ESCAPE)
        if self.replaceCosmetic and replaceCosmetic:
            data = Replacer.replace(data, Replacer.COSMETIC)
        # Now put the replaced links back in the text.
        for token, replacement in url_matches.items():
            data = data.replace(token, replacement)
        return data

    def _format_tokens(self, tokens, parent, **context):
        idx = 0
        formatted = []
        while idx < len(tokens):
            token_type, tagName, tag_opts, token_text = tokens[idx]
            if token_type == self.TOKEN_TAG_START:
                render_func, tag = self.recognized_tags[tagName]
                if tag.standalone:
                    formatted.append(
                        render_func(tagName, None, tag_opts, parent, context))
                else:
                    # First, find the extent of this tag's tokens.
                    # noinspection PyTypeChecker
                    end, consume = self._find_closing_token(
                        tag, tokens, idx + 1)
                    subtokens = tokens[idx + 1:end]
                    # If the end tag should not be consumed, back up one
                    # (after grabbing the subtokens).
                    if not consume:
                        end -= 1
                    if tag.renderEmbedded:
                        # This tag renders embedded tags, simply recurse.
                        inner = self._format_tokens(subtokens, tag, **context)
                    else:
                        # Otherwise, just concatenate all the token text.
                        inner = self._transform(
                            ''.join([t[3] for t in subtokens]),
                            tag.escapeHtml, tag.replaceLinks,
                            tag.replaceCosmetic, **context)
                    # Strip and replace newlines, if necessary.
                    if tag.strip:
                        inner = inner.strip()
                    if tag.transformNewlines:
                        inner = inner.replace('\n', self.newline)
                    # Append the rendered contents.
                    formatted.append(
                        render_func(tagName, inner, tag_opts,
                                    parent, context))
                    # If the tag should swallow the first trailing newline,
                    # check the token after the closing token.
                    if tag.swallowTrailingNewline:
                        next_pos = end + 1
                        if (next_pos < len(tokens) and
                                tokens[next_pos][0] == self.TOKEN_NEWLINE):
                            end = next_pos
                    # Skip to the end tag.
                    idx = end
            elif token_type == self.TOKEN_NEWLINE:
                # If this is a top-level newline, replace it. Otherwise,
                # it will be replaced (if necessary) by the code above.
                formatted.append(self.newline if parent is None
                                 else token_text)
            elif token_type == self.TOKEN_DATA:
                escape = (self.escapeHtml if parent is None else
                          parent.escapeHtml)
                links = (self.replaceLinks if parent is None
                         else parent.replaceLinks)
                cosmetic = (self.replaceCosmetic if parent is None
                            else parent.replaceCosmetic)
                formatted.append(
                    self._transform(token_text, escape, links,
                                    cosmetic, **context))
            idx += 1
        return ''.join(formatted)

    def strip(self, data, strip_newlines=False):
        """Strip out any tags from the input text.

        Using the same tokenization as the formatter.
        """
        text = []
        for token_type, tagName, tag_opts, token_text in self.tokenize(data):
            if token_type == self.TOKEN_DATA:
                text.append(token_text)
            elif token_type == self.TOKEN_NEWLINE and not strip_newlines:
                text.append(token_text)
        return ''.join(text)


class Chunk:
    """Forms token groups to fix missing formatting in forum articles"""
    HEADER = 'header'
    PARAGRAPH = 'paragraph'
    QUOTE = 'quote'
    LIST = 'list'
    TYPES = [HEADER, PARAGRAPH, QUOTE, LIST]

    def __init__(self, tokens, chunkType):
        self.tokens = tokens
        self.chunkType = chunkType
        self.clean()
        self.modify()

    def __repr__(self):
        return " ".join([str(c) for c in self.tokens])

    def modify(self):
        """this innocent method is the reason why we have chunks"""
        if self.isEmpty:
            return

        if self.chunkType == self.PARAGRAPH:
            startToken = Token(Parser.TOKEN_TAG_START, 'p', None, '[p]')
            endToken = Token(Parser.TOKEN_TAG_END, 'p', None, '[/p]')
            self.tokens.insert(0, startToken)
            self.tokens.append(endToken)

    @cached_property
    def tokensAsTuples(self):
        return [t.asTuple for t in self.tokens]

    def clean(self):
        """remove newlines at beginning and end of chunk"""
        for idx in [0, -1]:
            try:
                while self.tokens[idx].isNewline:
                    self.tokens.pop(idx)
            except IndexError:
                pass

    @cached_property
    def isEmpty(self):
        if not self.tokens:
            return True

        for token in self.tokens:
            if not token.isNewline:
                return False


class Chunkman:
    """create chunks specific to forum articles for preparation"""
    def __init__(self, tokens):
        self.tokens = [Token(*t) for t in tokens]
        self._chunks = []

    @cached_property
    def flattened(self):
        return list(itertools.chain(*[c.tokensAsTuples for c in self.chunks]))

    @cached_property
    def chunks(self):
        """article chunks which can be converted individually

        :rtype: list of list of TransformableChunk
        """
        currentTokens = []
        idx = 0
        while idx < len(self.tokens):
            token = self.tokens[idx]
            if token.isHeaderStart:
                currentTokens = self.flush(currentTokens)
                newIdx = idx + 3
                self.flush(self.tokens[idx:newIdx], Chunk.HEADER)
                idx = newIdx
                continue

            if token.isQuoteStart:
                self.flush(currentTokens)
                sIdx = idx
                while not token.isQuoteEnd:
                    idx += 1
                    token = self.tokens[idx]
                idx += 1
                currentTokens = self.flush(self.tokens[sIdx:idx], Chunk.QUOTE)
                continue

            if token.isListStart:
                self.flush(currentTokens)
                sIdx = idx
                while not token.isListEnd:
                    idx += 1
                    token = self.tokens[idx]
                idx += 1
                currentTokens = self.flush(self.tokens[sIdx:idx], Chunk.LIST)
                continue

            if self.is_block_change(self.tokens, idx):
                currentTokens = self.flush(currentTokens)
                idx += 1
                continue

            currentTokens.append(token)
            idx += 1

        self.flush(currentTokens)
        return self._chunks

    def flush(self, tokens, chunkType=Chunk.PARAGRAPH):
        """append cleaned tokens and return a fresh (empty) list"""
        chunk = Chunk(tokens, chunkType)
        if not chunk.isEmpty:
            self._chunks.append(chunk)
        return []

    def is_block_change(self, tokens, idx):
        try:
            nextToken = tokens[idx + 1]
            return tokens[idx].isNewline and nextToken.isNewline

        except IndexError:
            pass


class AdfdParser(Parser):
    ORPHAN_MATCHER = re.compile(r'^<p></p>')
    HEADER_TAGS = ['h%s' % (i) for i in range(1, 6)]
    DEMOTION_LEVEL = 1  # number of levels header tags get demoted

    def __init__(self, *args, **kwargs):
        super(AdfdParser, self).__init__(*args, **kwargs)
        self._add_formatters()

    def to_html(self, data=None, tokens=None, **context):
        """Format input text using any installed renderers.

        Any context keyword arguments given here will be passed along to
        the render functions as a context dictionary.
        """
        if data:
            assert not tokens, tokens
            tokens = Chunkman(self.tokenize(data)).flattened
        assert tokens
        html = self._format_tokens(tokens, parent=None, **context).strip()
        return self.cleanup(html)

    def cleanup(self, text):
        out = []
        for line in text.split('\n'):
            if not line.strip():
                continue

            if not re.match(self.ORPHAN_MATCHER, line):
                out.append(line)
        return '\n'.join(out)

    def _add_formatters(self):
        self.add_simple_formatter('b', '<strong>%(value)s</strong>')
        self.add_simple_formatter('br', '<br>\n', standalone=True)

        # todo use foundation way for centering
        self.add_simple_formatter(
            'center', '<div style="text-align:center;">%(value)s</div>\n')

        self.add_simple_formatter(
            'code', '<code>%(value)s</code>\n', renderEmbedded=False,
            transformNewlines=False, swallowTrailingNewline=True)
        self.add_simple_formatter('hr', '<hr>\n', standalone=True)
        self.add_simple_formatter('i', '<em>%(value)s</em>')
        self.add_simple_formatter('p', '<p>%(value)s</p>\n')
        self.add_simple_formatter('s', '<strike>%(value)s</strike>')
        self.add_simple_formatter(
            'u', '<span style="text-decoration: underline;">%(value)s</span>')
        self.add_simple_formatter('sub', '<sub>%(value)s</sub>')
        self.add_simple_formatter('sup', '<sup>%(value)s</sup>')

        self._add_bbvideo_formatter()
        self._add_color_formatter()
        self._add_header_formatters()
        self._add_img_formatter()
        self._add_list_formatter()
        self._add_quote_formatter()
        self._add_removals()
        self._add_section_formatter()
        self._add_url_formatter()

    def _add_bbvideo_formatter(self):
        self.add_formatter('BBvideo', self._render_bbvideo,
                           replaceLinks=False, replaceCosmetic=False)

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
            'img', self._render_img, replaceLinks=False,
            replaceCosmetic=False)

    # noinspection PyUnusedLocal
    @staticmethod
    def _render_img(name, value, options, parent, context):
        href = value
        # Only add http:// if it looks like it starts with a domain name.
        if '://' not in href and RE.DOMAIN.match(href):
            href = 'http://' + href
        return '<img src="%s">' % (href.replace('"', '%22'))

    def _add_list_formatter(self):
        self.add_formatter(
            'list', self._render_list, transformNewlines=False,
            strip=True, swallowTrailingNewline=True)
        # Make sure transformNewlines = False for [*], so [code]
        # tags can be embedded without transformation.
        self.add_simple_formatter(
            '*', '<li>%(value)s</li>', newlineCloses=True,
            transformNewlines=False, sameTagCloses=True, strip=True)

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
            demotedTag = tag[0] + str(int(tag[1]) + self.DEMOTION_LEVEL)
            self.add_simple_formatter(
                tag, '\n<%s>%%(value)s</%s>\n' % (demotedTag, demotedTag))

    def _add_quote_formatter(self):
        self.add_formatter(
            'quote', self._render_quote, transformNewlines=False,
            strip=True, swallowTrailingNewline=True)

    # noinspection PyUnusedLocal
    @staticmethod
    def _render_quote(name, value, options, parent, context):
        """see http://html5doctor.com/blockquote-q-cite/"""
        author = (options['quote'] if (options and 'quote' in options) else '')
        cite = "<footer><cite>%s</cite></footer>" % (author) if author else ''
        value = value.replace('\n', '<br>')
        return '<blockquote><p>%s%s</p></blockquote>\n' % (value, cite)

    def _add_removals(self):
        for removal in ['meta', 'mod']:
            self.add_simple_formatter(removal, '')

    # noinspection PyUnusedLocal
    @staticmethod
    def _render_meta(name, value, options, parent, context):
        return '<div style="display: none;">%s</div>\n' % (value)

    def _add_section_formatter(self):
        self.add_formatter(
            'section', self._render_section, transformNewlines=False,
            strip=True, swallowTrailingNewline=True)

    # noinspection PyUnusedLocal
    @staticmethod
    def _render_section(name, value, options, parent, context):
        return '<section>%s</section>' % (value)

    def _add_url_formatter(self):
        self.add_formatter('url', self._render_url, replaceLinks=False,
                           replaceCosmetic=False)

    # noinspection PyUnusedLocal
    @staticmethod
    def _render_url(name, value, options, parent, context):
        if options and 'url' in options:
            # Option values are not escaped for HTML output.
            href = Replacer.replace(options['url'], Replacer.HTML_ESCAPE)
        else:
            href = value
        # Completely ignore javascript: and data: "links".
        if (re.sub(r'[^a-z0-9+]', '', href.lower().split(':', 1)[0]) in
                ('javascript', 'data', 'vbscript')):
            return ''

        # Only add http:// if it looks like it starts with a domain name.
        if '://' not in href and RE.DOMAIN.match(href):
            href = 'http://' + href
        return '<a href="%s">%s</a>' % (href.replace('"', '%22'), value)
