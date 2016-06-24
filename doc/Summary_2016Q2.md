# Twinkles 1 Progress Report, June 2016

https://github.com/DarkEnergyScienceCollaboration/Twinkles

## 1. Background

The goals of the Twinkles project are to:
 * Implement, test and validate data analysis algorithms for:
   - Lensed quasar de-blending and light curve extraction
   - Extracting supernova light curves in the presence of extended host galaxy sources
   - Lensed quasar time delay measurement
 * Serve as a *pathfinder* for the DESC data challenges, enabling the collaboration to gain expertise, connections, and capabilities in generating, processing and analyzing mock datasets:
   - Develop DESC computing group expertise in operating CatSim, PhoSim, and the DM stack at scale, at either NERSC or SLAC or both.
   - Improve the connections between DESC and the LSST Simulations and DM groups.
   - Provide a testing ground for (at least) the following DM Level 2 algorithms:
     * The Deblender
     * Image Differencing
     * MultiFit
   - Support the development of:
     * "SuperFit" algorithms, built against the MultiFit API to handle time-variable point sources and mixed point source / extended source models for optimal light curve extraction. Initializing and constraining them from upstream catalog quantities (such as DIASource detections) will be important.
     * Many other measurements.


## 2. People

Based on major contributions to date, the Twinkles Task Force has emerged as
consisting of the following working group members:
   * Strong Lensing: Phil Marshall
   * Supernovae: Michael Wood-Vasey, Rahul Biswas
   * Survey Simulations: Bryce Kalmbach, Scott Daniel, Simon Krughoff
   * Computing Infrastructure: Jim Chiang, Seth Digel, Richard Dubois, Tom Glanzman, Tony Johnson, Heather Kelly, Brian Van Klaveren

Minor contributions have also been made by Curtis McCully,
Dominique Fouchez and Fabrice Feinstein.

