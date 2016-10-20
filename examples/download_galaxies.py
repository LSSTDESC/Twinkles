#!/usr/bin/env python
"""
This script downloads galaxies in a catsim instance catalog into a csv file.
The CatSim Instance Catalog uses a Twinkles 3 appropriate `ObservationMetaData`
and the `GalaxyTiled` dbObject to download properties of the galaxies. 

These are used in simulating the positions of SN.

To run this,
- Twinkles must be setup (only to get directory paths, and setup catsim)
- You must have a connection to fatboy

Note : script will not work as an executable on OSX from El Capitan onwards,
but can be used as `python scriptname`
"""
import os
import numpy as np
from lsst.utils import getPackageDir
from lsst.sims.catalogs.definitions import InstanceCatalog
from lsst.sims.catUtils.utils import ObservationMetaDataGenerator
import argparse

parser = argparse.ArgumentParser(description='Download the maximal Twinkles Instance Catalog for galaxies'
                                 'example :\n'
                                 'python download_galaxies --OpSimDBPath'
                                 '~/data/LSST/OpSimData/minion_1016_sqlite.db')
parser.add_argument('--OpSimDBPath', type=str,
                    help='absolute path to OpSim Database',
                    default='/Users/rbiswas/data/LSST/OpSimData/minion_1016_sqlite.db')
args = parser.parse_args()
opsimdbpath = args.OpSimDBPath


twinklesdir = getPackageDir('Twinkles')
obs_gen = ObservationMetaDataGenerator(database=opsimdbpath,
                                       driver='sqlite')

obsMetaDataList = obs_gen.getObservationMetaData(boundLength=0.3, fieldRA=(53., 54.), fieldDec=(-29., -27.), 
                                       limit=5)
print(obsMetaDataList[0].summary)
from lsst.sims.catUtils.baseCatalogModels import GalaxyTileObj

galdb = GalaxyTileObj()

class galCopy(InstanceCatalog):
    column_outputs = ['id', 'galtileid', 'raJ2000', 'decJ2000', 'redshift',
                      'a_d', 'b_d', 'pa_disk', 'sindexDisk','DiskHalfLightRadius',
                      'a_b', 'b_b', 'pa_bulge', 'sindexBulge', 'BulgeHalfLightRadius',
                      'mass_stellar', 'mass_gas', 'mass_halo', 'mass_bulge',
                      'sedFilenameDisk', 'sedFilenameBulge', 'log10BulgeToTotLSSTrFlux'
                      ]
    override_formats = {'raJ2000': '%8e', 'decJ2000': '%8e'}
gals = galCopy(db_obj=galdb, obs_metadata=obsMetaDataList[0])
galFile = os.path.join(twinklesdir, 'data', 'CatSimGals_radp3.csv')
gals.write_catalog(galFile)
