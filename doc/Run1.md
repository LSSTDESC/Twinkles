# <a name="Run1"></a> Run 1

The simplest possible Twinkles simulation, that contains the features we care about. 
Initial design chosen for speed of implementation.

**Table of Contents**:
* [Observations](#Observations)
* [Astronomical Objects](#AstronomicalObjects)
  * [Lensed Quasars](#LensedQuasars)
  * [Supernovae](#Supernovae)
* [Pipeline Processing](#Pipeline)
* [Products](#Products)
  * [Images](#Images)
  * [Measurements and Tests](#Measurements)
_____

## <a name="Observations"></a> Observations

Let's choose a field from one of the [extragalactic deep drilling fields](http://www.lsst.org/News/enews/deep-drilling-201202.html) in `OpSim 3.61`. Here's the
Extended Chandra Deep Field South:

* (RA, Dec) = (03:32:30, 10:00:24)
* (l,b) = (224.07, -54.47)

A sensible unit of area could be a *single chip.* With dithers, field rotation etc the actual area surveyed to full depth would be a circle with diameter a bit less than a chip width. 

Dithers should be small, just enough to cover chip gaps (~10 arcsec?). If we keep simulating a single sensor at the center of the field, we can avoid the problems associated with field distortion etc, while still including field rotation (we hope straightforwardly). 

Observing strategy to be extracted from `OpSim 3.61` as above. How many images? Build up in stages?


## <a name="AstronomicalObjects"></a> Astronomical Objects

We are sprinkling interesting features onto existing `CatSim` objects. Galaxies can either have supernovae or AGN added, and in half the cases, a massive lens galaxy placed in front of them. All inserted objects need to have plausible properties: this is taken care of by the `sprinkler` code. Stars will also be present, which should help with some tests, and basic PSF modeling.

#### <a name="Lensed Quasars"></a> Lensed Quasars

These are simply taken from the OM10 catalog, as in [issue #21](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues/21), by the `sprinkler` code. For each galaxy in a `CatSim` catalog, we search the OM10 catalog for all sources within +/-0.05 in redshift from the `CatSim` source. If there aren't any OM10 lensed sources at this redshift, we move on the next object. Otherwise, we randomly choose one of the lens systems. Then, we remove the `CatSim` object from the catalog and instead add lensed images, with appropriately magnified source brightness, and finally add a model lens galaxy to the catalog. Not all the galaxies are placed behind lenses in this way - we stop after reaching a certain number, perhaps 100.


#### <a name="Supernovae"></a> Supernovae


## <a name="Pipeline"></a> Pipeline Processing

* Simplest possible pipeline: simple script?
* Simplest location for simulating data and running DM stack: SLAC? NERSC?
* Simplest way to analyze outputs?

## <a name="Products"></a> Products

#### <a name="Images"></a> Images

We will only make `eimages`, and treat them as emulated calibrated images. This will allow us to go straight to testing the DM *measurement algorithms* (as opposed to the image reduction ones).

#### <a name="Measurements"></a> Measurements and Tests

* Deblended objects. Can we see lensed quasar targets in the object catalog?
* Difference image sources. Can we see lensed quasar targets in the diffsource catalog?
* Forced photometry lightcurves. How good are the preliminary lightcurves?


[Back to the top.](#Run1)
