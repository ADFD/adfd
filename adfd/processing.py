"""

[quote] a1 a2 [quote="author"]i1 i2[/quote] a3 a4 [/quote]
should become
[ quote, a1, a2, [quote="author", i1, i2, /quote], a2, a3 /quote ]

"""
import re
from adfd.adfd_parser import AdfdParser


class Token(object):
    def __init__(self, *args):
        self.type, self.tag, self.options, self.text = args

    def __repr__(self):
        txt = "%s|" % (self.text[:10].encode('utf8').strip())
        return "%s%s" % ("%s|" % (self.tag) if self.tag else txt, self.type)


class AdfdStructurer(object):
    def __init__(self, tokens):
        self.tokens = [Token(*args) for args in tokens]

    def structurize(self):
        self.wrapped_sections = self.wrap_sections(self.tokens)
        self.wrapped_quotes = self.wrap_quotes(self.wrapped_sections)
        return self.flatten(self.wrapped_quotes)

    def wrap_sections(self, tokens):
        lol = []
        current = []
        idx = 0
        while idx < len(tokens):
            token = tokens[idx]
            if self.is_header_start(token):
                if current:
                    self.p_wrap(current)
                    lol.append(current)
                    current = []
                newIdx = idx + 3
                lol.append(tokens[idx:newIdx])
                idx = newIdx
                continue

            current.append(token)
            idx += 1

        if current:
            self.p_wrap(current)
            lol.append(current)
        return lol

    def wrap_quotes(self, wrappedSections):
        newSections = []
        for section in wrappedSections:
            if self.is_header_start(section[0]):
                newSections.append(section)
                continue

            lol = []
            # noinspection PyTypeChecker
            self._sectionize_quotes(section, 0, lol)
            newSections.append(lol)
        return newSections

    def _sectionize_quotes(self, tokens, idx, lol):
        current = []
        while idx < len(tokens):
            token = tokens[idx]
            if self.is_quotes_start(token):
                lol.append(token)
                idx += 1
                idx = self._sectionize_quotes(tokens, idx, lol)
            if self.is_quotes_end(token):
                lol.append(current)
                lol.append(token)
                return idx

            current.append(token)
            idx += 1

        if current:
            lol.append(current)

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

    def is_quotes_start(self, token):
        if token.type != AdfdParser.TOKEN_TAG_START:
            return False

        return token.tag == "quote"

    def is_quotes_end(self, token):
        if token.type != AdfdParser.TOKEN_TAG_END:
            return False

        return token.tag == "quote"

    def p_wrap(self, tokens):
        tokens.insert(0, Token(AdfdParser.TOKEN_TAG_START, 'p', None, '[p]'))
        tokens.append(Token(AdfdParser.TOKEN_TAG_END, 'p', None, '[/p]'))


if __name__ == '__main__':
    from adfd.utils import DataGrabber

    dg = DataGrabber('pwrap')
    data = dg.get_pairs()
    in_ = data[0][1]
    parser = AdfdParser(data=in_)
    print in_
    tokens = parser.tokens
    s = AdfdStructurer(tokens)
    # for l in s.wrap_sections(s.tokens):
    #     print l
    # print
    for l in s.wrap_quotes(s.wrap_sections(s.tokens)):
        print l
    # print structurer.structurize()
    # print parser.to_html()
