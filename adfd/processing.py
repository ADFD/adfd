import re

from plumbum.path.local import LocalPath

from adfd.adfd_parser import AdfdParser


class AdfdProcessor(object):
    def __init__(self, text=None, path=None):
        if text:
            self.text = text
        else:
            assert path
            path = LocalPath(path)
            self.text = path.read()
        assert self.text

    def process(self):
        parser = AdfdParser(data=self.text)
        apr = AdfdParagrafenreiter(parser.tokens)
        parser.tokens = apr.reitedieparagrafen()
        return parser.to_html()


class Token(object):
    def __init__(self, *args):
        self.asTuple = args
        self.type, self.tag, self.options, self.text = self.asTuple

    def __repr__(self):
        txt = "%s|" % (self.text[:10].encode('utf8').strip())
        return "%s%s" % ("%s|" % (self.tag) if self.tag else txt, self.type)


class AdfdParagrafenreiter(object):
    P_START_TOKEN = Token(AdfdParser.TOKEN_TAG_START, 'p', None, '[p]')
    P_END_TOKEN = Token(AdfdParser.TOKEN_TAG_END, 'p', None, '[/p]')

    def __init__(self, tokens):
        self.tokens = [Token(*args) for args in tokens]

    def reitedieparagrafen(self):
        self.paragraphed_sections = self.wrap_sections(self.tokens)
        self.paragraphed_quotes = self.wrap_quotes(self.paragraphed_sections)
        flatList = self.flatten(self.paragraphed_quotes)
        tokensAsTuples = [t.asTuple for t in flatList]
        return tokensAsTuples

    def wrap_sections(self, tokens):
        lol = []
        current = []
        idx = 0
        while idx < len(tokens):
            token = tokens[idx]
            if self.is_header_start(token):
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
            if self.is_header_start(section[0]):
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

            if self.is_quote_start(token):
                assert not self.is_quote_end(nextToken), tokens
                modifiedTokens.append(token)
                modifiedTokens.append(self.P_START_TOKEN)
            elif self.is_quote_end(nextToken):
                modifiedTokens.append(token)
                modifiedTokens.append(self.P_END_TOKEN)
            else:
                modifiedTokens.append(token)
            idx += 1
        return modifiedTokens

    def flatten(self, lol):
        result = []
        for el in lol:
            if isinstance(el, list):
                result.extend(self.flatten(el))
            else:
                result.append(el)
        return result

    def is_header_start(self, token):
        if token.type != AdfdParser.TOKEN_TAG_START:
            return False

        return re.match("h\d", token.tag)

    def is_quote_start(self, token):
        if not token:
            return False

        if token.type != AdfdParser.TOKEN_TAG_START:
            return False

        return token.tag == "quote"

    def is_quote_end(self, token):
        if not token:
            return False

        if token.type != AdfdParser.TOKEN_TAG_END:
            return False

        return token.tag == "quote"

    def wrap_section_paragraphs(self, tokens):
        tokens = self.strip_leading_newline_token(tokens)
        idx = 0
        tokens.insert(0, self.P_START_TOKEN)
        while idx < (len(tokens)):
            token = tokens[idx]
            try:
                nextToken = tokens[idx + 1]
            except IndexError:
                nextToken = None
            if self.is_newline(token) and self.is_newline(nextToken):
                tokens.insert(idx, self.P_END_TOKEN)
                if idx + 3 >= len(tokens):
                    break

                else:
                    tokens.insert(idx + 2, self.P_START_TOKEN)
            idx += 1
        return tokens

    def strip_leading_newline_token(self, tokens):
        if self.is_newline(tokens[0]):
            tokens.pop(0)
        return tokens

    def is_newline(self, token):
        if not token:
            return False

        return token.type == AdfdParser.TOKEN_NEWLINE


if __name__ == '__main__':
    from bs4 import BeautifulSoup

    rootPath = LocalPath(__file__).up(2)
    p = (rootPath / 'content/processed/10068.bb')
    ap = AdfdProcessor(path=p)
    print ap.text
    print
    html = ap.process()
    print html
    print '#' * 80
    print BeautifulSoup(html, 'html.parser').prettify()
