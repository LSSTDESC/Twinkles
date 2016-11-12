# Image Subtraction between two single frame Exposures

This describes how to run the LSST Image Processing Stack program on two different Twinkles exposures. The first step required is to setup the `lsst` stack on NERSC or a computer where the data can be accessed. For details on how to setup packages in the `lsst` stack, please go to [page](here). For what we need, we will have to set up the DM stack and the twinkles stack
```
setup lsst_apps
setup twinkles
```
The task is performed by the [`lsst/pipe_tasks/bin.src/imageDifference.py`](https://github.com/lsst/pipe_tasks/blob/master/bin.src/imageDifference.py) which, in turn, runs the [`ImageDiffferenceTask`](https://github.com/lsst/pipe_tasks/blob/master/python/lsst/pipe/tasks/imageDifference.py#L48). Generally speaking, this is a particular example of a `Pipe_Task` and therefore follows the syntax of the [`pipe-base` documentation](https://lsst-web.ncsa.illinois.edu/doxygen/x_masterDoxyDoc/pipe_base.html). In particular, the script takes a positional argument which is a data repository obtained as the output of the previous stages of image processing. The data repository on `Cori` is
`
REPO=/global/cscratch1/sd/desc/twinkles/work/4/output
`
The kwargs that are essential are the id of the science image (usually chosen to be the image with the larger  PSF) and the chosen template image. For the image differencing task, the id should be indicate both the visit id (obsHistID), and the ccd, and the filter, split by space.
`
--id visit=230 ccd=1,2
`
If only the `visit` id is provided, this will result in picking all the exposures in the data repository that satisfy the conditions, and do (an outer product?). However, for Twinkles, we only have a single ccd, so `visit` (specified as an integer) is a complete specification of an exposure. Similarly, the template id must be specified
`
--templateId visit=250
`
We need to specify an output directory through the kwargs  `-output OUTPUTREPO` and a configfile through
the kwargs `--configfile diffimconfig.py`.  The file [`diffimconfig.py`](configScripts/diffimconfig.py)
 
```
imageDifference.py ${REPO} --id visit=${SCIENCE_IMAGE} --templateId visit=${TEMPLATE_IMAGE} --output ${OUTREPO} --configfile ${TWINKLES_DIR}/doc/Cookbook/configScripts/diffimconfig.py
```

 

