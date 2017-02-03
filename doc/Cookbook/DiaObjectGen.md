## This assumes `twinkles_#435` of `obs_lsstSim`

# Get the reference catalog
[Twinkles](https://lsst-web.ncsa.illinois.edu/~krughoff/data/twinkles_reference_catalog.txt)
[DC1](https://lsst-web.ncsa.illinois.edu/~krughoff/data/dc1_reference_catalog.txt)

# Make your repo (if you don't have one)
```
mkdir $INPUT_REPO
echo "lsst.obs.lsstSim.LsstSimMapper" > $INPUT_REPO/_mapper
ingestImages.py $INPUT_REPO/ $RAW_PATH/*.fits.gz
```

# Ingest reference catalog
```
ingestReferenceCatalog.py $INPUT_REPO $PATH_TO_REF/twinkles_reference_catalog.txt --configfile $OBS_LSSTSIM_DIR/config/DC1_IngestRefConfig.py --output $INPUT_REPO
```
Note that to use the new style reference catalogs, you'll need some config overrides of anything that uses a `refObjLoader`.  See
[this config](https://github.com/lsst/obs_lsstSim/blob/twinkles_%23435/config/processEimage.py#L1) for examples.

processEimage.py DC1_input_data/ --id filter=r --output DC1_output_data
makeDiscreteSkyMap.py DC1_output_data/ --id --output DC1_output_data --config $OBS_LSSTSIM_DIR/config/makeDiscreteSkyMap_deep.py
makeDiscreteSkyMap.py DC1_output_data/ --id --output DC1_output_data --config $OBS_LSSTSIM_DIR/config/makeDiscreteSkyMap_goodSeeing.py
makeCoaddTempExp.py DC1_input_data/ --configfile $OBS_LSSTSIM_DIR/config/makeCoaddTempExp_goodSeeing.py --config modelPsf.defaultFwhm=3.0 select.minPsfFwhm=2.6 select.maxPsfFwhm=3.0 --selectId filter='r' --id filter='r' --output DC1_output_data/
makeCoaddTempExp.py DC1_input_data/ --configfile $OBS_LSSTSIM_DIR/config/makeCoaddTempExp_deep.py --selectId filter='r' --id filter='r' --output DC1_output_data/
assembleCoadd.py DC1_output_data/ --configfile /Volumes/Files/repos/obs_lsstSim_2/config/assembleCoadd_goodSeeing.py --selectId filter='r' --id filter='r' patch=0,0 tract=0 --output DC1_output_data/
assembleCoadd.py DC1_output_data/ --configfile /Volumes/Files/repos/obs_lsstSim_2/config/assembleCoadd_deep.py --selectId filter='r' --id filter='r' patch=0,0 tract=0 --output DC1_output_data/
imageDifference.py DC1_output_data/ --templateId filter='r' --id filter='r' --output DC1_diffim
detectCoaddSources.py DC1_output_data/ --id tract=0 patch=0,0 filter=r --output DC1_output_data
mergeCoaddDetections.py DC1_output_data/ --id tract=0 patch=0,0 filter=r --output DC1_output_data/
measureCoaddSources.py DC1_output_data/ --id tract=0 patch=0,0 filter=r --output DC1_output_data/
mergeCoaddMeasurements.py DC1_output_data --id tract=0 patch=0,0 filter='r' --output DC1_output_data
forcedPhotCcd.py DC1_output_data/ --id tract=0  --output DC1_output_forced
