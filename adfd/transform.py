import itertools

from cached_property import cached_property

from adfd.bbcode import Token, AdfdParser
from adfd.cst import PATH


class Chunk(object):
    HEADER = 'header'
    PARAGRAPH = 'paragraph'
    QUOTE = 'quote'
    TYPES = [HEADER, PARAGRAPH, QUOTE]
    P_START_TOKEN = Token(AdfdParser.TOKEN_TAG_START, 'p', None, '[p]')
    P_END_TOKEN = Token(AdfdParser.TOKEN_TAG_END, 'p', None, '[/p]')

    def __init__(self, tokens, chunkType):
        self.tokens = tokens
        self.chunkType = chunkType
        self.prepare_tokens()

    def __repr__(self):
        return " ".join([str(c) for c in self.tokens])

    # @cached_property
    # def asHtml(self):
    #     return self.parser.to_html(tokens=self.tokensAsTuples)

    @cached_property
    def tokensAsTuples(self):
        return [t.asTuple for t in self.tokens]

    def prepare_tokens(self):
        """this innocent method is the reason why we have chunks"""
        if self.chunkType == self.PARAGRAPH:
            self.tokens.insert(0, self.P_START_TOKEN)
            self.tokens.append(self.P_END_TOKEN)
        # elif self.chunkType == self.QUOTE:
        #     self.tokens.insert(1, self.P_START_TOKEN)
        #     self.tokens.insert(len(self.tokens) - 1, self.P_END_TOKEN)


class ArticleContent(object):
    def __init__(self, rawBbcode):
        self.rawBbcode = rawBbcode
        self.tokens = [Token(*t) for t in AdfdParser().tokenize(rawBbcode)]
        self._chunks = []

    @cached_property
    def serializedChunks(self):
        return list(itertools.chain(*[c.tokensAsTuples for c in self.chunks]))

    @cached_property
    def chunks(self):
        """article chunks which can be converted individually

        :rtype: list of list of TransformableChunk
        """
        curentTokens = []
        idx = 0
        while idx < len(self.tokens):
            token = self.tokens[idx]
            if token.isHeaderStart:
                curentTokens = self.flush(curentTokens)
                newIdx = idx + 3
                self.flush(self.tokens[idx:newIdx], Chunk.HEADER)
                idx = newIdx
                continue

            if token.isQuoteStart:
                self.flush(curentTokens)
                sIdx = idx
                while not token.isQuoteEnd:
                    idx += 1
                    token = self.tokens[idx]
                idx += 1
                curentTokens = self.flush(self.tokens[sIdx:idx], Chunk.QUOTE)
                continue

            try:
                nextToken = self.tokens[idx + 1]
            except IndexError:
                nextToken = None
            if token.isNewline and nextToken and nextToken.isNewline:
                curentTokens = self.flush(curentTokens)
                idx += 1
                continue

            curentTokens.append(token)
            idx += 1

        self.flush(curentTokens)
        return self._chunks

    def flush(self, tokens, chunkType=Chunk.PARAGRAPH):
        """append cleaned tokens and return a fresh (empty) list"""
        tokensWithoutNewlines = [t for t in tokens if not t.isNewline]
        if tokensWithoutNewlines:
            chunk = Chunk(tokensWithoutNewlines, chunkType)
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


if __name__ == '__main__':
    # p = PATH.TEST_DATA / 'transform' / '01a-simple.bb'
    p = PATH.TEST_DATA / 'transform' / '02c-with-header-and-quote.bb'
    content = p.read('utf8')
    ac = ArticleContent(content)
    print(ac.serializedChunks)
    html = AdfdParser().to_html(tokens=ac.serializedChunks)
    print(html)
    # for idx, chunk in enumerate(ac.chunks):
    #     print("%s: %s" % (idx, chunk))
    #     print(chunk.asHtml)
    #     # print(obj_attr(chunk))
    #     # for token in chunk.tokens:
    #     #     # print(token)
    #     #     # print(type(token))
    #     #     print(obj_attr(token))
