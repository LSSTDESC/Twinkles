 
# Survey Design

This document represents our current thinking about the Twinkles survey design, and will evolve with time.

The Twinkles philosophy is to make the simulated data *as realistic as possible,* and then deal with the data analysis consequences. This places the emphasis on survey readiness, an issue which will become progressively more urgent as time goes on. In this model, the identification of systematic effects has to be teased out from the complex data, which will be more difficult than if we were to work with more simplified, "controlled test" simulations. However, realistic complexity prevents us from having to draw qualified conclusions. In any case, simplified versions of the Twinkles field can always be generated after the fact.

## Basics

* A 10 year survey with realistic extragalactic deep drilling field cadence, but with the observations flagged so that N realistic wide-deep-fast main survey data subsets can be extracted. We will use `OpSim 3.61` outputs for the observing schedule, with additional realistic dithering and field rotation.

* Small sky area, overloaded with supernovae and lensed quasars. These need to be sufficiently well-separated to avoid implausible cross-talk. The number of objects required by the validation will drive the survey area given this separation. Initial estimates were that a 10 arcminute square sky patch would be sufficient.

* Realistic stars should be present, to enable PSF modeling, photometric calibration and verification etc. This means choosing a moderate Galactic latitude sky patch.  The chosen location is the Extended Chandra Deep Field South at:
RA: 03h 32m 30s Dec: -28d 06m 00s.  Part of the reason for this was that it corresponds to a deep drilling field in the current LSST survey design.

* A real sky patch, from the CFHTLS Deep field, could complement the Twinkles survey by providing real stars and galaxies for comparison. LSST DM stack reprocessing of CFHTLS is underway, led by DESC members at IN2P3.

## Individual Runs

Rome wasn't built in a day.

* **[Run 1](https://github.com/DarkEnergyScienceCollaboration/Twinkles/blob/master/doc/Run1.md)**: simplest possible implementation of the above basic features, with many corners cut to get started.
