# Run 1

The simplest possible Twinkles simulation, that contains the features we care about. 
Initial design chosen for speed of implementation.

## Observations 

Let's choose a field from one of the [extragalactic deep drilling fields](http://www.lsst.org/News/enews/deep-drilling-201202.html) in `OpSim 3.61`. Here's the
Extended Chandra Deep Field South:

* (RA, Dec) = (03:32:30, 10:00:24)
* (l,b) = (224.07, -54.47)

A sensible unit of area could be a *single chip.* With dithers, field rotation etc the actual area surveyed to full depth would be a circle with diameter a bit less than a chip width. 

Dithers should be small, just enough to cover chip gaps (~10 arcsec?). If we keep simulating a single sensor at the center of the field, we can avoid the problems associated with field distortion etc, while still including field rotation (we hope straightforwardly). 

Observing strategy to be extracted from `OpSim 3.61` as above. 

## Contents

We are sprinkling interesting features onto existing `CatSim` objects. Galaxies can either have supernovae or AGN added, and in half the cases, a massive lens galaxy placed in front of them. All inserted objects need to have plausible properties: this is taken care of by the `sprinkler` code. Stars will also be present, which should help with some tests, and basic PSF modeling.

### Lensed Quasars

These are simply taken from the OM10 catalog, as in [issue #21](https://github.com/DarkEnergyScienceCollaboration/Twinkles/issues/21), by the `sprinkler` code. For each galaxy in a `CatSim` catalog, we search the OM10 catalog for all sources within +/-0.05 in redshift from the `CatSim` source. If there aren't any OM10 lensed sources at this redshift, move on the next object. Otherwise, randomly choose one the lens systems. Then, we remove the `CatSim` object from the catalog and instead add lensed images, with appropriately magnified source brightness. Then we add a model lens galaxy to the catalog, and then pass the modified catalog to `PhoSim` to make images.

### Supernovae
