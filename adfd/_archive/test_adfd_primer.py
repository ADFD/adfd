# -*- coding: utf-8 -*-
from __future__ import print_function

import pytest
from adfd_primer import AdfdPrimer, BadHeader, BadQuotes

from adfd.utils import DataGrabber


class TestAdfdPrimer(object):
    dg = DataGrabber('priming')

    @pytest.mark.parametrize("line,exp", dg.get_boolean_tests('headers1'))
    def test_headers1(self, line, exp):
        assert AdfdPrimer.is_header_line(line) == exp

    @pytest.mark.parametrize("line,exp", dg.get_boolean_tests('headers2'))
    def test_headers2(self, line, exp):
        with pytest.raises(BadHeader):
            assert AdfdPrimer.is_header_line(line) == exp

    def test_quotes(self):
        for chunk in self.dg.get_chunks('quotes'):
            formattedQuotes = AdfdPrimer.format_quotes(chunk)
            assert formattedQuotes[0] == AdfdPrimer.QUOTE_START
            assert formattedQuotes[-1] == AdfdPrimer.QUOTE_END

    @pytest.mark.parametrize(
        "line", ['[quote]bla[quote]blub', 'bla[/quote]bla[/quote]']
    )
    def test_bad_quotes(self, line):
        with pytest.raises(BadQuotes):
            AdfdPrimer.format_quotes([line])

    @pytest.mark.parametrize(
        "line,exp", [
            (u'[quote="Äuthor"]', u"Äuthor"),
            (u'[quote]', None),
            (u'something else', None),
        ])
    def test_get_author(self, line, exp):
        assert AdfdPrimer.get_quote_author(line) == exp
