
# DESC Taskforce 2015 Proposal: Twinkles

| Title|Twinkles|
|----------|-------------------------|
| Primary Lead(s)                       | Marshall, Wood-Vasey, Dubois |                                  |---------------------------------------|--------------------------------------------------------------|
| Interested DESC Members               | Krughoff, Fassnacht, Jha, Dodelson, Walter, Peterson, Connolly, Glanzman, Digel, Sehrish, Johnson, McCully |
| DESC Working Groups                   | SN, SL, CI, SIMS                                              |---------------------------------------|--------------------------------------------------------------|
| Start Date (approximate)              | September 2015                                                     |---------------------------------------|--------------------------------------------------------------|
| End Date (approximate)                | December 2016                                                     |---------------------------------------|--------------------------------------------------------------|
| Working Deliverable Publication Title | Twinkles v1.0: Cosmological Light Curve Extraction in a Tiny Simulated LSST Imaging Survey |
| Intermediate Milestones               | Twinkles v1.0 Survey Requirements Document (Fall 2015); Twinkles v1.0 Pipeline (Summer 2016); Twinkles v1.0 Imaging Dataset (Summer 2016); Twinkles v1.0 Level 2 Catalog (Summer 2016) ; Twinkles v1.0 Validation Report (Fall 2016)                                                             |---------------------------------------|--------------------------------------------------------------|


### Why is this project a priority?

It addresses the following key technical issues:

* The Twinkles data release will stimulate and drive the development of level 3 and 4 DESC analysis software for: 1) finding strong lenses and supernovae, 2) extracting high accuracy light curves for strong lenses and supernovae, 3) modeling light curves (by providing fluxes with realistic, correlated, statistical and systematic uncertainties).

* The Twinkles simulation and end-to-end data simulation and reduction pipeline, assembled from component parts provided by the LSST project (CatSim, OpSim, GalSim, PhoSim, DM Stack), can serve as a pathfinder for the pipeline that DESC will need to run at much larger scale to provide collaboration wide simulated data at DC2 and DC3.

* Twinkles can also provide a test bed for the DESC computing infrastructure: we plan to develop and employ tools for managing large numbers of processing jobs and tracking the resulting data. It will also help drive and test various other aspects of the collaboration's software engineering capability, including its use of repositories, issues tracking, coding standards, build environment, and automated builds.

### Computing Resource Requirements

Because the sky area being considered is very small (~100 square arcmin) we expect to be able to generate the data on a number of small computing clusters available at several DESC institutions, including SLAC and Fermilab. The data storage requirements are also modest: a 100 square arcmin image is about 50Mb, and we expect the Twinkles 1.0 survey to comprise a few hundred visits, leading to **a storage requirement of just a few tens of Gb.** Each image will take a few CPU hours to simulate with PhoSim, and this will likely dominate the computing time. **A thousand CPU hours** will be needed for each iteration of the Twinkles 1.0 dataset: we can expect to need a few thousand in total. (The full Twinkles survey will be a few thousand visits in all six filters, so will still only need a few hundred Gb of storage, and 10,000 CPU hours to generate. Compared to the full LSST area, 100 square arcmin is about 2 microsurveys - so the storage requirements are O[100Gb] instead of O[100Pb].)

### Brief Project Summary

We are interested in making high accuracy cosmological measurements of type IA supernovae and strong gravitational lens time delays with the LSST data. To do this, we need to build a number of software instruments (for finding, monitoring and measuring time variable objects), and these must be tested and validated against realistic simulated data. We plan to use LSST project data simulation tools to generate a ten year, 6-filter set of mock images of a small patch of moderate Galactic latitude sky, containing an unrealistic overdensity of supernovae and lensed quasars but with realistic observing conditions and cadence, and process these images using the LSST DM Stack. The software pipeline we build to carry out this program can serve as a pathfinder for the end-to-end simulation system that the DESC will need to build its DC2 and DC3 challenge datasets.

The first Twinkles data release (Twinkles 1.0) will consist of a few hundred visit images, with filter set, cadence and campaign length driven by the requirements of the analysis groups' key project requirements, to be defined in Fall 2015. The v1.0 images will likely contain simplified objects, and may have less realistic observing conditions than in v2.0, depending on the rate of technology development.
