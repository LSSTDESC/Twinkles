## Recipe: Emulating the DM Level 2 Pipeline

_Simon Krughoff_

This recipe is intended to show an example of how to process simulated image
data, as if we were running the LSST DM Level 2 "annual release processing".
The products will be catalogs of sources, objects etc.

## Build the indexes for astrometric and photometric calibration

We use the `phoSim` reference catalogs to emulate the kind of high accuracy
calibration that we expect to be possible with the LSST data. This is an
approximation, but for many purposes a good one. 

Currently the reference catalogs need to be formatted as astrometry.net index files.  I can convert the
reference catalog produced by `generatePhosimInput.py`, but there are a couple of precursor steps.  First,
there is a bug in how phosim creates the nominal WCS (PHOSIM-18).  The result is that the WCS claims to be
ICRS but ignores precession.  Since the matching algorithms assume we know approximately where the telescope
is pointing, they fail unless the catalogs are fixed.

It is easier to hack the reference catalog than to fix every WCS in every image, so I just correct for the approximate
precession and it gets close enough that the matching algorithms fail (the WCS will still be wrong, but we don't really
care since we aren't comparing to external catalogs).

```
$> awk '{printf("%i, %f, %f, %f, %f, %f, %i, %i\n", $1, $2-0.0608766, $3-0.0220287, $4, $5,$6,$7,$8)}' twinkles_ref.txt >twinkles_ref_obs.txt
```
The first few lines look like this:
```
#uniqueId, raJ2000, decJ2000, lsst_g, lsst_r, lsst_i, starnotgal, isvariable
992887068676, 52.989609, -27.381822, 26.000570, 24.490695, 22.338254, 1, 0
1605702564868, 53.002656, -27.356515, 27.732406, 26.371370, 25.372229, 1, 0
1277139994628, 52.991627, -27.362006, 24.948391, 23.598418, 22.391097, 1, 0
1704223204356, 53.017637, -27.326836, 23.914298, 22.938313, 22.539221, 1, 0
1605697082372, 53.017005, -27.333503, 21.839375, 21.498586, 21.378259, 1, 0
1605694183428, 52.988539, -27.326388, 25.324673, 24.003677, 23.221476, 1, 0
1605694345220, 52.992405, -27.326471, 19.366450, 18.940676, 18.774756, 1, 0
1277138139140, 52.994290, -27.333325, 24.185304, 22.843333, 21.513559, 1, 0
1605701058564, 53.008024, -27.350062, 21.925079, 21.523769, 21.378805, 1, 0
```
Now we translate the text file into a FITS file for indexing. I decided to change the column names from the default output by CatSim.
Then you can do the actual index generation.  You'll need to set up a couple of packages then run some scripts to do the formatting.
```
$> setup astrometry_net
$> setup pyfits
$> text2fits.py -H 'id, ra, dec, g, r, i, starnotgal, isvariable' -s ', ' twinkles_ref_obs.txt twinkles_ref.fits -f 'kdddddjj'
$> export P=0106160
$> build-astrometry-index -i twinkles_ref.fits -o index-${P}00.fits -I ${P}00 -P 0 -S r -n 100 -L 20 -E -j 0.4 -r 1 > build-00.log
$> build-astrometry-index -1 index-${P}00.fits -o index-${P}01.fits -I ${P}01 -P 1 -S r -L 20 -E -M -j 0.4 > build-01.log &
$> build-astrometry-index -1 index-${P}00.fits -o index-${P}02.fits -I ${P}02 -P 2 -S r -L 20 -E -M -j 0.4 > build-02.log &
$> build-astrometry-index -1 index-${P}00.fits -o index-${P}03.fits -I ${P}03 -P 3 -S r -L 20 -E -M -j 0.4 > build-03.log &
$> build-astrometry-index -1 index-${P}00.fits -o index-${P}04.fits -I ${P}04 -P 4 -S r -L 20 -E -M -j 0.4 > build-04.log
$> mkdir and_files
$> mv index*.fits and_files
$> cd and_files
```
The matcher needs to know which index files are available and what columns to use for photometric calibration.  These are specified using a configuration file.  This file goes in the `and_files` directory.  It is called `andConfig.py` and looks like this:
```
root.starGalaxyColumn = "starnotgal"
root.variableColumn = "isvariable"
filters = ('u', 'g', 'r', 'i', 'z', 'y')
root.magColumnMap = {'u':'g', 'g':'g', 'r':'r', 'i':'i', 'z':'i', 'y':'i'}
root.indexFiles = ['index-010616000.fits',
'index-010616001.fits',
'index-010616002.fits',
'index-010616003.fits',
'index-010616004.fits']
```

### Set up the data to run DM processing

First you'll need to build the stack using tickets/DM-4302 of obs_lsstSim.  In order to patch a branch version onto a pre-existing stack you can do something like the following.

1. Build a master stack.  I suggest using [lsstsw](https://confluence.lsstcorp.org/display/LDMDG/The+LSST+Software+Build+Tool).
2. Set up the stack: e.g. `$> setup obs_lsstSim -t bNNNN`
3. Clone the package you want to patch on top of your stack `$> clone git@github.com:lsst/obs_lsstSim.git; cd obs_lsstSim`
4. Get the branch: `$> checkout tickets/DM-4302`
5. Set up just (-j) the cloned package (since the rest of the packages are already set up): `$> setup -j -r .`
6. Build the cloned package (this is necessary even for pure python packages): `$> scons opt=3`
7. Optionally install it in your stack: `$> scons install declare`

This assumes the simulated images have landed in a directory called ```images```
in the current directory.  In the images directory, you'll need a ```_mapper``` file with contents
```
lsst.obs.lsstSim.LsstSimMapper
```
The above file will tell the stack where to put the raw files and eimages.
```
# Setup the stack environment.  This will make the LsstSimMapper class available
$> setup obs_lsstSim

# Ingest the images from a directory called images to a repository called input_data
# there are some config overrides in the ingest.py file
$> ingestImages.py images images/lsst_*.fits.gz --mode link --output input_data
```
Now you are setup to process the data

### Process the data using the DM stack

Start here if you just want to exercise the DM stack.  If you didn't follow the steps above, first get the data and astrometry.net index files from
[here](https://lsst-web.ncsa.illinois.edu/~krughoff/data/gri_data.tar.gz).  Then untar the tarball in a working directory.

After you have the data, you can start following the steps below to get forced photometry in three bands.
```
# Setup the reference catalog for photometric and astrometric calibration
$> setup -m none -r and_files astrometry_net_data

# Create calibrated images from the input eimages.  This will write to a repository called output_data.  The --id argument
# defines the data to operate on.  In this case it means process all data (in this example the g, r, and i bands) with visit numbers between
# 840 and 879.  Mising data will be skipped
$> processEimage.py input_data/ --id visit=840..879 --output output_data

# Make a skyMap to use as the basis for the astrometic system for the coadds.  This can't be done up front because
# makeDiscreteSkyMap decides how to build the patches and tracts for the skyMap based on the data.
$> makeDiscreteSkyMap.py output_data/ --id visit=840..879 --output output_data

# Coadds are done in two steps.  Step one is to warp the data to a common astrometric system.  The following does that.
# The config option is to use background subtracted exposures as inputs.  You can also specify visits using the ^ operator meaning
# 'and'.
$> makeCoaddTempExp.py output_data/ --selectId visit=840..849 --id filter=r patch=0,0 tract=0 --config bgSubtracted=True --output output_data
$> makeCoaddTempExp.py output_data/ --selectId visit=860..869 --id filter=g patch=0,0 tract=0 --config bgSubtracted=True --output output_data
$> makeCoaddTempExp.py output_data/ --selectId visit=870..879 --id filter=i patch=0,0 tract=0 --config bgSubtracted=True --output output_data

# This is the second step which actually coadds the warped images.  The doInterp config option is required if there
# are any NaNs in the image (which there will be for this set since the images do not cover the whole patch).
$> assembleCoadd.py output_data/ --selectId visit=840..849 --id filter=r patch=0,0 tract=0 --config doInterp=True --output output_data
$> assembleCoadd.py output_data/ --selectId visit=860..869 --id filter=g patch=0,0 tract=0 --config doInterp=True --output output_data
$> assembleCoadd.py output_data/ --selectId visit=870..879 --id filter=i patch=0,0 tract=0 --config doInterp=True --output output_data

# Detect sources in the coadd and then merge detections from multiple bands.
$> detectCoaddSources.py output_data/ --id tract=0 patch=0,0 filter=g^r^i --output output_data
$> mergeCoaddDetections.py output_data/ --id tract=0 patch=0,0 filter=g^r^i --output output_data

# Do measurement on the sources detected in the above steps and merge the measurements from multiple bands.
$> measureCoaddSources.py output_data/ --id tract=0 patch=0,0 filter=g^r^i --config measurement.doApplyApCorr=yes --output output_data
$> mergeCoaddMeasurements.py output_data/ --id tract=0 patch=0,0 filter=g^r^i --output output_data

# Use the detections from the coadd to do forced photometry on all the single frame data.
$> forcedPhotCcd.py output_data/ --id tract=0 visit=840..879 sensor=1,1 raft=2,2 --config measurement.doApplyApCorr=yes --output output_data
```
Once the forced photometry is done, you can look at the output by loading the measurements using the butler.  [This script](../../bin/plot_point_mags.py) shows how to start looking at the measurements.  It produces the following image.  I tried to fit both the systematic floor and the 5sigma value for each of the bands.  Results are shown in the legend of the following image.

![Repeat figure](gri_err.png)

You can also use the stack to make a color image from the three coadds.  See [colorim.py](../../bin/colorim.py) for the code to do this.  Note that you can also overplot the detections.

[![Coadd thumbnail](rgb_coadd_thumb.png)](rgb_coadd.png)
