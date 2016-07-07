# Lessons learned from Run 1

* **Getting all the astrometry right is hard.**  There are differential effects we want to simulate with catsim so things move around correctly.  Unfortunately, we found that bulk precession ended up in the WCS produced by phosim which made our reference catalogs useless. (Simon)
* **Enabling data access is important.** It took me a while to figure out how to get to the data in a place where I could look at it.  This was mostly just figuring out which machine to use and paths to the data and stack.  Maybe Tony's concept of a portal will help this. (Simon)
* **Epics are really useful** for managing large numbers of GitHub issues. We now have most of our issues organized into epics, and a labeling system that allows 1) only the epics themselves to be shown in a high-level view, and 2) all issues in a particular epic to be focused on - both by using issue filtering. (Phil)
* **Conda installation of the DM Stack can be carried out by Travis CI** allowing us to use this service. (Phil)
* **Using both the LSST sims tools and the DM stack in the same project was surprisingly difficult.** Hopefully this will improve as a result of our trying to do it! (Phil)
* **We are already close to the edge of what the DM Stack can do,** and as a result, discussing how to emulate the forced photometry of DIAObjects, for example. Are we about to become Stack developers? (Phil)
