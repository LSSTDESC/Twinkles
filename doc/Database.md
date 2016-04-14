# Twinkles Database Plan

Our Level 2 pipeline produces several catalogs of objects and sources, from which we need to extract light curves. These catalogs need to be stored as database tables. Below we list our requirements for each phase of the Twinkles 1 project. The timeline for the Twinkles project can be viewed [here](https://github.com/DarkEnergyScienceCollaboration/Twinkles/milestones).

## Run 1.1

Light curve analysis is due to start on **April 22** (the Run 1.1 data release).

We need:
* A database that can hold approximately 50-100M records.
* To get this set up within the next week.
* The data to be accessible by people at UW, potentially via them setting up their own instance.

Proposed solution:
* MySQL tables set up by homegrown script.
* Independent instances at SLAC and UW, built locally.
* A NERSC instance is also possible on this time scale.

## Run 2

Light curve analysis is due to start on **May 20** (the Run 2 data release).

We need:
* A *single* database that can hold approximately 100M records.
* The data to be accessible by everyone.

Proposed solution:
* MySQL tables set up by homegrown script.
* One instance, at NERSC.


# Twinkles 1

Light curve analysis is due to start on **September 30** (the Twinkles 1 data release).

We need:
* A *single* database that can hold approximately 3G records.
* The data to be accessible by everyone.

Proposed solution:
* Qserv tables set up by Qserv ingest scripts.
* One instance, at XXX.

