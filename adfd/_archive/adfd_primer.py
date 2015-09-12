import logging
import re

log = logging.getLogger(__name__)


class AdfdPrimer(object):
    """Very stupid and rigid preprocessor/sanity checker for articles"""
    MIN_HEADER_LEN = len("[hx]A[/hx]")
    HEADER_START_PAT = r'\[h(\d)'
    HEADER_END_PAT = r'/h(\d)\]'
    QUOTE_START = '[quote]'
    QUOTE_END = '[/quote]'
    PARAGRAPH_BLACKLIST = ['list']

    def __init__(self, text):
        self.text = text

    def add_paragraphs(self, lines):
        paragraphedLines = []
        idx = 0
        while idx < len(lines):
            line = lines[idx]
            tag = self.get_tag_from_line(line)
            if tag and tag in self.PARAGRAPH_BLACKLIST:
                idx, lines = self.consume_blacklisted_lines(idx, tag, lines)
                paragraphedLines.append(lines)
            if line and self.is_paragraph(line):
                line = u"[p]%s[/p]" % (line)
            paragraphedLines.append(line)
            idx += 1
        return paragraphedLines

    def get_tag_from_line(self, line):
        matcher = re.match(r'\[(.*)\]', line)
        if matcher:
            return matcher.group(1)

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

    def consume_blacklisted_lines(self, idx, endtag, lines):
        consumedLines = []
        while True:
            line = lines[idx]
            consumedLines.append(line)
            tag = self.get_tag_from_line(line)
            if tag and tag == endtag:
                return consumedLines
            idx += 1


class BadHeader(Exception):
    pass


class BadQuotes(Exception):
    pass
