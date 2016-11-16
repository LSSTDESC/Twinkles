# Recipe: How to create `DIASources` using PSF Homogenized coadds

The basic sequence of operations is as follows:

* Produce calibrated exposures
* Produce the skyMap
* Generate a PSF matched coadd
* Produce the DIA sources using image differencing

This cookbook recipe has a few caveats:

* We are currently developing against the initial 40 visit Run 3 test dataset.  This means the values of some input variables may not be representative.  For example, the seeing in these first 40 images seems quite a bit worse than we expect on average.
* As written, this would duplicate steps in other cookbooks (e.g. `processEimage.py` in the L2 cookbook).  This is primarily because I found that I couldn't use the `calexp`s produced in the default way.  This probably means we'll want to switch to this new way of producing calibrated exposures.
* I have only processed the r band so far.  Doing the other bands may turn up further issues.

## Produce the `calexp`s

### Set up environment
```
$> export MYREPODIR=~/Twinkles/repos
$> export MYWORKDIR=~/Twinkles
$> export CALEXPDIR=$MYWORKDIR/fixed_psf_size
$> export COADDDIR=$MYWORKDIR/matched_coadd
$> export DIFFDIR=$MYWORKDIR/matched_diffim
$> export RAWDATADIR=/global/cscratch1/sd/desc/twinkles/work/4/input
$> export AND_DIR=/global/homes/d/desc/twinkles/trial/and_files_Phosim_Deep_Precursor
$> source /global/common/cori/contrib/lsst/lsstDM/setupStack-12_1.sh
$> cd $MYREPODIR
$> cd obs_lsstSim
$> git checkout twinkles_395
$> setup -j -m none -r $AND_DIR astrometry_net_data
$> cd $MYWORKDIR
```
### Make calibrated exposures
```
$> processEimage.py $RAWDATADIR --output $CALEXPDIR --id filter='r'
```
‼️ This task must be configured to have fixed size PSF measuremnt kernels or the PSF matching in the next step
doesn't work.  These configs are provided by the [`processEimage.py` config](https://github.com/lsst/obs_lsstSim/blob/twinkles_395/config/processEimage.py) in the [twinkles_395](https://github.com/lsst/obs_lsstSim/tree/twinkles_395) branch of the `obs_lsstSim` repository.</br>

> NB. PSFEX cannot be used as the PSF measurement algorithm in this task or the PSF matching will not work.

## Make the coadds
### Make the sky map
Input to the sky map maker should reflect all of the data to be coadded in the future.  This is typically done by specifying the `--id` flag with no argument.  The sky map should be generated once and used by all the bands.
```
$> makeDiscreteSkyMap.py $CALEXPDIR --id --output $COADDDIR
```
### Make the `CoaddTempExp`s
This requires a manual config step.  The seeing in the data varies from visit to visit.  For image differencing to work well in the current system, the template should have sharper seeing than the science images.  Thus, we choose a subset of the calibrated visit images to construct the coadd.  More data will give us higher signal to noise, but a wider coadd PSF.  Less data allows for a sharper coadd PSF, but lower signal to noise.  We have decided to parameterize this choice by allowing the maximum acceptable seeing in pixels, `select.maxPsfFwhm`, to be set at runtime.  The FWHM of the model Psf, `modelPsf.defaultFwhm`, also needs to be set, and must reflect this choice.  In concrete terms, `modelPsf.defaultFwhm` must be equal to or greater than `select.maxPsfFwhm`, and we recommend they be set to be equal to minimize loss to the broader coadd PSF.</br>
‼️ The config file must specify the same [size for the `modelPsf`](https://github.com/lsst/obs_lsstSim/blob/twinkles_395/config/makeCoaddTempExp.py#L6) as was specified for the Psf measurement kernel in the above step.
```
$> makeCoaddTempExp.py $CALEXPDIR --config modelPsf.defaultFwhm=4.85 select.maxPsfFwhm=4.85\
> --selectId filter='r' --id filter='r' --output $COADDDIR
```
> NB. You might think that it would be easy to determine the value of the `select.maxPsfFwhm` parameter in code, but the match PSF and the selection threshold must be known at the same time, at least, in the current task setup.  It would be possible to separate these two steps with a little more effort.

### Make the coadd
```
$> assembleCoadd.py $COADDDIR --selectId filter='r' --id filter='r' patch=0,0 tract=0 --output $COADDDIR
```
## Difference the images
```
#> imageDifference.py $COADDDIR --templateId patch='0,0' tract=0 filter='r' --id filter='r' --output $DIFFDIR
```
At this point you will have a diffim and the DIAsources.  Note that each of the images that went into the coadd will have significant
ringing in the diffim, because in these cases the template will be deconvolved in `ImageDifference.py` to match the science PSF.  The [config](https://github.com/lsst/obs_lsstSim/blob/twinkles_395/config/imageDifference.py) for the ImageDifferenceTask turns on decorrelation of the noise in the difference image.
