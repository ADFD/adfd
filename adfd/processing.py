import re
from adfd.adfd_parser import AdfdParser


class Token(object):
    def __init__(self, *args):
        self.type, self.tag, self.options, self.text = args

    def __repr__(self):
        txt = "%s|" % (self.text[:10].encode('utf8').strip())
        return "%s%s" % ("%s|" % (self.tag) if self.tag else txt, self.type)


class AdfdStructurer(object):
    P_START_TOKEN = Token(AdfdParser.TOKEN_TAG_START, 'p', None, '[p]')
    P_END_TOKEN = Token(AdfdParser.TOKEN_TAG_END, 'p', None, '[/p]')

    def __init__(self, tokens):
        self.tokens = [Token(*args) for args in tokens]

    def structurize(self):
        self.wrapped_sections = self.wrap_sections(self.tokens)
        self.wrapped_quotes = self.wrap_quotes(self.wrapped_sections)
        return self.flatten(self.wrapped_quotes)

    def wrap_sections(self, tokens):
        """[RETURNS NEW LIST] chop text into headers and sections"""
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

            if self.is_quotes_start(token):
                assert not self.is_quotes_end(nextToken), tokens
                modifiedTokens.append(token)
                modifiedTokens.append(self.P_START_TOKEN)
            elif self.is_quotes_end(nextToken):
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

    def is_quotes_start(self, token):
        if not token:
            return False

        if token.type != AdfdParser.TOKEN_TAG_START:
            return False

        return token.tag == "quote"

    def is_quotes_end(self, token):
        if not token:
            return False

        if token.type != AdfdParser.TOKEN_TAG_END:
            return False

        return token.tag == "quote"

    def p_wrap(self, tokens):
        tokens.insert(0, self.P_START_TOKEN)
        tokens.append(self.P_END_TOKEN)


if __name__ == '__main__':
    from adfd.utils import DataGrabber

    dg = DataGrabber('pwrap')
    data = dg.get_pairs()
    in_ = data[0][1]
    parser = AdfdParser(data=in_)
    # print in_
    tokens = parser.tokens
    s = AdfdStructurer(tokens)
    print "BEFORE", s.tokens
    print
    newTokens = s.structurize()
    print "AFTER", newTokens
