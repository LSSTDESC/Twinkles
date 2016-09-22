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
import numpy as np
from lsst.sims.catalogs.definitions import CompoundInstanceCatalog
from lsst.sims.catUtils.utils import ObservationMetaDataGenerator
from lsst.sims.catUtils.baseCatalogModels import (StarObj, CepheidStarObj,
                                                  GalaxyBulgeObj, GalaxyDiskObj,
                                                  GalaxyAgnObj, SNDBObj)
# from lsst.sims.catUtils.mixins import FrozenSNCat
from lsst.sims.catUtils.exampleCatalogDefinitions.phoSimCatalogExamples import \
        PhoSimCatalogPoint, PhoSimCatalogSersic2D, PhoSimCatalogSN, \
        DefaultPhoSimHeaderMap
from sprinkler import sprinklerCompound
from twinklesCatalogDefs import TwinklesCatalogZPoint

PhoSimHeaderMap = {'rottelpos': ('rotTelPos', np.degrees),
                   'obshistid': ('obsHistID', None),
                   'moonra': ('moonRA', np.degrees),
                   'moondec': ('moonDec', np.degrees),
                   'moonphase': ('moonPhase', None),
                   'moonalt': ('moonAlt', np.degrees),
                   'dist2moon': ('dist2Moon', np.degrees),
                   'sunalt': ('sunAlt', np.degrees),
                   'seeing': ('rawSeeing', None),
                   'vistime': 30.0,
                   'nsnap': 1,
                   'seed': ('obsHistID', None)}

def generatePhosimInput(mode='a', obsHistIdList=None, opsimDB='kraken_1042_sqlite.db'):
    """
    Create PhoSim InstanceCatalogs of galaxies, stars, supernovae, and lensed
    quasars.  These catalogs are based on OpSim pointings of a specified
    ObsHistID.

    Parameters
    ----------
    mode is a string indicating the mode in which to write the log information
    about this catalog-generation run.  'a' means 'append'; 'c' means 'clobber'.

    obsHistIdList is a list of obshistids for which to generate catalogs

    opsimDB is the path to the OpSim database from which pointings will be
    drawn.
    """

    if opsimDB is None:
        raise RuntimeError("Must specify an opsimDB")

    if not os.path.exists(opsimDB):
        raise RuntimeError("The opsimDB you specified does not exist")

    if obsHistIdList is None:
        raise RuntimeError("Must specify and obsHistIdList")

    if mode == 'a':
        filewrite = 'append'
    elif mode == 'c':
        filewrite = 'clobber'

    logfilename = 'run.log'
    if os.path.isfile(logfilename):
        if filewrite =='append':
            pass
        elif filewrite == 'clobber':
            with open('run.log', 'w') as f:
                f.write('obsHistID, status, timestamp\n')
        else:
            print('file exists and mode uncertain')
            exit()
    else:
        with open('run.log', 'w') as f:
            f.write('obsHistID, status, time\n')

    #you need to provide ObservationMetaDataGenerator with the connection
    #string to an OpSim output database.  This is the connection string
    #to a test database that comes when you install CatSim.
    print('connecting to ',opsimDB)
    generator = ObservationMetaDataGenerator(database=opsimDB, driver='sqlite')

    obsMetaDataResults = []

    for obsHistID in obsHistIdList:

        obsMetaDataResults.append(generator.getObservationMetaData(obsHistID=obsHistID,
                                  fieldRA=(53, 54), fieldDec=(-29, -27),
                                  boundLength=0.3)[0])
        use_obsHistID_list.append(obsHistID)

    snmodel = SNDBObj(table='twinkSN')
    available_connections = [snmodel.connection] # store a list of open connections to fatboy

    for obs_metadata in obsMetaDataResults:
        filename = os.path.join("InstanceCatalogs",
                                "phosim_input_%s.txt" % (obs_metadata.OpsimMetaData['obsHistID']))
        print('Starting Visit: ',
              obs_metadata.OpsimMetaData['obsHistID'])

        compoundStarDBList = [StarObj, CepheidStarObj]
        compoundGalDBList = [GalaxyBulgeObj, GalaxyDiskObj, GalaxyAgnObj]

        compoundStarICList = [PhoSimCatalogPoint, PhoSimCatalogPoint]
        compoundGalICList = [PhoSimCatalogSersic2D, PhoSimCatalogSersic2D,
                             TwinklesCatalogZPoint]

        snphosim = PhoSimCatalogSN(db_obj=snmodel,
                                   obs_metadata=obs_metadata)

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

                starCat._active_connections += available_connections # append already open fatboy connections

                starCat.phoSimHeaderMap = PhoSimHeaderMap

                print("writing starCat ")
                starCat.write_catalog(filename, chunk_size=10000)

                galCat = CompoundInstanceCatalog(compoundGalICList,
                                                 compoundGalDBList,
                                                 obs_metadata=obs_metadata,
                                                 # constraint='g_ab > 11.',
                                                 compoundDBclass=sprinklerCompound)

                galCat._active_connections = starCat._active_connections # pass along already open fatboy connections

                print("writing galCat")

                galCat.write_catalog(filename, write_mode='a',
                                     write_header=False)#, chunk_size=10000)

                print("writing sne")
                snphosim.write_catalog(filename, write_header=False,
                                       write_mode='a')#, chunk_size=10000)

                available_connections = galCat._active_connections # store the list of open fatboy connections

                with open(logfilename, 'a') as f:
                    f.write('{0:d},DONE,{1:3.6f}\n'.format(obs_metadata.OpsimMetaData['obsHistID'], time.time()))
                break
            except RuntimeError:
                continue

        print("Finished Writing Visit: ", obs_metadata.OpsimMetaData['obsHistID'])

if __name__ == "__main__":
    import sys

    opsimdb = sys.argv[1]
    if len(sys.argv) > 2:
        mode = str(sys.argv[1])
    else:
        mode = 'a'

    generatePhosimInput(mode, obsHistIdList=[220], opsimDB=opsimdb)
