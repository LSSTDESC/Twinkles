# -*- coding: utf-8 -*-
"""
Generate phoSim input catalog that has sprinkled lens systems inside.
"""

from __future__ import with_statement
import os
import numpy
from lsst.sims.catalogs.measures.instance import InstanceCatalog, CompoundInstanceCatalog
from lsst.sims.utils import ObservationMetaData
from lsst.sims.catUtils.utils import ObservationMetaDataGenerator
from lsst.sims.catalogs.generation.db import CatalogDBObject
from lsst.sims.catalogs.generation.db.dbConnection import DBConnection
from lsst.sims.catUtils.baseCatalogModels import OpSim3_61DBObject, StarObj, MsStarObj, \
        BhbStarObj, WdStarObj, RRLyStarObj, CepheidStarObj, GalaxyBulgeObj, GalaxyDiskObj, \
        GalaxyAgnObj, SNObj
from lsst.sims.catUtils.mixins import FrozenSNCat
from lsst.sims.catUtils.exampleCatalogDefinitions.phoSimCatalogExamples import \
        PhoSimCatalogPoint, PhoSimCatalogSersic2D, PhoSimCatalogSN
from sprinkler import sprinklerCompound
from twinklesCatalogDefs import TwinklesCatalogZPoint

def generatePhosimInput():

    opsimDB = os.path.join('.','kraken_1042_sqlite.db')

    #you need to provide ObservationMetaDataGenerator with the connection
    #string to an OpSim output database.  This is the connection string
    #to a test database that comes when you install CatSim.
    generator = ObservationMetaDataGenerator(database=opsimDB, driver='sqlite')
    obsHistIDList = numpy.genfromtxt('FirstSet_obsHistIDs.csv', delimiter=',', usecols=0)
    obsMetaDataResults = []
    for obsHistID in obsHistIDList[:5]:
        obsMetaDataResults.append(generator.getObservationMetaData(obsHistID=obsHistID,
                                  fieldRA=(53, 54), fieldDec=(-29, -27),
                                  boundLength=0.03)[0])

    starObjNames = ['msstars', 'bhbstars', 'wdstars', 'rrlystars', 'cepheidstars']

    snmodel = SNObj()
    for obs_metadata in obsMetaDataResults:
        filename = "phosim_input_%s.txt"%(obs_metadata.phoSimMetaData['Opsim_obshistid'][0])
        obs_metadata.phoSimMetaData['SIM_NSNAP'] = (1, numpy.dtype(int))
        obs_metadata.phoSimMetaData['SIM_VISTIME'] = (30, numpy.dtype(float))
        print 'Starting Visit: ', obs_metadata.phoSimMetaData['Opsim_obshistid'][0]

        compoundStarDBList = [MsStarObj, BhbStarObj, WdStarObj, RRLyStarObj, CepheidStarObj]
        compoundGalDBList = [GalaxyBulgeObj, GalaxyDiskObj, GalaxyAgnObj]
        compoundStarICList = [PhoSimCatalogPoint, PhoSimCatalogPoint,
                              PhoSimCatalogPoint, PhoSimCatalogPoint,
                              PhoSimCatalogPoint]
        compoundGalICList =  [PhoSimCatalogSersic2D, PhoSimCatalogSersic2D,
                              TwinklesCatalogZPoint]

        snphosim = PhoSimCatalogSN(db_obj=snmodel,
                                   obs_metadata=obs_metadata,
                                   column_outputs=['EBV'])
        snphosim.writeSedFile = True
        snphosim.suppressDimSN = True
        snphosim.prefix = 'spectra_files/'
        while True:
            try:
                starCat = CompoundInstanceCatalog(compoundStarICList,
                                                   compoundStarDBList,
                                                   obs_metadata=obs_metadata,
                                                   constraint='rmag > 16.',
                                                   compoundDBclass=sprinklerCompound)
                starCat.write_catalog(filename)
                galCat = CompoundInstanceCatalog(compoundGalICList,
                                                   compoundGalDBList,
                                                   obs_metadata=obs_metadata,
                                                   compoundDBclass=sprinklerCompound)
                galCat.write_catalog(filename, write_mode='a',
                                     write_header=False)

                snphosim.write_catalog(filename, write_header=False,
                                       write_mode='a')
                break
            except RuntimeError:
                continue

        print "Finished Writing Visit: ", obs_metadata.phoSimMetaData['Opsim_obshistid'][0]

if __name__ == "__main__":
    generatePhosimInput()
