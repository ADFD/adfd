#####
TODOS
#####
* move plugins to theme
* move files in better structure
* when creating post structure use the information provided here to
* replace links to forum topics/post to website articles

######
BBCODE
######

Discourse has an phpBB importer - try this out just for kicks!
https://meta.discourse.org/t/importing-from-phpbb3/30810
https://meta.discourse.org/t/best-way-to-install-discourse-on-my-server/19708/7
http://blog.discourse.org/2013/03/localizing-discourse/

#######
IMAGERY
#######

as part of import: extract all images that are not hosted on adfd.org to check copyright

Create visuals with https://github.com/google/deepdream

#######
Plugins
#######
https://plugins.getnikola.com/#rest_html5

#######
Filters
#######
* typogrify and pyphen: http://ralsina.me/tr/es/posts/new-in-nikola-v6-typography.html
    * https://pypi.python.org/pypi/typogrify
    * pyphen http://pyphen.org/

html tidy (tidy5)
#################
http://tidy.sourceforge.net/docs/quickref.html
needs tidy5 command http://www.html-tidy.org/
WARNING no ubuntu package yet: http://www.htacg.org/binaries/


Hyphenation
###########
using pyphon atm, but seems to be coming up in css as well: https://css-tricks.com/almanac/properties/h/hyphenate/

##########
Foundation
##########
http://foundation.zurb.com/docs/

what is where in sass: http://foundation.zurb.com/docs/sass-files.html
how to use sass: http://foundation.zurb.com/docs/using-sass.html

==========
Experiment
==========
CodePen http://codepen.io/anon/pen/qdQWJG

=========
Resources
=========
Zurb university: http://zurb.com/library
Grids in founddation5 https://www.youtube.com/watch?v=kk6KpKK5Jjc
templates: http://foundation.zurb.com/templates.html

===========
Inspiration
===========
http://www.harimari.com/

######
Design
######
====================
Schräger Hintergrund
====================
http://codepen.io/rafibomb/pen/ogRjXb/

==================
Sidebar/Navigation
==================

shrinking sidebar: http://webdesign.tutsplus.com/tutorials/how-to-build-a-shrinking-fixed-top-bar-with-foundation--cms-20895
sidebar examples: http://line25.com/articles/modern-examples-of-the-classic-sidebar-menu-layout
sticky sidebar: http://zurb.com/building-blocks/sticky-sidebar
off cavas: http://zurb.com/university/lessons/transform-a-sidebar-into-a-slick-off-canvas-menu

===========
Typographie
===========
Make headers automatically fit their container: http://fittextjs.com/
caps drop: http://demosthenes.info/blog/961/Big-Beautiful-DropCaps-with-CSS-initial-letter
viewport sized typography: https://css-tricks.com/viewport-sized-typography/
modular scale http://foundation.zurb.com/forum/posts/18180-foundation-5-and-modular-scale

Inspiration
===========
http://limi.net/articles/firefox-acid3/
http://www.quora.com/What-are-some-examples-of-blogs-with-beautiful-typography

Fonts
=====
google fonts: https://www.google.com/fonts#
optimizing google fonts: http://googlewebfonts.blogspot.de/2010/09/optimizing-use-of-google-font-api.html
http://www.forbes.com/sites/allbusiness/2014/03/06/10-best-sans-serif-web-fonts-from-google-fonts-library/
http://diveintohtml5.info/about.html | http://www.thibault.org/fonts/essays/
http://designshack.net/articles/css/10-great-google-font-combinations-you-can-copy/
http://designshack.net/articles/typography/10-more-great-google-font-combinations-you-can-copy/

Icon Fonts
==========
http://fortawesome.github.io/Font-Awesome/icons/
http://fortawesome.github.io/Font-Awesome/examples/
https://www.google.com/design/icons/
https://github.com/google/material-design-icons/ (bower installable)

=====
Color
=====
**cool** http://jackiebalzer.com/color
blue designs: https://webdesignledger.com/55-beautifully-blue-web-designs-to-inspire-you#sthash.p2H6TI0w.dpbs
http://riccardoscalco.github.io/crayon/
http://www.smashingmagazine.com/2010/01/color-theory-for-designers-part-1-the-meaning-of-color/

==============
Push Pull Grid
==============
Found the solution in a separate thread! Start with the order you want in the source for mobile, then use the push/pull classes to bend it around for the LARGER sizes. In other words, approach it from the opposite end.
http://foundation.zurb.com/forum/posts/726-foundation-push-and-pull-class-in-grid
http://codepen.io/rafibomb/pen/xfJph

======
Slider
======

orbit is deprecated: http://foundation.zurb.com/forum/posts/14504-moving-on-from-developing-orbit

========
Advanced
========
Proper CSS
==========
Pseudo Elements
---------------
* https://css-tricks.com/pseudo-element-roundup/
* https://css-tricks.com/float-center/

Selectors
---------
http://wiki.selfhtml.org/wiki/CSS/Selektoren
descendant selectors: http://www.w3.org/TR/CSS2/selector.html#descendant-selectors
https://signalvnoise.com/posts/3003-css-taking-control-of-the-cascade

Misc
====
landing pages: http://www.webdesignerdepot.com/2015/07/the-ultimate-guide-to-designing-landing-pages-that-convert/
https://html5boilerplate.com/
https://www.jamesstone.com/blog/the-five-secrets-of-sass-foundation/
