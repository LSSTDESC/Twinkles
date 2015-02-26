# Run 1

The simplest possible Twinkles simulation, that contains the features we care about. 
Initial design chosen for speed of implementation.

## Pointing, Field Size etc 

Let's choose a field from one of the [extragalactic deep drilling fields](http://www.lsst.org/News/enews/deep-drilling-201202.html) in `OpSim 3.61`. Here's the
Extended Chandra Deep Field South:

* (RA, Dec) = (03:32:30, 10:00:24)
* (l,b) = (224.07, -54.47)

A sensible unit of area could be a single chip. With dithers, field rotation etc the actual area surveyed to full depth would be a circle with diameter a bit less than a chip width. 

## Contents

We are sprinkling interesting features onto existing `CatSim` objects. Galaxies can either have supernovae or AGN added, and in half the cases, a massive lens galaxy placed in front of them. All inserted objects need to have plausible properties: this is taken care of by the `sprinkler` code. Stars will also be present, which should help with some tests, and basic PSF modeling.


### Supernovae

### Lensed Quasars

