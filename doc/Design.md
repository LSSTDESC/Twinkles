 
# Survey Design

This document represents our current thinking about the Twinkles survey design, and will evolve with time.

The Twinkles philosophy is to make the simulated data *as realistic as possible,* and then deal with the data analysis consequences. This places the emphasis on survey readiness, an issue which will become progressively more urgent as time goes on. In this model, the identification of systematic effects has to be teased out from the complex data, which will be more difficult than if we were to work with more simplified, "controlled test" simulations. However, realistic complexity prevents us from having to draw qualified conclusions. In any case, simplified versions of the Twinkles field can always be generated after the fact.

## Basics

* A 10 year survey with realistic extragalactic deep drilling field cadence, but with the observations flagged so that N realistic wide-deep-fast main survey data subsets can be extracted. We will use `OpSim 3.61` outputs for the observing schedule, with additional realistic dithering and field rotation.

* Small sky area, overloaded with supernovae and lensed quasars. These need to be sufficiently well-separated to avoid implausible cross-talk. The number of objects required by the validation will drive the survey area given this separation. Initial estimates were that a 10 arcminute square sky patch would be sufficient.

* Realistic stars should be present, to enable PSF modeling, photometric calibration and verification etc. This means choosing a moderate Galactic latitude sky patch.

* A real sky patch, from the CFHTLS Deep field, could complement the Twinkles survey by providing real stars and galaxies for comparison. LSST DM stack reprocessing of CFHTLS is underway, led by DESC members at IN2P3.

## Details

### Pointing, Field Size etc 

Let's choose a field from one of the [extragalactic deep drilling fields](http://www.lsst.org/News/enews/deep-drilling-201202.html) in `OpSim 3.61`. Here's the
Extended Chandra Deep Field South:

* (RA, Dec) = (03:32:30, 10:00:24)
* (l,b) = (224.07, -54.47)

A sensible unit of area could be a single chip. With dithers, field rotation etc the actual area surveyed to full depth would be a circle with diameter a bit less than a chip width. 

### Contents

We are sprinkling interesting features onto existing `CatSim` objects. Galaxies can either have supernovae or AGN added, and in half the cases, a massive lens galaxy placed in front of them. All inserted objects need to have plausible properties: this is taken care of by the `sprinkler` code. Stars will also be present, which should help with some tests, and basic PSF modeling.

#### Supernovae

#### Lensed Quasars

