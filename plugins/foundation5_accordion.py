# -*- coding: utf-8 -*-

"""
Copyright © 2015 Oliver Bestwalter.

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions of
the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from __future__ import unicode_literals

import uuid

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from nikola.plugin_categories import RestExtension


class Plugin(RestExtension):

    name = "rest_foundation5_accordion"

    def set_site(self, site):
        self.site = site
        directives.register_directive(
            'foundation5_accordion', Foundation5Accordion)
        Foundation5Accordion.site = site
        return super(Plugin, self).set_site(site)


class Foundation5Accordion(Directive):
    """ Restructured text extension for inserting slideshows."""
    has_content = True

    def run(self):
        if len(self.content) == 0:  # pragma: no cover
            return

        if self.site.invariant:  # for testing purposes
            accordion_id = 'accordion_' + 'fixedvaluethatisnotauuid'
        else:
            accordion_id = 'accordion_' + uuid.uuid4().hex

        elements = []
        while True:
            pass

        for line in self.content:
            pass

        output = self.site.template_system.render_template(
            'foundation5_accordion.tmpl',
            None,
            {'accordion_content': elements, 'accordion_id': accordion_id}
        )
        return [nodes.raw('', output, format='html')]


directives.register_directive('foundation5_accordion', Foundation5Accordion)
