# ADFD

[![Build Status](https://travis-ci.org/ADFD/adfd.svg)](https://travis-ci.org/ADFD/adfd)

Crude CMS / static website generator using the database of a phpBB Board as data source. 

At the moment still very specific to the needs of the forum it is created for and pretty alpha on the design side.

Takes a site description (YAML) from a special topic in the board or a file, fetches topics and meta data from the phpBB database and makes it available as a web site (either dynamic with Flask or frozen by Flask-FlatPages + Frozen-Flask). 

Frontend is based on Zurb Foundation 6.
