# Twinkles

10 years. 6 filters. 1 tiny patch of sky. Thousands of time-variable cosmological distance probes.

![Co-add image from a few hundred *gri* images of the Twinkles 1 field, from Run 1.1 ](https://cloud.githubusercontent.com/assets/945715/14874645/529e031a-0cb7-11e6-92a7-a000c8514d11.png)

### An LSST DESC Tiny Synoptic Survey Simulation

We are interested in making high accuracy cosmological measurements of type IA supernovae and strong gravitational lens time delays with the Large Synoptic Survey Telescope data. To do this, we need to build a number of software instruments, and these must be tested and validated against realistic simulated data. We are using the LSST photon simulator `PhoSim` to generate a ten year, 6-filter set of mock images of a small patch of moderate Galactic latitude sky, containing an unrealistic overdensity of supernovae and lensed quasars but with realistic observing conditions and cadence. See the documents below for more details of our evolving plans and progress to date.

### Latest News

[![Build Status](https://travis-ci.org/DarkEnergyScienceCollaboration/Twinkles.svg?branch=master)](https://travis-ci.org/DarkEnergyScienceCollaboration/Twinkles)

* Follow **[this link](https://github.com/DarkEnergyScienceCollaboration/Twinkles/labels/In%20Progress)** to see the issues currently being worked on.
* We're keeping our DM Level 2 measurements in **[databases](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Database.md)**, using our homegrown emulator **[`Pserv`](https://github.com/DarkEnergyScienceCollaboration/Pserv)** while Qserv is still under development. 
* Veuillez s'il vous plait consulter le Twinkles **[difference imaging sandbox](https://github.com/DarkEnergyScienceCollaboration/Twinkles/wiki/A-sandbox-for-difference-imaging)**
* Our goal for the March 2016 collaboration meeting is to produce and begin analyzing a small prototype Twinkles 1 dataset: **[Run 1](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Run1.md)**
* The requirements document (well, design and specifications) for Twinkles 1 is under construction, **[here](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Requirements/)**
* We are now a **[2015 DESC Taskforce](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Taskforce2015_Twinkles.md)**, in order to kick-start development ready for a first data release at DC1.
* **[Twinkles is on the sky!](http://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/examples/notebooks/First%20Light.ipynb)**  LSST DESC Hack Day, February 2015.
* **[Initial design for the Twinkles pipeline](https://confluence.slac.stanford.edu/display/LSSTDESC/Twinkles+flow+chart)** LSST DESC Hack Day, February 2015.


### Read More

* **[Twinkles 1: Design and Specifications](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Requirements/)**

* **[Twinkles 1: Run 1 Plan](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Run1.md)**

Old Notes:
* [Scientific and Technical Motivation](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Motivation.md)
* [Survey Design](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Design.md)
* [Data Generation and Analysis: Pipeline Design](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Organisation.md)
* [Getting Set Up to Run Twinkles Simulations](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Setup.md)


### People

Check out our [contributions here](https://github.com/DarkEnergyScienceCollaboration/Twinkles/graphs/contributors)!

* Rahul Biswas (UW,
[@rbiswas4](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3Arbiswas4))
* Jim Chiang (SLAC,
[@jchiang87](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3Ajchiang87))
* Scott Daniel (UW,
[@danielsf](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3Adanielsf))
* Seth Digel (SLAC)
* Richard Dubois (SLAC,
[@richardxdubois](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3Arichardxdubois))
* Tom Glanzman (SLAC,
[@TomGlanzman](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3ATomGlanzman))
* Tony Johnson (SLAC,
[@tony-johnson](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3Atony-johnson))
* Bryce Kalmbach (UW,
[@jbkalmbach](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3Ajbkalmbach))
* Heather Kelly (SLAC, [@heather999](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3Aheather999))
* Simon Krughoff (UW,
[@SimonKrughoff](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3ASimonKrughoff))
* Phil Marshall (SLAC,
[@drphilmarshall](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3Adrphilmarshall))
* Curtis McCully (LCOGT)
* Saba Sehrish (Fermilab)
* Michael Wood-Vasey (Pitt,
[@wmwv](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues?q=assignee%3Awmwv)


### Credits etc

This is work in progress. If you would like to cite the Twinkles project in your research, please use '(LSST DESC, in prep.)' for now, and provide the [URL of this repository](https://github.com/DarkEnergyScienceCollaboration/Twinkles). We aim to release our data products along with a companion paper during the DESC DC1 era, 2016. If you are interested in this project, feel free to post greetings, comments or queries to the [issues](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues).  

All content is Copyright 2015, 2016 the above authors, and distributed under the MIT License, which means you can do whatever you like with it but agree not to blame us - but we'd prefer it if you kept in touch while you did so!