## 3. Progress

   * Twinkles 1 specifications  *Phil Marshall*

      - In the Science Roadmap we defined two phases, Twinkles 1 (DC1) and Twinkles 2 (DC2), distinguished by a) scope and b) realism. Twinkles 1 was supposed to be single filter, and simple enough to get started. Twinkles 2 was supposed to be multi-filter, and as realistic as we could make it.
      - During early Twinkles 1 R&D work (2016Q1) we determined that generating and processing multi-filter data was not actually very difficult, and so we changed the definition of Twinkles 1 to include multi-filter data. The only difference between Twinkles 1 and Twinkles 2 will therefore be in the realism of the data generated and the processing applied to it.
      - We adopted a staged strategy to building up our simulation and processing capabilities, envisioning at least one small test run prior to the full DG phase (2016 Q3 onwards). The first of these test runs was named "Run 1" and scoped to include ~1000 visits in all filters, covering all ten years at WDF-like cadence (although the actual time sampling was chosen to be a down-sample of the DDF observations, for simplicity).

   * Run 1  *Tony Johnson, Tom Glanzman, Rahul Biswas*

     PhoSim image simulation:
       - For the inputs to these images, we:
         - Created a table of SNe with a reasonable distribution of parameters, but with rate (abundance) high enough to yield ~100 SNIa with SNR >5 per image for the Twinkles sky patch.
         - Simulated lensed quasar systems based on the OM10 catalog, and “sprinkled” them into the PhoSim instance catalogs at the correct positions around distant lens-type galaxies, and ensured implemented correct time variability and time delays between the multiple images
       - We selected a subset of the DDF observations in the Kraken OpSim output database to enable a coverage of 10 years with about 1000 observations. This was necessary as we wanted to limit the number of visits in Run 1 (to keep this test manageable), while giving us sufficient time coverage of long lived variables (10 years).
       - We assembled code for creating PhoSim instance catalogs with the complete list of astophysical objects,  including the SNe and lensed quasars described above, as well as stars galaxies, variable stars, and solar system objects.
       - We installed PhoSim v3.4.2 at SLAC,  developed a workflow engine for running at SLAC, and used it to produce ~1200 simulated visit (emulated-calibrated "eimage") images.
       - We identified an issue of queue expiration for high sky background images, that require greater run time than the batch system will allow.

    DM Level 2 Processing of results *Tony Johnson, Simon Krughoff, Jim Chiang*
       - We designed a simple DM Level 2 pipeline as a "Cookbook" document, and
       implemented the steps as a set of Stack command-line tasks called from the SLAC workflow engine.
       The data products of this pipeline are co-added images, calibrated exposures, coadd sources, and
       forced photometry flux measurements of each coadd source.
       - This pipeline was run at SLAC, and the products copied to NERSC for access by the group. Several issues were identified with the batch processing, including high memory demand for the coaddition task.
       - The Level 2 catalog outputs were ingested into a MySQL database at NERSC to enable the SN and SL analyses.
       - Implementation of the standard DM stack validation pipeline has begun using the DM team's [validate_drp](https://github.com/lsst/validate_drp) package.
       - We compared DM Level 2 ForcedSource SNe light curves with CatSim inputs, finding good agreement in filters *grizy* for isolated supernovae with faint hosts. We see signs of blending problems in other systems, and found a systematic error in the *u*-band flux calibration which is under investigation.

    Computing Infrastucture Pathfinding *Jim Chiang, Rahul Biswas, Phil Marshall, Brian van Klaveren*
       - Since the bulk of DESC science analyses will be performed at the catalog level, we implemented a MySQL database that uses the published baseline schema for the Qserv tables. That MySQL database was implemented at NERSC using the [pserv](https://github.com/DarkEnergyScienceCollaboration/pserv) package, and it enables us to write code using the same queries that are anticipated to be used for the production tables.
       - In order to exercise Qserv itself, we are working with the Qserv developers at SLAC to implement a small Qserv database to serve up the larger Twinkles 2 dataset.
       - We've converged on a standard repository structure that enables:
         - package and dependency management using eups,
         - building and running code against the LSST Stack,
         - automated builds and testing using the Travis-CI continuous integration service.
         A [cookiecutter template package](https://github.com/DarkEnergyScienceCollaboration/desc_package_template) was developed to generate new repositories that have the necessary boilerplate configurations in place to use these services.

   * Run 1.1 *Tony Johnson*
   
       - Analysis of the run 1 results identified some small bugs in the DM code, which were reported and fixed, and some areas where the parallelization of the workflow had been performed incorrectly. These errors were fixed and the DM workflow rerun resulting in a run 1.1 dataset, which was again copied to NERSC and imported into the PServ database for analysis.

   * Run 2  *Tony Johnson*
   
       - The main goal of run 2 is to rerun the Run 1.1 DM level 2 workflow at NERSC, with the aim of identifying and solving any issues which would make running the full DC1 simulation and analysis at NERSC in the fall.
       - An "job control" daemon for the SLAC workflow agent was developed able to submit jobs to the NERSC slurm batch system.
       - A number of initial issuess with efficiently using NERSC have been identified and reported to the CI group. Work is currently underway to understand and solve these issues, with help from NERSC and DM experts. Uopdated results are expected to be available by the time of the Oxford collaboration meeting.

   * SN/SLMonitor Development *Bryce Kalmbach*
      - We developed code to extract flux/error data from the MySQL database at NERSC, and display light curves.
      - We are currently developing code to display reference light curves and postage stamp images as well.


## 4. Plans through September 2016

The 12 month Taskforce period expires at the end of calendar Q3, 2016. While
some  processing time will be lost to scheduled Cori-I downtime, we aim to have
completed the PhoSim image simulation for the main Twinkles 1 data generation
run by the end of September, and have  started to run DM Level 2 tasks at
NERSC. Approximate timeline:

   * July 2016: present Twinkles progress to date to the collaboration in an "Open House" session, designed to show both the data and code we have produced so far, and transmit the lessons we have learned.
   * July 2016: finalize the specifications for Twinkles 1, based on the experience through the R&D phase of CY16 Q1-Q2.
   * August 2016: implement the required CatSim, OpSim, Sprinkler, and PhoSim settings and produce 10,000 visit eimages with PhoSim, either at SLAC or at NERSC.
   * September 2016: finish PhoSim runs, and document choices in the paper. Complete implementation of DM Level 2 pipeline (including image differencing) and begin processing, at NERSC.
   * October 2016: complete DM Level 2 processing and document choices in the paper. Begin science analysis of SL and SN objects.
   * November 2016: iterate on DM Level 2 processing if necessary. Complete science analysis.
   * December 2016: finish paper.


## 5. Finances

The first and only significant financial expenditure planned is for October
2016, to provide lodging in Half Moon Bay for a Twinkles retreat. The proposal
for this activity can be viewed
[here](https://docs.google.com/document/d/1Yc0rTsgkGteFFJ-Z5crR77iBQJHH4zgmXmgWwS1Dkgo/edit?pli=1#).
In short, we are proposing a 6-night off-site residential retreat, all Task
Force members to work closely together on digesting, analyzing and documenting
the Twinkles 1 data and code, with the goal of producing a paper for the
Astronomical Journal Supplement (or similar). We have a quote for $3,687.23 for
6 nights ($123 per person per night), and are working with SLAC administrative
and legal staff to make this booking. Other expenses (travel, M&IE) will be
covered from Task Force members own research funds; the location will be in the
Bay Area to minimize travel costs, and only the UW and Pittsburgh team members
will need accommodation.
