from __future__ import print_function

from plumbum.path.local import LocalPath
import pytest

from adfd.adfd_parser import AdfdPrimer, BadHeader


def get_text(fName):
    return (LocalPath(__file__).up() / 'data' / (fName + '.bb')).read()


def get_lines(fName):
    return AdfdPrimer(get_text(fName)).strippedLines


def get_chunks(fName):
    """separates chunks separated by empty lines

    :returns: list of list of str
    """
    chunks = []
    currentChunkLines = []
    for line in get_lines(fName):
        if line:
            currentChunkLines.append(line)
        else:
            chunks.append(currentChunkLines)
            currentChunkLines = []
    return chunks


def header_params(fName):
    return [(l, 'good' in l) for l in get_chunks(fName)]


class TestAdfdPrimer(object):
    @pytest.mark.parametrize("line,exp", header_params('headers1'))
    def test_headers1(self, line, exp):
        print(line)
        assert AdfdPrimer.is_header_line(line) == exp

    @pytest.mark.parametrize("line,exp", header_params('headers2'))
    def test_headers2(self, line, exp):
        print(line)
        with pytest.raises(BadHeader):
            assert AdfdPrimer.is_header_line(line) == exp

    def test_quotes(self):
        for chunk in get_chunks('quotes'):
            formattedQuotes = AdfdPrimer.format_quotes(chunk)
            assert formattedQuotes[0] == AdfdPrimer.QUOTE_START
            assert formattedQuotes[-1] == AdfdPrimer.QUOTE_END
