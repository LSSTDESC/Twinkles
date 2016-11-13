# How to create `DIASources` using PSF Homogenized coadds

This cookbook has a few caveats.
* This uses the initial 40 visit dataset produced by Tom and Tony.  This means the values may not be representative.  For example,
  the seeing in these images seems quite a bit worse than we expect on average.
* This will duplicate steps in other cookbooks (i.e. processEimage.py).  This is primarily because I found that I couldn't use
  the `calexp`s produced in the default way.
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
doesn't work.</br>
‼️ PSFEX cannot be used as the PSF measurement algorithm in this task or th PSF matching will not work.
## Make the coadds
### Make the sky map
This should reflect all of the data (`--id` flag with no argument), so should be generated once and used by all the bands.
```
$> makeDiscreteSkyMap.py $CALEXPDIR --id --output $COADDDIR
```
### Make the `CoaddTempExp`s
This requires a manual config step.  Specifically, the maximum acceptable seeing in pixels must be specified.  The FWHM of the model Psf
must reflect this choice.  This means that `modelPsf.defaultFwhm` must be equal to or greater than `select.maxPsfFwhm`.</br>
‼️ The config file must specify the same size for the `modelPsf` as was specified for the Psf measurement kernel in the
above step.
```
$> makeCoaddTempExp.py $CALEXPDIR --config modelPsf.defaultFwhm=4.85 select.maxPsfFwhm=4.85\
> --selectId filter='r' --id filter='r' --output $COADDDIR
```
### Make the coadd
```
$> assembleCoadd.py $COADDDIR --selectId filter='r' --id filter='r' patch=0,0 tract=0 --output $COADDDIR
```
## Difference the images
```
#> imageDifference.py $COADDDIR --templateId patch='0,0' tract=0 filter='r' --id filter='r' --output $DIFFDIR
```
At this point you will have a diffim and the DIAsources.  Note that any of the images that went into the coadd will have significant
ringing in the diffim because the template will be deconvolved to match the science PSF.
