#######################
How to set up Weeklies
#######################
We are trying out GitHub Pages to store weekly summaries.

==============
Prerequisities
==============
* `Pandoc <http://pandoc.org>`_
* Twinkles Live Notes Google Doc
* Access to the gh-pages branch of the Twinkles repository

Recipe
----------

* Copy the notes for that week into a separate Google Doc
* Click File->Download As and choose Microsoft Word 
* Checkout the gh-pages branch of the Twinkles repository
* Find the weeklies under gh-pages/weekly
* If necessary, add a new month or year following the directory structure
* cd into the directory that will contain the new weekly HTML doc
* Run pandoc
pandoc <pathToWeekly/weekly_<date>.docx -t html --extract-media=images -s --normalize --css ../../../stylesheets/pandoc.css --template ../../../stylesheets/html.template -o weekly_<date>.html

* Review the resulting HTML and edit if necessary
* Edit weekly/index.html and add a link to the new weekly
* git add, commit, and push to the Twinkles gh-pages branch

To Do
------
* Use a template in pandoc to set up the style of our weeklies automatically
* Automate setting of the Title
* Try travis-ci to automate the creation of the HTML via pandoc

