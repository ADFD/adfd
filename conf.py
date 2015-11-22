# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time
from nikola import filters

from LICENSE import LICENSE_LINK as LICENSE
from adfd import structure

BLOG_AUTHOR = "ADFD"  # (translatable)
BLOG_TITLE = "ADFD"  # (translatable)
SITE_URL = "http://adfd.org/"
# This is the URL where Nikola's output will be deployed.
# If not set, defaults to SITE_URL
# BASE_URL = "http://adfd.org/"
BLOG_EMAIL = "webmaster@adfd.org"  # todo make sure mail address exists
BLOG_DESCRIPTION = "Offizielle Webseite des ADFD"  # (translatable)

# Final output is <img src="LOGO_URL" id="logo" alt="BLOG_TITLE">.
# The URL may be relative to the site root.
LOGO_URL = '/images/logo78x81.png'

THEME = "base-foundation5-jinja"

# todo deploy to different places depending env (e.g. vagrant or not)
# OUTPUT_FOLDER = 'output'

# todo figure out a sensible demotion policy
# The <hN> tags in HTML generated by certain compilers (reST/Markdown)
# will be demoted by that much (1 → h1 will become h2 and so on)
# This was a hidden feature of the Markdown and reST compilers in the
# past.  Useful especially if your post titles are in <h1> tags too, for
# example. (defaults to 1.)
# DEMOTE_HEADERS = 1

# The difference between POSTS and PAGES is that POSTS are added
# to feeds and are considered part of a blog, while PAGES are
# just independent HTML pages.
# POSTS = (("posts/*.rst", "posts", "post.tmpl"), ...)
# PAGES = (("stories/*.rst", "stories", "story.tmpl"), ...)
PAGES = [
    # fixme finding stuff in sibfolders not tested yet ...
    ("content/static/*.html", "", "story.tmpl"),
    ("content/topics/*.html", "", "story.tmpl"),
]
POSTS = []


# todo use this to deploy foundation build into output
# One or more folders containing files to be copied as-is into the output.
# The format is a dictionary of {source: relative destination}.
# Default is:
# Which means copy 'files' into 'output'
FILES_FOLDERS = {
    'static': '',
    'themes/base-foundation5-jinja/core/css': 'assets/css',
    'themes/base-foundation5-jinja/core/js': 'assets/js',
    'themes/base-foundation5-jinja/core/bower_components/'
    'foundation-icon-fonts': 'assets/fonts/foundation-icon-fonts',
    'themes/base-foundation5-jinja/core/bower_components':
        'assets/bower_components',
}

# Create by default posts in one file format?
# Set to False for two-file posts, with separate metadata.
ONE_FILE_POSTS = False

# Writes tag cloud data in form of tag_cloud_data.json.
WRITE_TAG_CLOUD = False

# Final location for the main blog page and sibling paginated pages is
# output / TRANSLATION[lang] / INDEX_PATH / index-*.html
INDEX_PATH = "blog"

REDIRECTIONS = []

# todo consider using nikola plugin -i ping
# call with nikola deploy <command>
DEPLOY_COMMANDS = {
    'default': ["rsync -rav --delete output/ mj13.de:/home/www/privat/neu"],
    'check': ['nikola check -l'],
}
COMMENT_SYSTEM_ID = None  # silence deploy warning (default testaccount)

# todo use this instead of hardcoding it
# FAVICONS contains (name, file, size) tuples.
# Used to create favicon link like this:
# <link rel="name" href="file" sizes="size"/>
# FAVICONS = (("icon", "/favicon.ico", "16x16"),
#             ("icon", "/icon_128x128.png", "128x128"))

# Create index.html for page (story) folders?
# WARNING: if a page would conflict with the index file (usually
#          caused by setting slug to `index`), the STORY_INDEX
#          will not be generated for that directory.
STORY_INDEX = True
INDEX_FILE = "index.html"

# If a link ends in /index.html,  drop the index.html part.
# http://mysite/foo/bar/index.html => http://mysite/foo/bar/
# (Uses the INDEX_FILE setting, so if that is, say, default.html,
# it will instead /foo/default.html => /foo)
# (Note: This was briefly STRIP_INDEX_HTML in v 5.4.3 and 5.4.4)
STRIP_INDEXES = True
# This can be disabled on a per-page/post basis by adding
#    .. pretty_url: False
# to the metadata.
PRETTY_URLS = True

ROBOTS_EXCLUSIONS = []  # site is not root

# You will also get gist, nikola and podcast
MARKDOWN_EXTENSIONS = ['fenced_code', 'codehilite', 'extra']

SHOW_SOURCELINK = False
COPY_SOURCES = False

# By default, Nikola generates RSS files for the website and for tags, and
# links to it.  Set this to False to disable everything RSS-related.
# GENERATE_RSS = True

