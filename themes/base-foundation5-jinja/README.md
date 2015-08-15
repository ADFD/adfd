# TODO

## fix classes

active
author
breadcrumb
breadcrumbs
byline
byline-name
carousel-indicators
carousel-inner
carousel-control
commentline
comments
dateline
dsq-brlink
dt-published
e-content
entry-content
entry-summary
entry-title
fb-comments
fb-comments-count
feedlink
fn
g-comments
g-commentcount
h-entry
hentry
hidden-print
IDCommentsReplace
icon-file
icon-folder-open
image-reference
item
left
linkline
listdate
listpage
listtitle
livefyre-commentcount
metadata
muut
next
p-name
p-summary
p-category
pager
post-{{ post.meta('type') }} (title, meta, micro)
post-list
post-list-item
postlist
postindex
postindexpager
postpage
postpromonav
posttranslations
posttranslations-intro
previous
published
reference
right
searchform
sourceline
sr-only                     -> foundation:show-for-sr
st-only-focusable           -> foundation:show-on-focus
storypage
tagindex
tagpage
tags
thumbnail
thumbnails
translations
u-url
vcard

## fix ids

* todo check id="*"


# Base Foundation 5 Jinja

This theme is adding the foundation 5 sass project to the base template. 

This is a good starting point for using Nikola with foundation 5.

## Foundation installation

inside assets is the [recommended installation](http://foundation.zurb.com/docs/sass.html#cli).

It was set up using the Linux toolchain as described here:

    [sudo] npm install -g bower grunt-cli
    [sudo] gem install foundation
    rbenv rehash  # if you use rbenv
    gem install compass
    foundation new base-foundation5-jinja
    cd base-foundation5-jinja
    gem install bundler
    bundle

Addtional packages:

    foundation-icon-fonts
    
### Styling:
    
    bundle exec compass watch  # watch assets and recompile sass on changes

### Kepp bower components up to date:
    
    bower update
    
Contents of the installation are described [here](http://foundation.zurb.com/docs/sass-files.html)

How to use: http://foundation.zurb.com/docs/using-sass.html

## Limitations

bundles and CDN are not supported yet.
