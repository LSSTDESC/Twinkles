# Twinkles 1 Progress Report, June 2016

https://github.com/DarkEnergyScienceCollaboration/Twinkles

## 1. Background

The goals of the Twinkles project are to:
 * Implement, test and validate data analysis algorithms for:
   - Lensed quasar de-blending and light curve extraction
   - Extracting supernova light curves in the presence of extended host galaxy sources
   - Lensed quasar time delay measurement
 * Build expertise, connections, and mock datasets:
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
       - phoSim: install v3.4.2 at SLAC; develop workflow engine for running at SLAC; produce ~1200 simulated visits
       - Create a table holding SN with reasonable distribution of parameters except the rate which was made high enough to get ~100 of SNIa with SNR >5 per image for a patch of sky that should have included the Twinkles area
       - Lensed Quasars
         - Simulated lensed quasar systems “sprinkled” into PhoSim instance catalogs at positions of distant AGN-hosting galaxies
         - Variability and time delays are present in "sprinkled" systems
       - Make a selection of the DDF observations in Kraken to enable a coverage of 10 years with about 1000 observations. This was necessary as we wanted to limit the number of visits in run1 (scale of work), and the usual DDF cadence would exhaust this limit in a span of time too short to give us coverage of long lived transients
       - Put together code for creating phosim instance catalogs with the entire list of astophysical objects  including the SN described above, lensed quasars, stars galaxies, variable stars, solar system objects.
       - Analysis/processing of results *Jim*
         - MySQL database at NERSC filled with Level 2 results; a Qserv instance at SLAC is in progress
         - Comparison of Level 2 SNe light curves with CatSim inputs.

   * Run 1.1 *Tony Johnson*

   * Run 2  *Tony Johnson*

   * SN/SLMonitor Development *Bryce Kalmbach*
      - Developed code to extract flux/error data from Pserv database at NERSC, and display light curves
      - Currently developing code to display reference light curves as well

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
