# ADFD

[![Build Status](https://travis-ci.org/ADFD/adfd.svg)](https://travis-ci.org/ADFD/adfd)

Crude CMS / static website generator using the database of a phpBB Board as data source. 

Very specific to the needs of the forum it is created for.

Takes a site description (YAML) from a special topic in the board or a file, fetches topics and meta data from the phpBB database and makes it available as a web site (either dynamic with [Flask](http://flask.pocoo.org/) for development or made static for production with [Frozen-Flask](http://pythonhosted.org/Frozen-Flask/)). 

Frontend built with [Semantic-UI](http://semantic-ui.com).
