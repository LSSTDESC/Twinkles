
# Scientific and Technical Motivation

Type Ia supernovae and time delay lenses have a lot in common. They are both
complex objects that need to be detected in catalog space (using the outputs
of the DM stack deblender, object aggregator, and MultiFit) and classified in
pixel space (either in a "SuperFit", or some other level 3 tool). Light curves must be extracted for both, so that time domain model parameters (stretch, time delay) can be inferred. These commonalities suggest that the development of the software instrumentation needed to detect and measure both types of system can be carried out using the same test dataset, the Twinkles survey.

Moreover, the production of the Twinkles images, and their "standard" pipeline processing using the LSST DM stack, can be used to drive the development of several aspects of DESC computing infrastructure.

In this document we detail both the scientific and technical justification for the proposed Twinkles project.


## Science Justification

We need to implement, test and validate algorithms for:

* Selecting lensed quasar targets from catalogued deblender outputs

* Extracting supernova light curves in the presence of their host galaxies' light

* Extracting multiply-imaged AGN light curves in the presence of both their host galaxy's and the lens galaxy's light

* Measuring lensed quasar time delays from the realistic correlated multi-filter lightcurves


Any dataset that enables the above would also, naturally, enable testing of algorithms for:

 * Lens modeling using LSST pixel data, using both the multiply-imaged AGN images and their host galaxy Einstein Rings
 
 * Measuring faint galaxy shapes, if such objects are also included
 
 * Many other measurements.



## Technical Justification

The construction of a Twinkles image anad catalog mock dataset will involve:

* Building DESC computing group expertise in operating CatSim, PhoSim, and the DM stack at scale, at either NERSC or SLAC or both.
* Improving the connections between DESC and the LSST Simulations and DM groups.

The Twinkles dataset will be a valuable testing ground for (at least) the following DM level 2 algorithms:

* The Deblender
* Image Differencing
* MultiFit

It will support the development of:

* "SuperFit" algorithms, built against the MultiFit API to handle time-variable point sources and mixed point source / extended source models for optimal light curve extraction. Initializing and constraining them from upstream catalog quantities (such as DIASource detections) will be important.

