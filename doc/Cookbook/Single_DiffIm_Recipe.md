# Recipe: Image Subtraction between Two Single-sensor Visit Images

This describes how to run the LSST Image Processing Stack program on two different Twinkles exposures. 

## Set up the LSST environment
The first step required is to set up the `lsst` stack on NERSC. While the general instructions for installing and setting up the LSST stack are [here](https://pipelines.lsst.io/install/index.html), for what we need here, we will have to specifically set up the DM stack on `Cori` thsi is best done by:
```
source /global/common/cori/contrib/lsst/lsstDM/setupStack-12_1-Run3.1.sh
```

The image differencing task is performed by the [`lsst/pipe_tasks/bin.src/imageDifference.py`](https://github.com/lsst/pipe_tasks/blob/master/bin.src/imageDifference.py) which, in turn, runs the [`ImageDiffferenceTask`](https://github.com/lsst/pipe_tasks/blob/master/python/lsst/pipe/tasks/imageDifference.py#L48). Generally speaking, this is a particular example of a `Pipe_Task` and therefore follows the syntax of the [`pipe-base` documentation](https://lsst-web.ncsa.illinois.edu/doxygen/x_masterDoxyDoc/pipe_base.html). In particular, the script takes as an argument the name of a data repository, obtained as the output of the previous stages of image processing. The data repository on `Cori` is
```
REPO=/global/cscratch1/sd/desc/twinkles/work/4/output
```
The kwargs that are essential are the ID of the science image (usually chosen to be the image with the larger PSF), and the chosen template image. For the image differencing task, the ID should be indicate both the visit ID (`obsHistID`), and the `ccd`, and the `filter`, split by space.
```
--id visit=230 ccd=1,2
```
If only the `visit` ID is provided, this will result in picking all the exposures in the data repository that satisfy the conditions. However, for Twinkles, we are only simulating a single chip, so `visit` (specified as an integer) is a complete specification of an exposure. Similarly, the template ID must be specified:
```
--templateId visit=250
```
We need to specify an output directory through the kwargs  `-output OUTPUTREPO` and a configfile through
the kwargs `--configfile diffimconfig.py`.  The [`diffimconfig.py`](configScripts/diffimconfig.py) is in the Cookbook folder in the Twinkles git repo. The complete command is:

```
imageDifference.py ${REPO} --id visit=${SCIENCE_IMAGE} --templateId visit=${TEMPLATE_IMAGE} --output ${OUTREPO} --configfile ${TWINKLES_DIR}/doc/Cookbook/configScripts/diffimconfig.py
```

 

