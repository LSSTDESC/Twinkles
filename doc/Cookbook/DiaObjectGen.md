### In order to use this cookbook, you will need the `twinkles_#435` branch of `obs_lsstSim`.
First, set up a recent stack.
```bash
git clone https://github.com/lsst/obs_lsstSim
cd obs_lsstSim
git checkout twinkles_#435
setup -k -r .
scons
```

## Get the reference catalog
[Twinkles](https://lsst-web.ncsa.illinois.edu/~krughoff/data/twinkles_reference_catalog.txt)<br>
[DC1](https://lsst-web.ncsa.illinois.edu/~krughoff/data/dc1_reference_catalog.txt)

## Setup -- Define a few environment variables to make thes instructions more portable
```bash
export INPUT_REPO=input_data
export OUTPUT_REPO=output_data
export RAW_PATH=raw_data
export PATH_TO_REF=.

```

## Make your repo (if you don't have one)
```bash
mkdir $INPUT_REPO
echo "lsst.obs.lsstSim.LsstSimMapper" > $INPUT_REPO/_mapper
ingestImages.py $INPUT_REPO/ $RAW_PATH/*.fits.gz
```

## Ingest reference catalog
```
ingestReferenceCatalog.py $INPUT_REPO $PATH_TO_REF/twinkles_reference_catalog.txt --configfile $OBS_LSSTSIM_DIR/config/DC1_IngestRefConfig.py --output $INPUT_REPO
```
> Note that to use the new style reference catalogs, you'll need some config overrides of anything that uses a `refObjLoader`.  See
> [this config](https://github.com/lsst/obs_lsstSim/blob/twinkles_%23435/config/processEimage.py#L1) for examples.  There is no need to implement any overrides if you are following this cookbook.  All overrides are applied in the relevant config override file mentioned in the command.

## Common operations for both L2 and L1 type processing
```bash
processEimage.py $INPUT_REPO --id --output $OUTPUT_REPO
```

## Level 2 processing steps
```bash
makeDiscreteSkyMap.py $OUTPUT_REPO --id --output $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/makeDiscreteSkyMap_deep.py
# The coadd steps *must* be done one band at a time.
makeCoaddTempExp.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/makeCoaddTempExp_deep.py --selectId filter=u --id filter=u --output $OUTPUT_REPO
makeCoaddTempExp.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/makeCoaddTempExp_deep.py --selectId filter=g --id filter=g --output $OUTPUT_REPO
makeCoaddTempExp.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/makeCoaddTempExp_deep.py --selectId filter=r --id filter=r --output $OUTPUT_REPO
makeCoaddTempExp.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/makeCoaddTempExp_deep.py --selectId filter=i --id filter=i --output $OUTPUT_REPO
makeCoaddTempExp.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/makeCoaddTempExp_deep.py --selectId filter=z --id filter=z --output $OUTPUT_REPO
makeCoaddTempExp.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/makeCoaddTempExp_deep.py --selectId filter=y --id filter=y --output $OUTPUT_REPO
assembleCoadd.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/assembleCoadd_deep.py --selectId filter=u --id filter=u patch=0,0 tract=0 --output $OUTPUT_REPO
assembleCoadd.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/assembleCoadd_deep.py --selectId filter=g --id filter=g patch=0,0 tract=0 --output $OUTPUT_REPO
assembleCoadd.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/assembleCoadd_deep.py --selectId filter=r --id filter=r patch=0,0 tract=0 --output $OUTPUT_REPO
assembleCoadd.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/assembleCoadd_deep.py --selectId filter=i --id filter=i patch=0,0 tract=0 --output $OUTPUT_REPO
assembleCoadd.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/assembleCoadd_deep.py --selectId filter=z --id filter=z patch=0,0 tract=0 --output $OUTPUT_REPO
assembleCoadd.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/assembleCoadd_deep.py --selectId filter=y --id filter=y patch=0,0 tract=0 --output $OUTPUT_REPO
# Detection and measurement can be done per band or all bands in one go (will be done serially if the latter)
# Merge steps *must* be done on all the bands to me merged at once.
detectCoaddSources.py $OUTPUT_REPO --id tract=0 patch=0,0 filter=u^g^r^i^z^y --output $OUTPUT_REPO
mergeCoaddDetections.py $OUTPUT_REPO --id tract=0 patch=0,0 filter=u^g^r^i^z^y--output $OUTPUT_REPO
measureCoaddSources.py $OUTPUT_REPO --id tract=0 patch=0,0 filter=u^g^r^i^z^y --output $OUTPUT_REPO
mergeCoaddMeasurements.py $OUTPUT_REPO --id tract=0 patch=0,0 filter=u^g^r^i^z^y --output $OUTPUT_REPO
forcedPhotCcd.py $OUTPUT_REPO --id tract=0 --output $OUTPUT_REPO
```

## Level 1 processing steps
```bash
makeDiscreteSkyMap.py $OUTPUT_REPO --id --output $OUTPUT_REPO --config $OBS_LSSTSIM_DIR/config/makeDiscreteSkyMap_goodSeeing.py
makeCoaddTempExp.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/makeCoaddTempExp_goodSeeing.py --config modelPsf.defaultFwhm=3.0 select.minPsfFwhm=2.6 select.maxPsfFwhm=3.0 --selectId filter='r' --id filter='r' --output $OUTPUT_REPO #per band
assembleCoadd.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/assembleCoadd_goodSeeing.py --selectId filter='r' --id filter='r' patch=0,0 tract=0 --output $OUTPUT_REPO #per band
imageDifference.py $OUTPUT_REPO --templateId filter='r' --id filter='r' --output $OUTPUT_REPO #per band
diaObjectMaker.py $OUTPUT_REPO --id --output $OUTPUT_REPO
```
