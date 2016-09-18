# New Feature: live view

Instead of reading the contents from prepared files I want to do it on the fly.

## Render Topic directly from DB

* fetch topicId from site description
* try to fetch topic directly from db (make Page object from it)
* If fails: try to fetch topic from filesystem
* somehow mark the topic as live view or from file visibly

## Render Site structure from a special Topic that contains the structure as YAML

* Transfrom site description to YAML
* Create topic containing site description
* read description from topic and create structure from it

## Caching

Only if it is painfully slow ...

* compare timestamps / hashes to determine if something changed

# Problems

* hyphenate still screws up links