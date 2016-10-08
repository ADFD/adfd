[![Build Status](https://travis-ci.org/ADFD/adfd.svg)](https://travis-ci.org/ADFD/adfd)

# ADFD board <-> website bridge 

Crude CMS / static website generator using the database of a phpBB Board as data source. 

Very specific to the needs of the [ADFD](http://adfd.org).

Takes a site description (YAML) from a special topic in the board or a file, fetches topics and meta data from the phpBB databas, transforms them to HTML and generates web site (either dynamic with [Flask](http://flask.pocoo.org/) for development or static for production with [Frozen-Flask](http://pythonhosted.org/Frozen-Flask/)). Uses [Semantic-UI](http://semantic-ui.com).


