from cached_property import cached_property

from adfd.adfd_parser import AdfdParser
from adfd.cst import PATH
from adfd.processing import Token


class ArticleContent(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self._chunks = []

    # @cached_property
    @property
    def chunks(self):
        """article chunks which can be converted individually

        :rtype: list of list of TransformableChunk
        """
        curentTokens = []
        idx = 0
        while idx < len(self.tokens):
            token = self.tokens[idx]
            if token.isHeaderStart:
                curentTokens = self.flush_tokens(curentTokens)
                newIdx = idx + 3
                self.flush_tokens(self.tokens[idx:newIdx])
                idx = newIdx
                continue

            if token.isQuoteStart:
                self.flush_tokens(curentTokens)
                quoteStartIdx = idx
                while not token.isQuoteEnd:
                    idx += 1
                    token = self.tokens[idx]
                idx += 1
                curentTokens = self.flush_tokens(self.tokens[quoteStartIdx:idx])
                continue

            try:
                nextToken = self.tokens[idx + 1]
            except IndexError:
                nextToken = None
            if token.isNewline and nextToken and nextToken.isNewline:
                curentTokens = self.flush_tokens(curentTokens)
                idx += 1
                continue

            curentTokens.append(token)
            idx += 1

        self.flush_tokens(curentTokens)
        return self._chunks

    def flush_tokens(self, tokens):
        """append cleaned tokens and return a fresh (empty) list"""
        tokensWithoutNewlines = [t for t in tokens if not t.isNewline]
        if tokensWithoutNewlines:
            chunk = TransformableChunk(tokensWithoutNewlines)
            self._chunks.append(chunk)
        return []

    @cached_property
    def toc(self):
        """Table of contents extractes from the header elements"""
        raise NotImplementedError

    @cached_property
    def structure(self):
        """complete article as tree structure"""
        raise NotImplementedError

    @cached_property
    def asHTml(self):
        """traverse chunks in right order and output collected HTML"""
        raise NotImplementedError


class TransformableChunk(object):
    """A chunk is a part of the text that knows how to transform itself"""
    HEADER = 'header'
    PARAGRAPH = 'paragraph'
    QUOTATION = 'quotation'
    """Either stands on its own or is part of a paragraph"""
    TYPES = [HEADER, PARAGRAPH, QUOTATION]

    def __init__(self, tokens):
        self.tokens = tokens

    def __repr__(self):
        return " ".join([str(c) for c in self.tokens])

    @cached_property
    def asHtml(self):
        pass


if __name__ == '__main__':
    # p = PATH.TEST_DATA / 'transform' / '01a-simple.bb'
    p = PATH.TEST_DATA / 'transform' / '02c-with-header-and-quote.bb'
    content = p.read('utf8')
    tokens = [Token(*t) for t in AdfdParser(data=content).tokens]
    ac = ArticleContent(tokens)
    # print(ac.tokens)
    for idx, chunk in enumerate(ac.chunks):
        print("%s: %s" % (idx, chunk))
