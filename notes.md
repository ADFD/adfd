# Plan for 2.0

## Introduce a proper pipeline and separation of concerns

Re introduce what was thrown out during the last push for making it more accessible and run as process on the server that immediately updates the site. That was convenient for the user, but in the rush to get that to work I sacrificed clarity and simplicity of the process.

Move back to a proper process and separate ADFD specific things from generalizable things, to make this useful for others who might want to use this.

### Basic flow

The basic idea is still to grab user edited content from a phpbb forum formatted in (extended) bbcode to use as a basis for a static website. Only the first step is really dependent on the structure of a phpbb database to extract the content. From then on it is only dealing with files that contain bbcode.

1. take the structure information (yaml file or a special meta post in the forum that contains the structure)
2. fetch all the posts from the db and save them to the file system in a structure that already mirrors the site structure
3. Render a static website taking the folder with the files as input

### Other activities that are part of dev 

TODO collect here, what else this tool is doing and separate it out.

Rough idea

#### adfd dev tools

provide a vagrantfile to do local dev of the actual forum for upgrades and bug fixes.

#### adfd db-tools

Split this into its own reposotory and host it in a private repo
 
    * create and fetch db dumps
    * load them into a local db
    * extract posts on request and save them flat as `<post-id.bbcode>`
    
#### adfd stat-tools

* needs access to an existing adfd db containing only the public information for statistical analysis
* might be nice to package that with a Vagrantfile or something like that for other scientists to explore?

#### adfd site tools

* take a flat list of files and create a structure with folders and proper file names that already mirrors the site structure of the site, but still in bbcode
* generate a static HTML site from the structured list
* provide deployment and VCS tools (e.g. if the structured list is not new, but updated, delete removed files, add new files, and update modified files)

## Style

Replace semantic with something much simpler (23.000 lines of js???) - e.g. tailwind, bulma or something much more broadly used - e.g. bootstrap (has lots of js though ...)
