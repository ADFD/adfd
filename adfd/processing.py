import re
from adfd.adfd_parser import AdfdParser


class Token(object):
    def __init__(self, *args):
        self.type, self.tag, self.options, self.text = args

    def __repr__(self):
        return "%s|%s|%s" % (
            self.type, self.tag, self.text[:8].encode('utf8').strip())


class AdfdStructurer(object):
    def __init__(self, tokens):
        self.tokens = [Token(*args) for args in tokens]

    @property
    def partitions(self):
        lol = []
        current = []
        idx = 0
        while idx < len(self.tokens):
            token = self.tokens[idx]
            assert token.type in AdfdParser.TOKENS, token.type
            if token.type == AdfdParser.TOKEN_TAG_START:
                if self.is_header_tag(token):
                    if current:
                        self.p_wrap(current)
                        lol.append(current)
                        current = []
                    newIdx = idx + 3
                    lol.append(self.tokens[idx:newIdx])
                    idx = newIdx
                    continue

            current.append(token)
            idx += 1
        return lol

    def is_header_tag(self, token):
        return re.match("h\d", token.tag)

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
    structurer = AdfdStructurer(tokens)
    for l in structurer.partitions:
        print l
    # print parser.to_html()
