# Lessons Learned

## Run 1 and 1.1:

* **Getting all the astrometry right is hard.**  There are differential effects we want to simulate with catsim so things move around correctly.  Unfortunately, we found that bulk precession ended up in the WCS produced by phosim which made our reference catalogs useless. (Simon)
* **Enabling data access is important.** It took me a while to figure out how to get to the data in a place where I could look at it.  This was mostly just figuring out which machine to use and paths to the data and stack.  Maybe Tony's concept of a portal will help this. (Simon)
* **Epics are really useful** for managing large numbers of GitHub issues. We now have most of our issues organized into epics, and a labeling system that allows 1) only the epics themselves to be shown in a high-level view, and 2) all issues in a particular epic to be focused on - both by using issue filtering. (Phil)
* **Conda installation of the DM Stack can be carried out by Travis CI** allowing us to use this service. (Phil)
* **Using both the LSST sims tools and the DM stack in the same project was surprisingly difficult.** Hopefully this will improve as a result of our trying to do it! (Phil)
* **We are already close to the edge of what the DM Stack can do,** and as a result, discussing how to emulate the forced photometry of DIAObjects, for example. Are we about to become Stack developers? (Phil)
* **The CPU time required to simulate a 30-s visit in Phosim ranges over two orders of magnitude,** depending mostly on the brightness of the sky, which depends mostly on whether the moon is up.  The overall time required is dominated by these visits, and in fact 103 of the 1227 Run 1 simulations reached the 120-hour batch farm limit at SLAC, and so did not finish.  This has implications for scheduling and running simulations at NERSC, where the CPU time limits per job are less, and suggests that checkpointing may be needed in the workflow. (Seth)


## Run 2:

* **At NERSC, it matters a lot for throughput where the software is installed.** (Tony)
* **We need to stay on top of the DMstack (apps and sims) development** both in terms of determining the versions to install but also to sort out problems as they are encountered. This is best done either through [community.lsst.org](http://community.lsst.org) or via GitHub issues (Heather)
* **Conda installs of DMstack are great, but may not aways be available** In that case, brush up on your use of [lsstsw](https://developer.lsst.io/build-ci/lsstsw.html). (Heather)
