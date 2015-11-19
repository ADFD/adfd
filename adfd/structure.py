"""
This is just a hunch, but atm I feel that I make my life easier if I create the
whole structure of the site from an input of categories and a set of Articles
programmatically and then create the navigation and whatever the website
generator needs here.

rough idea:

Website structure is represented by a hierarchical tree. Each tree node holds
a list of articles.

Each Article has
    * ID that is used to localize the file with the content
    * and the ordering comes from place in the list.
    * metadata from accompanying file (e.g. tags, slug, ...)

"""
