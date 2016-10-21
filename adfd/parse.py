import html
import itertools
import logging
import re

from adfd.utils import slugify
from cached_property import cached_property
from pyphen import Pyphen
from typogrify.filters import typogrify

log = logging.getLogger(__name__)


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
    """
    type
        TAG_START, TAG_END, NEWLINE or DATA
    tag
        The name of the tag if token_type=TAG_*, otherwise None
    options
        dict of options specified for TAG_START, otherwise None
    text
        The original token text
    """
    TAG_START = 'start'
    TAG_END = 'end'
    NEWLINE = 'newline'
    DATA = 'data'

    def __init__(self, *args):
        self.type, self.tag, self.options, self.text = args
        self.isOpener = self.type == Token.TAG_START
        self.isCloser = self.type == Token.TAG_END
        self.isHeaderStart = self.isOpener and re.match("h\d", self.tag)
        self.isQuoteStart = self.isOpener and self.tag == "quote"
        self.isQuoteEnd = self.isCloser and self.tag == "quote"
        self.isListStart = self.isOpener and self.tag == "list"
        self.isListEnd = self.isCloser and self.tag == "list"
        self.isNewline = self.type == Token.NEWLINE

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        if self.tag:
            return "<%s%s>" % ('/' if self.isCloser else '', self.tag)

        return "<%s>" % self.text

    @property
    def asTuple(self):
        return (self.type, self.tag, self.options, self.text)


