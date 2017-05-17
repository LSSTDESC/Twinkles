
## desc-0000-twinkles-1-phosim-pipeline
# Twinkles 1 PhoSim Pipeline and Results

*Tom Glanzman and others*

We describe the implementation of the Twinkles 1 PhoSim pipeline, taking pre-made instance catalogs and processing them into e-images. The SLAC workflow engine `pipeline-II` is used to handle the processing, which was performed on the batch system at SLAC. XXX images were generated in a wallclcok time of XXX days, at an efficiency of XX%


## Editing this Paper

Fork and/or clone the project repo, and then
edit the primary file. The name of this file will vary according to its format, but it should be one of either `main.rst` (if it's a [`reStructuredText`](http://docutils.sourceforge.net/rst.html) Note), `main.md` (if it's a [`Markdown`](https://github.com/adam-p/Markdown-here/wiki/Markdown-Cheatsheet) Note), `main.ipynb` (if it's an [`IPython Notebook`](https://ipython.org/notebook.html)) or `main.tex` (if it's a latex Note or paper).
Please use the `figures` folder for your images.

## Building this Paper

GitHub is our primary distributor for LSST DESC Notes:
once the Note has been merged into the project repo's master branch, it will be visible as a *shared* (but not *published*) paper. The presentation of Notes will be improved later, as the LSST DESC Publication System evolves.

You can compile latex papers locally with
```
make  [apj|apjl|prd|prl|mnras]
```
`make` with no arguments compiles the latex using the `default_format` stored in `.metadata.json`. Choosing `tex` causes the paper to be made using the `texmf/styles/lsstdescnote.cls` class, with commands defined in `texmf/styles/lsstdesc_macros.sty`. Don't edit these style files, as you may want to replace them with newer versions as they become available. Instead, use the `macros.tex` file to add your own `newcommand`'s and `def`'s.

At present, the Makefile is only used to compile latex. In future, we hope to enable compilation of jupyter notebooks, `Markdown` and `reStructuredText` format notes into PDF as well.

## Updating the Styles and Templates

From time to time, the latex style files will be updated: to re-download the latest versions, do
```
make update
```
This will over-write your folder's copies - but that's OK, as they are not meant to be edited by you!
The template files (`main.*` etc) are also likely to be updated; to get fresh copies of these files, do
```
make templates
```
However, since you will have edited at least one of the templates in your folder, `make templates` creates a special `templates` folder for you to refer to. Finally, to get *new* style or template files that are added to the `start_paper` project, you'll need to first get the latest `Makefile`, and then `make update` and/or `make templates`. The command to obtain the latest `Makefile` is
```
make new
```
This will add the latest `Makefile` to your `templates` folder. If you want to over-write your existing `Makefile`, you can do
```
make upgrade
```

## Automatic PDF Sharing

If this project is in a public GitHub repo, you can use the `.travis.yml` file in this folder to cause [travis-ci](http://travis-ci.org) to compile your paper into a PDF in the base repo at GitHub every time you push a commit to the master branch. The paper should appear as:

**https://github.com/DarkEnergyScienceCollaboration/Twinkles/tree/pdf/desc-0000-twinkles-1-phosim-pipeline.pdf**

To enable this service, you need to follow these steps:

1. Turn on travis continuous integration, by [toggling your repo on your travis profile](https://travis-ci.org/profile). If you don't see your repo listed, you may not have permission to do this: in this case, [contact an admin via the issues](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues/new?body=@DarkEnergyScienceCollaboration/admin).
2. Get a [GitHub "personal access token"](https://github.com/settings/tokens). Choose the "repo" option.
3. Set the `GITHUB_API_KEY` environment variable with the value of this token at your repo's [travis settings page](https://travis-ci.org/DarkEnergyScienceCollaboration/Twinkles/settings).
4. Copy the `.travis.yml` file in this folder to the top level of your repo (or merge its contents with your existing `.travis.yml` file).
Edit the final `git push` command with your GitHub username.  
Commit and push to trigger your travis build, but note that the PDF will only be deployed if the master branch is updated.
