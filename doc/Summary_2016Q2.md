# Summary as of 2016 June

https://github.com/DarkEnergyScienceCollaboration/Twinkles

1. Original goals
 * Implement, test and validate algorithms 
   - Lensed quasar deblending
   - Supernova light curves over extended sources
   - Multipy-imaged AGN lightcurves.
   - Measure lensed quasar time delays
 * Build expertise, connections, and mock datasets
   - Building DESC computing group expertise in operating CatSim, PhoSim, and the DM stack at scale, at either NERSC or SLAC or both.
   - Improving the connections between DESC and the LSST Simulations and DM groups.
   - Provide a testing ground for (at least) the following DM level 2 algorithms:
     * The Deblender
     * Image Differencing
     * MultiFit
    - It will support the development of:
     * "SuperFit" algorithms, built against the MultiFit API to handle time-variable point sources and mixed point source / extended source models for optimal light curve extraction. Initializing and constraining them from upstream catalog quantities (such as DIASource detections) will be important.
      - Many other measurements.
2. People and their WGs involved
   * Strong Lensing
   * Supernovae
   * Survey Simulations
3. Progress to date
   * Pre-Run1  *Tony/Tom*
   * Run 1  *Tony/Tom/Rahul*
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
   * Run 2  *Phil/Tony*
   * SN/SLMonitor
      - Developed code to extract lightcurve data from MYSQL database at NERSC and display lightcurves
      - Currently developing code to display reference lightcurves as well
4. Plans through September (the end of the 12 month Taskforce period).
   *Phil*

5. Finances
   The first significant financial expenditure planned is for October 2016 to provide lodging in Half Moon Bay for a Twinkles retreat.