class Parser:
    def __init__(
            self, newline='\n', normalizeNewlines=True,
            escapeHtml=True, hyphenate=False, typogrify=False,
            replaceLinks=True, replaceCosmetic=True,
            tagOpener='[', tagCloser=']',
            linker=None, linkerTakesContext=False, dropUnrecognized=False):
        self.tagOpener = tagOpener
        self.tagCloser = tagCloser
        self.newline = newline
        self.normalizeNewlines = normalizeNewlines
        self.recognizedTags = {}
        self.unknownTags = set()
        self.dropUnrecognized = dropUnrecognized
        self.escapeHtml = escapeHtml
        self.typogrify = typogrify
        self.hyphenate = hyphenate
        self.replaceCosmetic = replaceCosmetic
        self.replaceLinks = replaceLinks
        self.linker = linker
        self.linkerTakesContext = linkerTakesContext

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
        self.recognizedTags[options.tagName] = (render_func, options)

    def add_simple(self, tagName, format_string, **kwargs):
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
        """Create a list of NEWLINE and DATA tokens.

        If you concatenate their data, you will have the original string.

        :type data: str
        :returns: list of Token
        """
        parts = data.split('\n')
        tokens = []
        """:type: list of Token"""
        for num, part in enumerate(parts):
            if part:
                tokens.append(Token(*(Token.DATA, None, None, part)))
            if num < (len(parts) - 1):
                tokens.append(Token(*(Token.NEWLINE, None, None, '\n')))
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
        if ((not tag.startswith(self.tagOpener)) or
                (not tag.endswith(self.tagCloser)) or
                ('\n' in tag) or ('\r' in tag)):
            return (False, tag, False, None)

        tagName = tag[len(self.tagOpener):-len(self.tagCloser)].strip()
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
        # noinspection PyTypeChecker
        for i in range(start + 1, len(data)):
            ch = data[i]
            if ch in ('"', "'"):
                if not in_quote:
                    in_quote = ch
                elif in_quote == ch:
                    in_quote = False
            if (not in_quote and
                    data[i:i + len(self.tagOpener)] == self.tagOpener):
                return i, False
            if (not in_quote and
                    data[i:i + len(self.tagCloser)] == self.tagCloser):
                return i + len(self.tagCloser), True
        return len(data), False

    def tokenize(self, data):
        """Create list of tokens from original data
        :returns: list of Token
        """
        if self.normalizeNewlines:
            data = data.replace('\r\n', '\n').replace('\r', '\n')
        pos = 0
        tokens = []
        """:type: list of Token"""
        while pos < len(data):
            start = data.find(self.tagOpener, pos)
            if start >= pos:
                # Check if there was data between this start and the last end
                if start > pos:
                    tokens.extend(self._newline_tokenize(data[pos:start]))
                    # noinspection PyUnusedLocal
                    pos = start

                # Find the extent of this tag, if it's ever closed.
                end, found_close = self._tag_extent(data, start)
                if found_close:
                    tag = data[start:end]
                    valid, tagName, closer, opts = self._parse_tag(tag)
                    # Make sure this is a well-formed, recognized tag,
                    # otherwise it's just data
                    if valid and tagName in self.recognizedTags:
                        if closer:
                            args = (Token.TAG_END, tagName, None, tag)
                            tokens.append(Token(*args))
                        else:
                            args = (Token.TAG_START, tagName, opts, tag)
                            tokens.append(Token(*args))
                    elif valid and tagName not in self.recognizedTags:
                        # If we found a valid (but unrecognized) tag and
                        # self.dropUnrecognized is True, just drop it
                        self.unknownTags.add(tagName)
                        if not self.dropUnrecognized:
                            tokens.extend(self._newline_tokenize(tag))
                else:
                    # We didn't find a closing tag, tack it on as text.
                    tokens.extend(self._newline_tokenize(data[start:end]))
                pos = end
            else:
                # No more tags left to parse.
                break
        if pos < len(data):
            tokens.extend(self._newline_tokenize(data[pos:]))
        return tokens

    def _find_closer(self, tag, tokens, pos):
        """Find position of closing token.

        Given the current tag options, a list of tokens, and the current
        position in the token list, this function will find the position of the
        closing token associated with the specified tag. This may be a closing
        tag, a newline, or simply the end of the list (to ensure tags are
        closed). This function should return a tuple of the form (end_pos,
        consume), where consume should indicate whether the ending token
        should be consumed or not.
        """
        embedCount = 0
        blockCount = 0
        while pos < len(tokens):
            token = tokens[pos]
            """:type: Token"""
            if (tag.newlineCloses and token.type in
                    (Token.TAG_START, Token.TAG_END)):
                # If we're finding the closing token for a tag that is
                # closed by newlines, but there is an embedded tag that
                # doesn't transform newlines (i.e. a code tag that keeps
                # newlines intact), we need to skip over that.
                innerTag = self.recognizedTags[token.tag][1]
                if not innerTag.transformNewlines:
                    if token.type == Token.TAG_START:
                        blockCount += 1
                    else:
                        blockCount -= 1
            if (token.type == Token.NEWLINE and tag.newlineCloses and
                    blockCount == 0):
                # If for some crazy reason there are embedded tags that
                # both close on newline, the first newline will automatically
                # close all those nested tags.
                return pos, True
            elif token.type == Token.TAG_START and token.tag == tag.tagName:
                if tag.sameTagCloses:
                    return pos, False

                if tag.renderEmbedded:
                    embedCount += 1
            elif token.type == Token.TAG_END and token.tag == tag.tagName:
                if embedCount > 0:
                    embedCount -= 1
                else:
                    return pos, True

            pos += 1
        return (pos, True)

    def _link_replace(self, match, **context):
        """Callback for re.sub to replace link text with markup.

        Turns out using a callback function is actually faster than using
        backrefs, plus this lets us provide a hook for user customization.
        linkerTakesContext=True means that the linker gets passed context
        like a standard format function.
        """
        url = match.group(0)
        if self.linker:
            if self.linkerTakesContext:
                return self.linker(url, context)
            else:
                return self.linker(url)
        else:
            href = url
            if '://' not in href:
                href = 'http://' + href
            # Escape quotes to avoid XSS, let the browser escape the rest.
            return '<a href="%s">%s</a>' % (href.replace('"', '%22'), url)

    def _transform(self, tokens, escapeHtml, replaceLinks, replaceCosmetic,
                   **context):
        """Transforms the input string based on the options specified.

        Takes into account if option is enabled globally for this parser.
        """
        text = ''.join([t.text for t in tokens])
        urlMatches = {}
        if self.replaceLinks and replaceLinks:
            # If we're replacing links in the text (i.e. not those in [url]
            # tags) then we need to be careful to pull them out before doing
            # any escaping or cosmetic replacement.
            pos = 0
            while True:
                match = RE.URL.search(text, pos)
                if not match:
                    break

                # Replace any link with a token that we can substitute back
                # in after replacements.
                token = '{{ bbcode-link-%s }}' % len(urlMatches)
                urlMatches[token] = self._link_replace(match, **context)
                # noinspection PyUnresolvedReferences
                start, end = match.span()
                text = text[:start] + token + text[end:]
                # To be perfectly accurate, this should probably be
                # len(text[:start] + token), but start will work, because the
                # token itself won't match as a URL.
                pos = start
        if self.escapeHtml and escapeHtml:
            text = Replacer.replace(text, Replacer.HTML_ESCAPE)
        if self.replaceCosmetic and replaceCosmetic:
            text = Replacer.replace(text, Replacer.COSMETIC)
        if self.hyphenate:
            text = hyphenate(text)
        # Now put the replaced links back in the text.
        for token, replacement in urlMatches.items():
            text = text.replace(token, replacement)
        return text

    def _format_tokens(self, tokens, parent, **context):
        out = []
        idx = 0
        while idx < len(tokens):
            token = tokens[idx]
            """:type: Token"""
            if token.type == Token.TAG_START:
                fn, tag = self.recognizedTags[token.tag]
                if tag.standalone:
                    ret = fn(token.tag, None, token.options, parent, context)
                    out.append(ret)
                else:
                    # First, find the extent of this tag's tokens.
                    # noinspection PyTypeChecker
                    end, consume = self._find_closer(tag, tokens, idx + 1)
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
                            subtokens, tag.escapeHtml, tag.replaceLinks,
                            tag.replaceCosmetic, **context)
                    # Strip and replace newlines, if necessary.
                    if tag.strip:
                        inner = inner.strip()
                    if tag.transformNewlines:
                        inner = inner.replace('\n', self.newline)
                    # Append the rendered contents.
                    ret = fn(token.tag, inner, token.options, parent, context)
                    out.append(ret)
                    # If the tag should swallow the first trailing newline,
                    # check the token after the closing token.
                    if tag.swallowTrailingNewline:
                        nextPos = end + 1
                        if (nextPos < len(tokens) and
                                tokens[nextPos].type == Token.NEWLINE):
                            end = nextPos
                    # Skip to the end tag.
                    idx = end
            elif token.type == Token.NEWLINE:
                # If this is a top-level newline, replace it. Otherwise,
                # it will be replaced (if necessary) by the code above.
                out.append(self.newline if parent is None else token.text)
            elif token.type == Token.DATA:
                escape = (self.escapeHtml if parent is None else
                          parent.escapeHtml)
                links = (self.replaceLinks if parent is None
                         else parent.replaceLinks)
                cosmetic = (self.replaceCosmetic if parent is None
                            else parent.replaceCosmetic)
                ret = self._transform(
                    [token], escape, links, cosmetic, **context)
                out.append(ret)
            idx += 1
        return ''.join(out)

    def strip(self, data, strip_newlines=False):
        """Strip out any tags from the input text.

        Using the same tokenization as the formatter.
        """
        text = []
        for token in self.tokenize(data):
            if token.type == Token.DATA:
                text.append(token.text)
            elif token.type == Token.NEWLINE and not strip_newlines:
                text.append(token.text)
        return ''.join(text)


