## Process all images
```bash
processEimage.py $INPUT_REPO --id --output $OUTPUT_REPO
```
## Make the coadd for a particular year
This will require feeding this part just the visits in the time window you want to end up in the coadd.
```bash
makeDiscreteSkyMap.py $OUTPUT_REPO --id --output $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/makeDiscreteSkyMap_goodSeeing.py
makeCoaddTempExp.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/makeCoaddTempExp_goodSeeing.py --config modelPsf.defaultFwhm=3.0 select.minPsfFwhm=2.6 select.maxPsfFwhm=3.0 --selectId filter=u --id filter=u --output $OUTPUT_REPO
makeCoaddTempExp.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/makeCoaddTempExp_goodSeeing.py --config modelPsf.defaultFwhm=3.0 select.minPsfFwhm=2.6 select.maxPsfFwhm=3.0 --selectId filter=g --id filter=g --output $OUTPUT_REPO
makeCoaddTempExp.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/makeCoaddTempExp_goodSeeing.py --config modelPsf.defaultFwhm=3.0 select.minPsfFwhm=2.6 select.maxPsfFwhm=3.0 --selectId filter=r --id filter=r --output $OUTPUT_REPO
makeCoaddTempExp.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/makeCoaddTempExp_goodSeeing.py --config modelPsf.defaultFwhm=3.0 select.minPsfFwhm=2.6 select.maxPsfFwhm=3.0 --selectId filter=i --id filter=i --output $OUTPUT_REPO
makeCoaddTempExp.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/makeCoaddTempExp_goodSeeing.py --config modelPsf.defaultFwhm=3.0 select.minPsfFwhm=2.6 select.maxPsfFwhm=3.0 --selectId filter=z --id filter=z --output $OUTPUT_REPO
makeCoaddTempExp.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/makeCoaddTempExp_goodSeeing.py --config modelPsf.defaultFwhm=3.0 select.minPsfFwhm=2.6 select.maxPsfFwhm=3.0 --selectId filter=y --id filter=y --output $OUTPUT_REPO
assembleCoadd.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/assembleCoadd_goodSeeing.py --selectId filter=u --id filter=u patch=0,0 tract=0 --output $OUTPUT_REPO
assembleCoadd.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/assembleCoadd_goodSeeing.py --selectId filter=g --id filter=g patch=0,0 tract=0 --output $OUTPUT_REPO
assembleCoadd.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/assembleCoadd_goodSeeing.py --selectId filter=r --id filter=r patch=0,0 tract=0 --output $OUTPUT_REPO
assembleCoadd.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/assembleCoadd_goodSeeing.py --selectId filter=i --id filter=i patch=0,0 tract=0 --output $OUTPUT_REPO
assembleCoadd.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/assembleCoadd_goodSeeing.py --selectId filter=z --id filter=z patch=0,0 tract=0 --output $OUTPUT_REPO
assembleCoadd.py $OUTPUT_REPO --configfile $OBS_LSSTSIM_DIR/config/assembleCoadd_goodSeeing.py --selectId filter=y --id filter=y patch=0,0 tract=0 --output $OUTPUT_REPO
```
## difference
This will require feeding just the visits you want to difference (i.e. the next year's visits)
```bash
imageDifference.py $OUTPUT_REPO --templateId filter=u --id filter=u --output $OUTPUT_REPO
imageDifference.py $OUTPUT_REPO --templateId filter=g --id filter=g --output $OUTPUT_REPO
imageDifference.py $OUTPUT_REPO --templateId filter=r --id filter=r --output $OUTPUT_REPO
imageDifference.py $OUTPUT_REPO --templateId filter=i --id filter=i --output $OUTPUT_REPO
imageDifference.py $OUTPUT_REPO --templateId filter=z --id filter=z --output $OUTPUT_REPO
imageDifference.py $OUTPUT_REPO --templateId filter=y --id filter=y --output $OUTPUT_REPO
# This will aggregate across all bands.  We should restrict the dia objects to include just dia sources from images not included in the coadd.  I'm not sure practically how that works.
diaObjectMaker.py $OUTPUT_REPO --id --output $OUTPUT_REPO
```

This will not work for the case where you want to difference against multiple coadds.  That would require one `$OUTPUT_REPO` per yearly coadd.