# A search form to search this site, for the sidebar. You can use a Google
# custom search (http://www.google.com/cse/)
# Or a DuckDuckGo search: https://duckduckgo.com/search_box.html
# Default is no search form.
# (translatable)
# SEARCH_FORM = ""
#
# This search form works for any site and looks good in the "site" theme where
# it appears on the navigation bar:
#
# SEARCH_FORM = """
# <!-- Custom search -->
# <form method="get" id="search" action="//duckduckgo.com/"
#  class="navbar-form pull-left">
# <input type="hidden" name="sites" value="%s"/>
# <input type="hidden" name="k8" value="#444444"/>
# <input type="hidden" name="k9" value="#D51920"/>
# <input type="hidden" name="kt" value="h"/>
# <input type="text" name="q" maxlength="255"
#  placeholder="Search&hellip;" class="span2" style="margin-top: 4px;"/>
# <input type="submit" value="DuckDuckGo Search" style="visibility: hidden;" />
# </form>
# <!-- End of custom search -->
# """ % SITE_URL
#
# If you prefer a Google search form, here's an example that should just work:
# SEARCH_FORM = """
# <!-- Custom search with Google-->
# <form id="search" action="//www.google.com/search"
#  method="get" class="navbar-form pull-left">
# <input type="hidden" name="q" value="site:%s" />
# <input type="text" name="q" maxlength="255"
#  results="0" placeholder="Search"/>
# </form>
# <!-- End of custom search -->
# """ % SITE_URL

# Use content distribution networks for jQuery, twitter-bootstrap css and js,
# and html5shiv (for older versions of Internet Explorer)
# If this is True, jQuery and html5shiv are served from the Google CDN and
# Bootstrap is served from BootstrapCDN (provided by MaxCDN)
# Set this to False if you want to host your site without requiring access to
# external resources.
# USE_CDN = False

# Check for USE_CDN compatibility.
# If you are using custom themes, have configured the CSS properly and are
# receiving warnings about incompatibility but believe they are incorrect, you
# can set this to False.
# USE_CDN_WARNING = True

# Extra things you want in the pages HEAD tag. This will be added right
# before </head>
# (translatable)
# EXTRA_HEAD_DATA = ""
# Google Analytics or whatever else you use. Added to the bottom of <body>
# in the default template (base.tmpl).
# (translatable)
# BODY_END = ""

# If you hate "Filenames with Capital Letters and Spaces.md", you should
# set this to true.
UNSLUGIFY_TITLES = True

# TODO figure out how this works properly and switch on in production
USE_BUNDLES = False

# Plugins you don't want to use. Be careful :-)
# DISABLED_PLUGINS = ["render_galleries"]

# todo move foundation plugins somewhere sensible
# EXTRA_PLUGINS_DIRS = []

# List of regular expressions, links matching them will always be considered
# valid by "nikola check -l"
# LINK_CHECK_WHITELIST = []

# Templates will use those filters, along with the defaults.
# Consult your engine's documentation on filters if you need help defining
# those.
# TEMPLATE_FILTERS = {}

# Put in global_context things you want available on all your templates.
# It can be anything, data, functions, modules, etc.
GLOBAL_CONTEXT = {
    'sansSerifFont': 'Ubuntu:bold',
    'serifFont': 'Vollkorn',

    # 'sansSerifFont': 'Open+Sans',
    # 'serifFont': 'Bree+Serif',

    # 'sansSerifFont': 'Pontano+Sans',
    # 'serifFont': 'Crimson+Text',

    # 'sansSerifFont': 'Allerta',
    # 'serifFont': 'Bevan',

    # 'sansSerifFont': 'Raleway',
}

# Add functions here and they will be called with template
# GLOBAL_CONTEXT as parameter when the template is about to be
# rendered
GLOBAL_CONTEXT_FILLER = []

SHOW_BLOG_TITLE = False

NAVIGATION_LINKS = structure.NAVIGATION_LINKS
DEFAULT_LANG = "de"
TRANSLATIONS = {DEFAULT_LANG: ""}
TRANSLATIONS_PATTERN = "{path}.{lang}.{ext}"

TIMEZONE = "Europe/Berlin"
DATE_FORMAT = '%d.%m.%Y'
DATE_FANCINESS = 0
CACHE_FOLDER = '.cache'

CONTENT_FOOTER = (
    'Inhalte &copy; {date} <a href="mailto:{email}">{author}</a> {license}')
CONTENT_FOOTER_FORMATS = {
    DEFAULT_LANG: (
        (),
        {
            "email": BLOG_EMAIL,
            "author": BLOG_AUTHOR,
            "date": time.gmtime().tm_year,
            "license": LICENSE
        }
    )
}

COMPILERS = {
    # "bbcode": ('.bb',),
    "html": ('.html', '.htm'),  # assumes file is HTML and just copies it
    # "rest": ('.rst', '.txt'),
    # "rest_html5": ('.rst', '.txt'),  # needs rest-html5 plugin
    # "markdown": ('.md', '.mdown', '.markdown'),
    # "php": ('.php',),  # rendered fully with all templates
    # "pandoc": ('.rst', '.md', '.txt'),  # disabled by default (conflicts)
}

# see https://getnikola.com/handbook.html#post-processing-filters>
FILTERS = {
    ".html": [
        filters.typogrify,
        # needs tidy5 command http://www.html-tidy.org/
        # WARNING no ubuntu package yet: http://www.htacg.org/binaries/
        filters.html_tidy_nowrap,
    ],
    # ".js": [filters.closure_compiler],
    # ".jpg": ["jpegoptim --strip-all -m75 -v %s"],
}

HYPHENATE = True  # add soft hyphens for noce looking justifed text blocks
