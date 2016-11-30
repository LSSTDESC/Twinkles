# Twinkles
### A Tiny Simulated LSST Survey

10 years. 6 filters. 1 tiny patch of sky. Thousands of time-variable cosmological distance probes.

![Co-add image from a few hundred *gri* images of the Twinkles 1 field, from Run 1.1 ](https://cloud.githubusercontent.com/assets/945715/14874645/529e031a-0cb7-11e6-92a7-a000c8514d11.png)

In the LSST Dark Energy Science Collaboration we are interested in
making high accuracy cosmological measurements of type IA supernovae and
strong gravitational lens time delays with the Large Synoptic Survey
Telescope data. To do this, we need to build a number of software
instruments, and these must be tested and validated against realistic
simulated data. We are using the LSST photon simulator `PhoSim` to
generate a ten year, 6-filter set of mock images of a small patch of
moderate Galactic latitude sky, containing an unrealistic overdensity of
supernovae and lensed quasars but with realistic observing conditions
and cadence. See the documents below for more details of our evolving
plans and progress to date.

### Latest News

[![Build Status](https://travis-ci.org/LSSTDESC/Twinkles.svg?branch=master)](https://travis-ci.org/LSSTDESC/Twinkles) [![Coverage Status](https://coveralls.io/repos/github/LSSTDESC/Twinkles/badge.svg?branch=master)](https://coveralls.io/github/LSSTDESC/Twinkles?branch=master)

* We have a [public website](https://darkenergysciencecollaboration.github.io/Twinkles/), whose main function is to host the **["Twinkles Weeklies"](https://darkenergysciencecollaboration.github.io/Twinkles/weekly/index.html)**. These are brief summaries from our weekly meetings, with links to the progress that is reported there.
* Check out **[our most recently updated GitHub issues](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc)** to see what we're working on at the moment. You can filter our [issue list](https://github.com/DarkEnergyScienceCollaboration/Twinkles) in various ways to see what we're up to more generally.
* For a quick overview of how far we've got so far, you can peruse our **[Summer 2016 Twinkles 1 Progress Report](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Summary_2016Q2.md)**
* We're keeping our DM Level 2 measurements in **[databases](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Database.md)**, using our homegrown emulator **[`Pserv`](https://github.com/DarkEnergyScienceCollaboration/Pserv)** while Qserv is still under development.
* Veuillez s'il vous plait consulter le Twinkles **[difference imaging sandbox](https://github.com/DarkEnergyScienceCollaboration/Twinkles/wiki/A-sandbox-for-difference-imaging)**
* Our goal for the March 2016 collaboration meeting was to produce and begin analyzing a small prototype Twinkles 1 dataset: **[Run 1](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Run1.md)**
* We are a **[2015 DESC Taskforce](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Taskforce2015_Twinkles.md)**, assembled in order to kick-start development ready for our first data release at DC1.
* **[Twinkles is on the sky!](http://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/examples/notebooks/First%20Light.ipynb)**  LSST DESC Hack Day, February 2015.
* **[Initial design for the Twinkles pipeline](https://confluence.slac.stanford.edu/display/LSSTDESC/Twinkles+flow+chart)** LSST DESC Hack Day, February 2015.


### Read More

Some of these links are quite old, but will have to do while we write
up our progress so far as a set of LSST DESC Notes.
* [Scientific and Technical Motivation](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Motivation.md)
* [Survey Design](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Design.md)
* [Data Generation and Analysis: Pipeline Design](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Organisation.md)
* [Getting Set Up to Run Twinkles Simulations](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Setup.md)


### People

* Phil Marshall (SLAC,
[@drphilmarshall](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3Adrphilmarshall))
* Michael Wood-Vasey (Pitt,
[@wmwv](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3Awmwv))
* Richard Dubois (SLAC,
[@richardxdubois](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3Arichardxdubois))
* Rahul Biswas (UW,
[@rbiswas4](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3Arbiswas4))
* Jim Chiang (SLAC,
[@jchiang87](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3Ajchiang87))
* Scott Daniel (UW,
[@danielsf](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3Adanielsf))
* Seth Digel (SLAC,
[@sethdigel](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3Asethdigel))
* Tom Glanzman (SLAC,
[@TomGlanzman](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3ATomGlanzman))
* Tony Johnson (SLAC,
[@tony-johnson](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3Atony-johnson))
* Bryce Kalmbach (UW,
[@jbkalmbach](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3Ajbkalmbach))
* Heather Kelly (SLAC, [@heather999](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3Aheather999))
* Simon Krughoff (UW,
[@SimonKrughoff](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3ASimonKrughoff))
* Curtis McCully (LCOGT)
* Saba Sehrish (Fermilab)


Check out all of our [GitHub contributions](https://github.com/DarkEnergyScienceCollaboration/Twinkles/graphs/contributors)!

### Credits etc

This is work in progress. If you would like to cite the Twinkles project in your research, please use '(LSST DESC, in prep.)' for now, and provide the [URL of this repository](https://github.com/DarkEnergyScienceCollaboration/Twinkles). We aim to release our data products along with a companion paper during the DESC DC1 era, c. 2016. If you are interested in this project, feel free to post greetings, comments or queries to the [issues](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues).  

All content is Copyright 2015, 2016 the above authors, and distributed under the MIT License, which means you can do whatever you like with it but agree not to blame us - but we'd prefer it if you kept in touch while you did so!
