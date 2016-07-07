# Lessons learned from Run 1

* **Getting all the astrometry right is hard.**  There are differential effects we want to simulate with catsim so things move around correctly.  Unfortunately, we found that bulk precession ended up in the WCS produced by phosim which made our reference catalogs useless.
* **Enabling data access is important.** It took me a while to figure out how to get to the data in a place where I could look at it.  This was mostly just figuring out which machine to use and paths to the data and stack.  Maybe Tony's concept of a portal will help this.
* **Epics are really useful for managing large numbers of issues. We now have most of our issues organized into epics, and a labeling system that allows 1) only the epics themselves to be shown in a high-level view, and 2) all issues in a particular epic to be focused on - both by using issue filtering.
