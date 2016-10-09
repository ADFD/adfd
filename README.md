[![Build Status](https://travis-ci.org/ADFD/adfd.svg)](https://travis-ci.org/ADFD/adfd)

# ADFD board <-> website bridge 

Crude CMS / static website generator using the database of a phpBB Board as data source. 

Takes a site description (YAML) from a special topic in the board (or a file), fetches topics and meta data from the phpBB database, transforms them to HTML and generates web site (either dynamic with [Flask](http://flask.pocoo.org/) for development or static for production with [Frozen-Flask](http://pythonhosted.org/Frozen-Flask/)). Uses [Semantic-UI](http://semantic-ui.com).

Very specific to the needs of the [ADFD](http://adfd.org), but feel free to use the code to adapt this to your own needs if you find it useful.

#  Overview

The system is designed to be used by members of the board who have editing rights in the forum that contains the topics that are transformed into website articles. Therefore all information necessary for building the web site must be contained in form of editable data in forum posts. The used data format for setting this kind of data comes in the form of specific tags that contain simple [yaml](http://www.yaml.org/) data structures. These can easily be extracted and used in the generator code.

## Defining the site structure

The structure of the web site is defined in [here (members only)](http://adfd.org/austausch/viewtopic.php?f=54&t=12109). Every article should be referenced exactly once (**Development Note:** not necessary for development, but that should be the end result). 

The page structure consists of categories and articles (see [model.py](adfd/model.py)). The [navigation](adfd/site/navigation.py) is generated automatically from a sorted nested dictionary containing categories and articles. Categories **can but not must** have their own start page that can be visited (results in clickable link in menu and breadcrumbs). Here is an example of YAML used to define a simple site structure:

    Home | 3:
      - Main Category 1 | 13:
        - 42
        - Sub Category 1 | 32:
          - 43
          - Article Title | 112
      - Main Category 2:
        - 72
      - MainCategory3 | 4
        - 9736
        - 873

The start page of the article will be fetched from the phpBB topic with ID 3 (**Note:** for the root the name "Home" does not matter as it will not be used for the root of the web page). Below the root are three main categories - two of which have their own start page (name and topic ID are separated by the pipe character). "Main Category 1" also contains another category with Topic 13 as its start page and the topics 43 and 112 as articles in that category.

The page structure presents itself to the user as nested menu. The Urls are made [semantic](https://en.wikipedia.org/wiki/Semantic_URL) by building up a path from the [slugified](https://en.wikipedia.org/wiki/Semantic_URL#Slug) names of the categories and articles leading to the endpoint. For example `http://some-page.com/main-category-1/sub-category-1/some-article` would be the URL of the article fetched from topic 43 that has the title "Some Article" (the title is also fetched directly from the topic and does not have to be set in the structure (but can be if wanted/needed as seen for topic 112 that has an alternative title given directly in the structure)).

## Meta data

To add meta data to a post use the custom BBCode tag `meta` and set some YAML variables. Example:

    [meta]
    sourceTopicId: 1123
    firstPostOnly: False
    allAuthors: Peter, Paul, Mary
    [/meta]

This will be accessible then as attributes of `ContentContainer` so they can be accessed like `container.md.sourceTopicId` or `container.md.allAuthors`.

see [model.py](adfd/model.py) and [metadata.py](adfd/metadata.py).

Technically arbitrary data can be set with this mechanism, but what is actually used is defined and documented in the `PageMetadata` class.

## [Still in planning phase] Redirection from Forum to website

Many articles on the website originate from topics in the ADFD board. When the website is online, those topics will be masked by redirecting requests to the topic on the board to their corresponding static web page. 

For this to work articles that should appear on the website often start as copies from the source that know about there source (topicId of the source topic). They all reside in [Inhalt (members only)](http://adfd.org/austausch/viewforum.php?f=54). If an article started its life explicitly as website article simply does not contain a link to it's source (all else being the same). **Development note:** for the time of development this is not necessary, but when the page goes live this should be completed to be able to use the redirect mechanism.


## Redirect from forum thread to article

Articles that are on the web site should override the article it originates from. Therefore routes to those articles should be redirected to the corresponding article.

* Every article that should end up on the website should be copied from the original
* The copy has the topicID of the source article as metadata
* That article is the source for the website
* As soon as the article is online. The original article will redirect to the web site
* How this is done needs to be clarified (see next section)

### Possible implementations 

(ordered from most to least favorite)

#### Special redirect tag embedded in post

Javascript solution but easiest to implement.

BBCode tag `redirect` (only usable by members with special permissions) that adds redirect directly in the post. Example:

    [redirect]http://www.google.com/[/redirect]

Renders to: 
    
    <script type="text/javascript">
        window.location = "http://www.google.com/";
    </script>

#### phpBB extension 

that reads metadata from the source article that contains the redirect path

#### Apache rewrite rules

Most effective(?) but maybe also hardest to develop (lots of different urls can lead to the same thread (e.g. by topicId or postIds)), test and automate.

# Credits

Dan Watson [bbcode parser](https://github.com/dcwatson/bbcode) (basis for own version)

# License

[BSD 3-clause License](https://opensource.org/licenses/BSD-3-Clause). See [LICENSE](./LICENSE) for more information.
