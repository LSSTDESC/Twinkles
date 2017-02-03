### This assumes `twinkles_#435` of `obs_lsstSim`

## Get the reference catalog
[Twinkles](https://lsst-web.ncsa.illinois.edu/~krughoff/data/twinkles_reference_catalog.txt)<br>
[DC1](https://lsst-web.ncsa.illinois.edu/~krughoff/data/dc1_reference_catalog.txt)

## Setup -- Define a few environment variables to make thes instructions more portable
```bash
export INPUT_REPO = input_data
export OUTPUT_REPO = output_data
export RAW_PATH = raw_data
export PATH_TO_REF = .

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
> [this config](https://github.com/lsst/obs_lsstSim/blob/twinkles_%23435/config/processEimage.py#L1) for examples.

## Common operations for both L2 and L1 type processing
```bash
processEimage.py $INPUT_REPO --id --output $OUTPUT_REPO
```

## Level 2 processing steps
```bash
makeDiscreteSkyMap.py $OUTPUT_REPO --id --output $OUTPUT_REPO --config $OBS_LSSTSIM_DIR/config/makeDiscreteSkyMap_deep.py
makeCoaddTempExp.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/makeCoaddTempExp_deep.py --selectId --id --output $OUTPUT_REPO
assembleCoadd.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/assembleCoadd_deep.py --selectId filter='r' --id filter='r' patch=0,0 tract=0 --output $OUTPUT_REPO #per band
detectCoaddSources.py $OUTPUT_REPO --id tract=0 patch=0,0 filter=r --output $OUTPUT_REPO #per band
mergeCoaddDetections.py $OUTPUT_REPO --id tract=0 patch=0,0 --output $OUTPUT_REPO
measureCoaddSources.py $OUTPUT_REPO --id tract=0 patch=0,0 filter=r --output $OUTPUT_REPO #per band
mergeCoaddMeasurements.py $OUTPUT_REPO --id tract=0 patch=0,0 --output $OUTPUT_REPO
forcedPhotCcd.py $OUTPUT_REPO --id tract=0  --output $OUTPUT_REPO
```

## Level 1 processing steps
```bash
makeDiscreteSkyMap.py $OUTPUT_REPO --id --output $OUTPUT_REPO --config $OBS_LSSTSIM_DIR/config/makeDiscreteSkyMap_goodSeeing.py
makeCoaddTempExp.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/makeCoaddTempExp_goodSeeing.py --config modelPsf.defaultFwhm=3.0 select.minPsfFwhm=2.6 select.maxPsfFwhm=3.0 --selectId filter='r' --id filter='r' --output $OUTPUT_REPO #per band
assembleCoadd.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/assembleCoadd_goodSeeing.py --selectId filter='r' --id filter='r' patch=0,0 tract=0 --output $OUTPUT_REPO #per band
imageDifference.py $OUTPUT_REPO --templateId filter='r' --id filter='r' --output $OUTPUT_REPO #per band
diaObjectMaker.py $OUTPUT_REPO --id --output $OUTPUT_REPO
```