class Chunk:
    """Forms token groups to fix missing formatting in forum articles"""
    HEADER = 'header'
    PARAGRAPH = 'paragraph'
    QUOTE = 'quote'
    LIST = 'list'
    TYPES = [HEADER, PARAGRAPH, QUOTE, LIST]

    def __init__(self, tokens, chunkType):
        """
        :type tokens: list Token
        :param chunkType: one of Chunk.TYPES
        """
        self.tokens = tokens
        self.chunkType = chunkType
        self.clean()
        self.modify()

    def __repr__(self):
        return " ".join([str(c) for c in self.tokens])

    def clean(self):
        """remove newlines at beginning and end of chunk"""
        for idx in [0, -1]:
            try:
                while self.tokens[idx].isNewline:
                    self.tokens.pop(idx)
            except IndexError:
                pass

    def modify(self):
        """This innocent method is the reason why we have chunks"""
        if self.isEmpty:
            return

        if self.chunkType == self.PARAGRAPH:
            startToken = Token(Token.TAG_START, 'p', None, '[p]')
            endToken = Token(Token.TAG_END, 'p', None, '[/p]')
            self.tokens.insert(0, startToken)
            self.tokens.append(endToken)

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
        """

        :type tokens: list of Token
        """
        self.tokens = tokens
        self._chunks = []

    @cached_property
    def flattened(self):
        return list(itertools.chain(*[chunk.tokens for chunk in self.chunks]))

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
    HEADER_TAGS = ['h%s' % i for i in range(1, 6)]

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
        if self.typogrify:
            html = typogrify(html)
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
        self.add_simple('b', '<strong>%(value)s</strong>')
        self.add_simple('br', '<br>\n', standalone=True)
        self.add_simple(
            'center', '<div style="text-align:center;">%(value)s</div>\n')
        self.add_simple(
            'code', '<code>%(value)s</code>\n', renderEmbedded=False,
            transformNewlines=False, swallowTrailingNewline=True)
        self.add_simple('hr', '<hr>\n', standalone=True)
        self.add_simple('i', '<em>%(value)s</em>')
        self.add_simple('p', '<p>%(value)s</p>\n')
        self.add_simple('s', '<strike>%(value)s</strike>')
        self.add_simple(
            'u', '<span style="text-decoration: underline;">%(value)s</span>')
        self.add_simple('sub', '<sub>%(value)s</sub>')
        self.add_simple('sup', '<sup>%(value)s</sup>')

        self._add_bbvideo_formatter()
        self._add_color_formatter()
        self._add_header_formatters()
        self._add_img_formatter()
        self._add_list_formatter()
        self._add_mod_formatter()
        self._add_quote_formatter()
        self._add_raw_formatter()
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
            'target="_blank">%(url)s</a>' % dataMap)

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

    def _add_mod_formatter(self):
        self.add_formatter('mod', self._render_mod)

    # noinspection PyUnusedLocal
    @staticmethod
    def _render_mod(name, value, options, parent, context):
        if 'mod' in options:
            name = options['mod'].strip()
        elif options:
            name = list(options.keys())[0].strip()
        else:
            return value

        match = re.match(r'^([a-z]+)|^(#[a-f0-9]{3,6})', name, re.I)
        name = match.group() if match else 'inherit'
        return ('<div style="background: orange;">[%s] %s</div>'
                % (name, value))

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
        self.add_simple(
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
            self.add_formatter(tag, self._render_header)

    @staticmethod
    def _render_header(tag, value, options, parent, context):
        demotionLevel = 1  # number of levels header tags get demoted
        level = int(tag[1]) + demotionLevel
        slug = slugify(value)
        r = '<h%s id="%s">' % (level, slug)
        r += '<a class="header" href="#%s">%s' % (slug, value)
        r += ' <i class="paragraph icon"></i>'
        r += '</a></h%s>' % level
        return r

    def _add_quote_formatter(self):
        self.add_formatter(
            'quote', self._render_quote, transformNewlines=False,
            strip=True, swallowTrailingNewline=True)

    # noinspection PyUnusedLocal
    @staticmethod
    def _render_quote(name, value, options, parent, context):
        author = (options['quote'] if (options and 'quote' in options) else '')
        if author:
            cite = ('<div class="ui inverted secondary segment">'
                    '<i class="comment outline icon"></i>%s</div>' % author)
        else:
            cite = ''
        value = value.replace('\n', '<br>')
        return '<div class="ui raised segment">%s%s</div>\n' % (value, cite)

    def _add_raw_formatter(self):
        self.add_formatter(
            'raw', self._render_raw, replaceLinks=False, replaceCosmetic=False)

    # noinspection PyUnusedLocal
    def _render_raw(self, name, value, options, parent, context):
        return html.unescape(value)

    def _add_removals(self):
        for removal in ['meta']:
            self.add_simple(removal, '')

    # # noinspection PyUnusedLocal
    # @staticmethod
    # def _render_meta(name, value, options, parent, context):
    #     return '<div style="display: none;">%s</div>\n' % value

    def _add_section_formatter(self):
        self.add_formatter(
            'section', self._render_section, transformNewlines=False,
            strip=True, swallowTrailingNewline=True)

    # noinspection PyUnusedLocal
    @staticmethod
    def _render_section(name, value, options, parent, context):
        return '<section>%s</section>' % value

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


class Replacer:
    HTML_ESCAPE = (
        ('&', '&amp;'),
        ('<', '&lt;'),
        ('>', '&gt;'),
        ('"', '&quot;'),
        ("'", '&#39;'))

    COSMETIC = (
        ('---', '&mdash;'),
        ('--', '&ndash;'),
        ('...', '&#8230;'),
        ('(c)', '&copy;'),
        ('(reg)', '&reg;'),
        ('(tm)', '&trade;'))

    @staticmethod
    def replace(data, replacements):
        """
        Given a list of 2-tuples (find, repl) this function performs all
        replacements on the input and returns the result.
        """
        for find, repl in replacements:
            data = data.replace(find, repl)
        return data


def hyphenate(text, hyphen='&shy;'):
    py = Pyphen(lang='de_de')
    words = text.split(' ')
    return ' '.join([py.inserted(word, hyphen=hyphen) for word in words])


# fixme likely not needed
def untypogrify(text):
    def untypogrify_char(c):
        return '"' if c in ['“', '„'] else c

    return ''.join([untypogrify_char(c) for c in text])


class RE:
    URL = re.compile(
        r'(?im)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)'
        r'(?:[^\s()<>]+|\([^\s()<>]+\))'
        r'+(?:\([^\s()<>]+\)|[^\s`!()\[\]{};:\'".,<>?]))')
    """
    from http://daringfireball.net/2010/07/improved_regex_for_matching_urls
    Only support one level of parentheses - was failing on some URLs.
    See http://www.regular-expressions.info/catastrophic.html
    """
    DOMAIN = re.compile(
        r'(?im)(?:www\d{0,3}[.]|[a-z0-9.\-]+[.]'
        r'(?:com|net|org|edu|biz|gov|mil|info|io|name|me|tv|us|uk|mobi))')
    """
    For the URL tag, try to be smart about when to append a missing http://.
    If the given link looks like a domain, add a http:// in front of it,
    otherwise leave it alone (be a relative path, a filename, etc.).
    """


def extract_from_bbcode(tag, content):
    rString = r'\[%s\](.*)\[/%s\]' % (tag, tag)
    regex = re.compile(rString, re.MULTILINE | re.DOTALL)
    match = regex.search(content)
    try:
        return match.group(1)
    except AttributeError:
        pass
        # log.warning("no [%s] in %s[...]" % (tag, content[:50]))
