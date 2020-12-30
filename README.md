[![Build Status](https://travis-ci.com/ADFD/adfd.svg)](https://travis-ci.com/ADFD/adfd)

**NOTE:** very specific to the needs of the [ADFD](http://adfd.org), but feel free to use the code to adapt this to your own needs if you find it useful.

[ISSUES (only accessible to active contributors)](https://trello.com/b/asPQPemL/adfd-webseite)

# Build a static web page from a collection of posts in a phpBB board

Takes a site description (YAML) from a special topic in the board (or a file), fetches topics and meta data from the phpBB database, transforms them to HTML and generates a web site (either dynamic with [Flask](http://flask.pocoo.org/) for development or static for production with [Frozen-Flask](http://pythonhosted.org/Frozen-Flask/)). Uses [Semantic-UI](http://semantic-ui.com).

##  How it works

Members of a phpBB board create and edit posts which will be converted to static articles on the web page. They also control the structure of the website by editing a special post that contains the structure with [YAML](http://www.yaml.org/).
All information necessary for building the web site is contained in form of editable text in forum posts. The data format for setting additional meta data is passed as keyword/value pairs contained in a special bbcode section (`[meta]...[/meta]`).

## Defining the site structure

The structure of the web site is defined in [this file](adfd/web/structure.yml) for development/testing and later [here (members only)](http://adfd.org/austausch/viewtopic.php?f=54&t=12109) for production.

Every article should be referenced exactly once (**Development Note:** not necessary for development, but that should be the end result).

The page structure is a sorted hierarchical tree of categories and articles (see [model.py](adfd/model.py)). The [navigation](adfd/web/navigation.py). Categories **can but not must** have their own start page that can be visited (results in clickable link in menu and breadcrumbs). Here is an example of YAML used to define a simple site structure:

    Home | 3:
      - Main Category 1 | 13:
        - 42
        - Sub Category 1 | 32:
          - 43
          - Alternative Article Title | 112
      - Main Category 2:
        - 72
      - MainCategory3 | 4
        - 9736
        - 873

**Explanation:** The start page of the website is fetched from the phpBB topic with ID 3 (**Note:** for the root the name "Home" does not matter as it will not be used for the root of the web page). Below the root are three main categories - two of which have their own start page (name and topic ID are separated by the pipe character). "Main Category 1" also contains another category with Topic 13 as its start page and the topics 43 and 112 as articles in that category.

The page structure presents itself to the user as nested menu. The Urls are made [semantic](https://en.wikipedia.org/wiki/Semantic_URL) by building up a path from the [slugified](https://en.wikipedia.org/wiki/Semantic_URL#Slug) names of the categories and articles leading to the endpoint. For example `http://some-page.com/main-category-1/sub-category-1/some-article` would be the URL of the article fetched from topic 43 that has the title "Some Article" (the title is also fetched directly from the topic and does not have to be set in the structure (but can be if wanted/needed as seen for topic 112 that has an alternative title given directly in the structure)).

**Development Note:** this is just the first implementation - it might be extended to accomodate orphan pages or other special content, if the need comes up.

## Meta data

To add meta data to a post the custom BBCode tag `meta` can be used to pass simple key/value pairs to the generator. Example:

    [meta]
    oldTopicId: 1123
    firstPostOnly: False
    allAuthors: Peter, Paul, Mary
    [/meta]

This will be accessible then as attributes of `ContentContainer` objects. They can be accessed like `container.md.oldTopicId` or `container.md.allAuthors` (see [model.py](adfd/model.py) and [metadata.py](adfd/metadata.py)).

With this mechanism completely arbitrary data can be set, but what is actually used is defined and documented in the `PageMetadata` class.

## Development

All dev/test/build/deploy activities are automated via tox and/or the adfd cli.

    $ tox -av  # check what tox can do for you
    $ tox -e dev
    $ source .tox/dev/bin/activate
    $ adfd --help  # check what the adfd cli can do for you

# Acknowledgements

Dan Watson: [bbcode parser](https://github.com/dcwatson/bbcode) (basis for own version)

# License

[BSD 3-clause License](https://opensource.org/licenses/BSD-3-Clause). See [LICENSE](LICENSE) for more information.
