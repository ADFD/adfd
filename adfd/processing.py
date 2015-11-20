from plumbum.path.local import LocalPath

from adfd.bbcode import Token, AdfdParser


class AdfdProcessor(object):
    def __init__(self, text=None, path=None):
        if text:
            self.text = text
        else:
            assert path
            path = LocalPath(path)
            self.text = path.read('utf8')
        assert self.text

    def process(self):
        parser = AdfdParser(data=self.text)
        apr = AdfdParagrafenreiter(parser.tokens)
        parser.tokens = apr.reitedieparagrafen()
        return parser.to_html()


class AdfdParagrafenreiter(object):
    P_START_TOKEN = Token(AdfdParser.TOKEN_TAG_START, 'p', None, '[p]')
    P_END_TOKEN = Token(AdfdParser.TOKEN_TAG_END, 'p', None, '[/p]')
    BLOCK_CHANGE_TOKEN = Token('change', None, None, None)

    def __init__(self, tokens):
        self.tokens = [Token(*args) for args in tokens]

    def reitedieparagrafen(self):
        """
        1. split headers and sections, like before
        2. Add new token that signals block changes
        2. Inside each section
            first pass:
                fix newlines:
                    before and after block tags -> makes sure there are
                    2 newlines
                replace double newLines with single block change token
                ... or do this in one step (addd and replace right away)
            second pass:
                wrap paragraphs around all blocks
        """
        self.sections = self.make_sections(self.tokens)
        self.paragraphed_quotes = self.wrap_quotes(self.sections)
        self.flatList = self.flatten(self.paragraphed_quotes)
        self.tokensAsTuples = [t.asTuple for t in self.flatList]
        return self.tokensAsTuples

    def make_sections(self, tokens):
        lol = []
        current = []
        idx = 0
        while idx < len(tokens):
            token = tokens[idx]
            if token.isHeaderStart:
                if current:
                    lol.append(self.wrap_section_paragraphs(current))
                    current = []
                newIdx = idx + 3
                lol.append(tokens[idx:newIdx])
                idx = newIdx
                continue

            current.append(token)
            idx += 1

        if current:
            lol.append(self.wrap_section_paragraphs(current))
        return lol

    def wrap_quotes(self, wrappedSections):
        lol = []
        for section in wrappedSections:
            if section[0].isHeaderStart:
                lol.append(section)
                continue

            lol.append(self._wrap_quotes(section))
        return lol

    def _wrap_quotes(self, tokens):
        modifiedTokens = []
        idx = 0
        while idx < len(tokens):
            token = tokens[idx]
            try:
                nextToken = tokens[idx + 1]
            except IndexError:
                nextToken = None

            if token.isQuoteStart:
                assert not nextToken.isQuoteEnd, nextToken
                modifiedTokens.append(token)
                modifiedTokens.append(self.P_START_TOKEN)
            elif nextToken and nextToken.isQuoteEnd:
                modifiedTokens.append(token)
                modifiedTokens.append(self.P_END_TOKEN)
            else:
                modifiedTokens.append(token)
            idx += 1
        return modifiedTokens

    def wrap_section_paragraphs(self, tokens):
        """Wrap paragraphs in section.

        I define a paragraph as a text separated by two newlines - simples

        All other tags encountered within the paragraph can just be skipped.
        """
        tokens = self.strip_leading_newline(tokens)
        tokens.insert(0, self.P_START_TOKEN)
        idx = 1
        while idx < (len(tokens)):
            idx = self.skip_tags(tokens, idx)
            token = tokens[idx]
            try:
                nextToken = tokens[idx + 1]
            except IndexError:
                nextToken = None
            if token.isNewline and nextToken.isNewline:

                tokens.insert(idx, self.P_END_TOKEN)
                if idx + 3 >= len(tokens):
                    break

                else:
                    tokens.insert(idx + 2, self.P_START_TOKEN)
            idx += 1
        return tokens

    def strip_leading_newline(self, tokens):
        if tokens[0].isNewline:
            tokens.pop(0)
        return tokens

    def skip_tags(self, tokens, idx):
        if tokens[idx].isOpener:
            idx += 1
            if tokens[idx].isCloser:
                return idx + 1

            idx = self.skip_tags(tokens, idx)
        return idx

    def flatten(self, lol):
        result = []
        for el in lol:
            if isinstance(el, list):
                result.extend(self.flatten(el))
            else:
                result.append(el)
        return result
