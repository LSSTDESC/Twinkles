# -*- coding: utf-8 -*-
"""
Script to generate phoSim input catalog that has sprinkled lens systems inside.
It is also setup to run visits from a selected set in kraken_1042.
To use:
    - need Om10 setup
    - sims stack setup, currently sims_catUtils must be a branch
     https://github.com/lsst/sims_catUtils/tree/newTwinklesCatalog and at
     commit  e203093  or after
    - Have the kraken_1042 sqlite db symlinked to this directory.

    You can modify the slicing to choose which visits to simulate
"""

from __future__ import with_statement, absolute_import, division, print_function
import sys
import os
import time
import numpy
from lsst.sims.catalogs.definitions import InstanceCatalog, CompoundInstanceCatalog
from lsst.sims.utils import ObservationMetaData
from lsst.sims.catUtils.utils import ObservationMetaDataGenerator
from lsst.sims.catalogs.db import CatalogDBObject
from lsst.sims.catalogs.db.dbConnection import DBConnection
from lsst.sims.catUtils.baseCatalogModels import OpSim3_61DBObject, StarObj, MsStarObj, \
        BhbStarObj, WdStarObj, RRLyStarObj, CepheidStarObj, GalaxyBulgeObj, GalaxyDiskObj, \
        GalaxyAgnObj, SNDBObj
from lsst.sims.catUtils.mixins import FrozenSNCat
from lsst.sims.catUtils.exampleCatalogDefinitions.phoSimCatalogExamples import \
        PhoSimCatalogPoint, PhoSimCatalogSersic2D, PhoSimCatalogSN, \
        DefaultPhoSimHeaderMap
from sprinkler import sprinklerCompound
from twinklesCatalogDefs import TwinklesCatalogZPoint


def generatePhosimInput(mode='a', runobsHistID=None):

    if mode == 'a':
        filewrite = 'append'
    elif mode == 'c':
        filewrite = 'clobber'

    opsimDB = os.path.join('.','kraken_1042_sqlite.db')


    logfilename = 'run.log'
    if os.path.isfile(logfilename):
        if filewrite =='append':
            pass
        elif filewrite == 'clobber':
            with open('run.log', 'w') as f:
                f.write('obsHistID,status,timestamp\n')
        else:
            print('file exists and mode uncertain')
            exit()
    else:
        with open('run.log', 'w') as f:
            f.write('obsHistID,status,time\n')


    #you need to provide ObservationMetaDataGenerator with the connection
    #string to an OpSim output database.  This is the connection string
    #to a test database that comes when you install CatSim.
    generator = ObservationMetaDataGenerator(database=opsimDB, driver='sqlite')
    obsHistIDList = numpy.genfromtxt('../../../data/SelectedKrakenVisits.csv', delimiter=',', usecols=0)
    obsMetaDataResults = []
    # Change the slicing in this line for the range of visits
    use_obsHistID_list = []
    for obsHistID in obsHistIDList[600:602]:
        if runobsHistID is not None:
            obsHistID = runobsHistID
        obsMetaDataResults.append(generator.getObservationMetaData(obsHistID=obsHistID,
                                  fieldRA=(53, 54), fieldDec=(-29, -27),
                                  boundLength=0.03)[0])
        use_obsHistID_list.append(obsHistID)

    starObjNames = ['msstars', 'bhbstars', 'wdstars', 'rrlystars', 'cepheidstars']

    snmodel = SNDBObj(table='twinkSN')
    for obs_metadata, obs_id in zip(obsMetaDataResults, use_obsHistID_list):
        filename = "InstanceCatalogs/phosim_input_%s.txt" \
                   %(obs_id)
                   #%(obs_metadata.phoSimMetaData['Opsim_obshistid'][0])

        phosim_header_map = DefaultPhoSimHeaderMap
        phosim_header_map['nsnap'] = (1, numpy.dtype(int))
        phosim_header_map['vistime'] = (30, numpy.dtype(int))
        #obs_metadata.phoSimMetaData['SIM_NSNAP'] = (1, numpy.dtype(int))
        #obs_metadata.phoSimMetaData['SIM_VISTIME'] = (30, numpy.dtype(float))
        print('Starting Visit: ', obs_id)

        compoundStarDBList = [MsStarObj, BhbStarObj, WdStarObj, RRLyStarObj,
                              CepheidStarObj]
        compoundGalDBList = [GalaxyBulgeObj, GalaxyDiskObj, GalaxyAgnObj]
        compoundStarICList = [PhoSimCatalogPoint, PhoSimCatalogPoint,
                              PhoSimCatalogPoint, PhoSimCatalogPoint,
                              PhoSimCatalogPoint]
        compoundGalICList = [PhoSimCatalogSersic2D, PhoSimCatalogSersic2D,
                             TwinklesCatalogZPoint]

        snphosim = PhoSimCatalogSN(db_obj=snmodel,
                                   obs_metadata=obs_metadata,
                                   column_outputs=['EBV'])
        snphosim.phoSimHeaderMap = phosim_header_map
        snphosim.writeSedFile = True
        snphosim.suppressDimSN = True
        snphosim.prefix = 'spectra_files/'
        while True:
            try:
                starCat = CompoundInstanceCatalog(compoundStarICList,
                                                  compoundStarDBList,
                                                  obs_metadata=obs_metadata,
                                                  constraint='gmag > 11.',
                                                  compoundDBclass=sprinklerCompound)
                starCat.phoSimHeaderMap = phosim_header_map
                starCat.write_catalog(filename, chunk_size=100)
                galCat = CompoundInstanceCatalog(compoundGalICList,
                                                 compoundGalDBList,
                                                 obs_metadata=obs_metadata,
                                                 # constraint='g_ab > 11.',
                                                 compoundDBclass=sprinklerCompound)
                galCat.phoSimHeaderMap = phosim_header_map
                galCat.write_catalog(filename, write_mode='a',
                                     write_header=False, chunk_size=10000)

                snphosim.write_catalog(filename, write_header=False,
                                       write_mode='a', chunk_size=10000)

                if runobsHistID is not None:
                    print('Done doing requested obsHistID')
                    sys.exit()
                with open(logfilename, 'a') as f:
                    f.write('{0:d},DONE,{1:3.6f}\n'.format(obs_metadata.phoSimMetaData['Opsim_obshistid'][0], time.time()))
                break
            except RuntimeError:
                continue

        print("Finished Writing Visit: ", obs_metadata.phoSimMetaData['Opsim_obshistid'][0])

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        mode = str(sys.argv[1])
    else:
        mode = 'a'
    generatePhosimInput(mode, runobsHistID=220)
