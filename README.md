# ADFD

[![Build Status](https://travis-ci.org/ADFD/adfd.svg)](https://travis-ci.org/ADFD/adfd)

Crude CMS / static website generator using the database of a phpBB Board as data source. 

At the moment still very specific to the needs of the forum it is created for and pretty alfa on the design side.

Takes a site description (YAML), fetches the topics and meta data from the phpBB database and makes it available as a web site (either dynamic with Flask or frozen by Flask-FlatPages + Frozen-Flask). 

Frontend is based on Zurb Foundation 6.
